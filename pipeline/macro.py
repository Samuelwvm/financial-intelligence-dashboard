"""Indicadores derivados para as telas Mundo e Brasil (macro.json).

- Juro real Brasil × EUA (ex-post): taxa nominal no fim do mês descontada da inflação
  dos 12 meses até aquele mês, pela fórmula de Fisher: (1 + juro) / (1 + inflação) − 1.
    Brasil: SELIC meta (BCB 432) e IPCA 12 meses (BCB 13522).
    EUA:    EFFR (New York Fed) e CPI-U 12 meses (BLS), só quando os dois meses existem.
- Inflação × meta: IPCA 12 meses contra a meta contínua do CMN.
Nada é projetado: tudo é inflação já medida e taxa já praticada.
"""

from __future__ import annotations

import bisect
import calendar
import sqlite3
from datetime import date

from . import db, us

MONTHS = 24

# Meta de inflação definida pelo Conselho Monetário Nacional (CMN): 3,0% ao ano,
# com intervalo de tolerância de 1,5 ponto para mais ou para menos (meta contínua).
INFLATION_TARGET = {"center": 3.0, "lower": 1.5, "upper": 4.5, "source": "CMN (Conselho Monetário Nacional)"}

Series = list[tuple[str, float]]


def fisher(nominal: float, inflation: float) -> float:
    return ((1 + nominal / 100) / (1 + inflation / 100) - 1) * 100


def month_end(month: str) -> str:
    """'2026-09-01' → '2026-09-30'."""
    y, m = int(month[:4]), int(month[5:7])
    return date(y, m, calendar.monthrange(y, m)[1]).isoformat()


def shift_months(month: str, n: int) -> str:
    y, m = int(month[:4]), int(month[5:7]) + n
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}-01"


def value_at_or_before(series: Series, iso: str) -> float | None:
    """Último valor com data <= iso (série ordenada por data)."""
    dates = [d for d, _ in series]
    i = bisect.bisect_right(dates, iso)
    return series[i - 1][1] if i else None


def cpi_12m(cpi: dict[str, float], month: str) -> float | None:
    a, b = cpi.get(month), cpi.get(shift_months(month, -12))
    return None if a is None or b is None else (a / b - 1) * 100


def real_rates(selic: Series, ipca12: Series, effr: Series, cpi: dict[str, float], months: int = MONTHS) -> dict:
    ipca = {d[:7] + "-01": v for d, v in ipca12}
    last_month = max(list(ipca) + list(cpi)) if (ipca or cpi) else None
    if last_month is None:
        raise RuntimeError("juro real: sem inflação")
    month_list = [shift_months(last_month, -k) for k in range(months - 1, -1, -1)]
    rows, latest_br, latest_us, us_gaps = [], None, None, []
    for m in month_list:
        end = month_end(m)
        br = us_ = None
        n_br = value_at_or_before(selic, end)
        if m in ipca and n_br is not None:
            br = fisher(n_br, ipca[m])
            latest_br = {"month": m, "nominal": n_br, "inflation": ipca[m], "real": round(br, 4)}
        infl_us = cpi_12m(cpi, m)
        n_us = value_at_or_before(effr, end)
        if infl_us is not None and n_us is not None:
            us_ = fisher(n_us, infl_us)
            latest_us = {"month": m, "nominal": n_us, "inflation": round(infl_us, 4), "real": round(us_, 4)}
        elif cpi and m <= max(cpi):
            us_gaps.append(m)  # mês sem CPI 12 meses (ex.: a BLS não publicou out/2025)
        rows.append([m, None if br is None else round(br, 4), None if us_ is None else round(us_, 4)])
    # Descarta meses do começo sem nenhum dos dois (janela começa no 1º mês com dado).
    while rows and rows[0][1] is None and rows[0][2] is None:
        rows.pop(0)
    if latest_br is None or latest_us is None:
        raise RuntimeError("juro real: falta o dado mais recente do Brasil ou dos EUA")
    return {"br": latest_br, "us": latest_us, "series": rows, "usGaps": us_gaps}


def inflation_target(ipca12: Series, months: int = MONTHS) -> dict:
    pts = [[d[:7] + "-01", v] for d, v in ipca12][-months:]
    if len(pts) < 12:
        raise RuntimeError("inflação × meta: série curta demais")
    return {**INFLATION_TARGET, "series": pts, "latest": {"month": pts[-1][0], "value": pts[-1][1]}}


def build_export(conn: sqlite3.Connection) -> dict:
    selic = db.price_series(conn, "SELIC_META")
    ipca12 = db.price_series(conn, "IPCA12M")
    effr = us.series(conn, "effr")
    cpi = dict(us.series(conn, "cpi"))
    return {
        "realRate": {
            **real_rates(selic, ipca12, effr, cpi),
            "sources": "Banco Central (SELIC meta, IPCA 12m) · New York Fed (EFFR) · BLS (CPI-U)",
        },
        "inflationTarget": inflation_target(ipca12),
    }
