"""Indicadores derivados para as telas Mundo e Brasil (macro.json).

- Juro real no mundo (ex-post), fonte única BIS: taxa básica do fim do mês descontada da
  inflação dos 12 meses até aquele mês, pela fórmula de Fisher: (1 + juro) / (1 + inflação) − 1.
  O ranking usa o mês mais recente que TODOS os países têm (comparação no mesmo mês).
- Inflação × meta: IPCA 12 meses (BCB) contra a meta contínua do CMN.
Nada é projetado: tudo é inflação já medida e taxa já praticada.
"""

from __future__ import annotations

import sqlite3

from . import bis, db

MONTHS = 24
# Juro real no mundo: 10 anos, para o filtro 2 · 5 · 10 anos da tela Mundo.
REAL_RATE_MONTHS = 120

# Meta de inflação definida pelo Conselho Monetário Nacional (CMN): 3,0% ao ano,
# com intervalo de tolerância de 1,5 ponto para mais ou para menos (meta contínua).
INFLATION_TARGET = {"center": 3.0, "lower": 1.5, "upper": 4.5, "source": "CMN (Conselho Monetário Nacional)"}

Series = list[tuple[str, float]]


def fisher(nominal: float, inflation: float) -> float:
    return ((1 + nominal / 100) / (1 + inflation / 100) - 1) * 100


def shift_months(month: str, n: int) -> str:
    y, m = int(month[:4]), int(month[5:7]) + n
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}-01"


def world_real_rates(policy: dict[str, dict[str, float]], cpi: dict[str, dict[str, float]], months: int = REAL_RATE_MONTHS) -> dict:
    """policy/cpi: {país: {mês: valor}}. Devolve o ranking no último mês comum e 24 meses por país."""
    countries = [c for c in bis.COUNTRIES if policy.get(c) and cpi.get(c)]
    if len(countries) < len(bis.COUNTRIES):
        faltam = sorted(set(bis.COUNTRIES) - set(countries))
        raise RuntimeError(f"juro real no mundo: sem dados do BIS para {faltam}")
    common = set.intersection(*(set(policy[c]) & set(cpi[c]) for c in countries))
    if not common:
        raise RuntimeError("juro real no mundo: nenhum mês com dados de todos os países")
    month = max(common)
    ranking = []
    for c in countries:
        p, i = policy[c][month], cpi[c][month]
        ranking.append({"code": c, "name": bis.COUNTRIES[c], "policy": p, "inflation": round(i, 4), "real": round(fisher(p, i), 4)})
    ranking.sort(key=lambda r: r["real"], reverse=True)
    window = [shift_months(month, -k) for k in range(months - 1, -1, -1)]
    series = {
        c: [[m, round(fisher(policy[c][m], cpi[c][m]), 4)] for m in window if m in policy[c] and m in cpi[c]]
        for c in countries
    }
    return {"month": month, "ranking": ranking, "series": series}


def inflation_target(ipca12: Series, months: int = MONTHS) -> dict:
    pts = [[d[:7] + "-01", v] for d, v in ipca12][-months:]
    if len(pts) < 12:
        raise RuntimeError("inflação × meta: série curta demais")
    return {**INFLATION_TARGET, "series": pts, "latest": {"month": pts[-1][0], "value": pts[-1][1]}}


def build_export(conn: sqlite3.Connection) -> dict:
    policy = {c: dict(bis.series(conn, f"policy:{c}")) for c in bis.COUNTRIES}
    cpi = {c: dict(bis.series(conn, f"cpi:{c}")) for c in bis.COUNTRIES}
    return {
        "realRate": {
            **world_real_rates(policy, cpi),
            "source": "BIS — Banco de Compensações Internacionais (taxas básicas e inflação ao consumidor)",
        },
        "inflationTarget": inflation_target(db.price_series(conn, "IPCA12M")),
    }
