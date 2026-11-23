"""Saúde do pipeline: falha se algum ativo/indicador ficou sem dado novo.

É o que faltou na V1: o job ficava verde com ^DJI parado havia 8 meses.
Um job com falha gera e-mail automático do GitHub para o dono do repositório.
"""

from __future__ import annotations

import os
from datetime import date

import numpy as np

from .assets import ASSETS, INDICATORS

# Dias úteis de atraso tolerados (feriados de 1–2 dias + defasagem D-1).
MAX_LAG_BDAYS = int(os.environ.get("HEALTH_MAX_LAG_BDAYS", "4"))
MAX_LAG_CRYPTO_DAYS = 2
MAX_LAG_MONTHLY_DAYS = 80  # IPCA: mês M é publicado por volta do dia 10 de M+1

WEEKMASK = {"weekdays": "1111100", "sun-thu": "1111001", "daily": "1111111"}


def lag(last: date, today: date, calendar: str) -> int:
    """Dias de negociação esperados e ainda sem dado: os dias no intervalo
    (última data, hoje), sem contar nenhum dos dois extremos — o pregão de
    hoje ainda não fechou quando o job roda (01:17 UTC)."""
    if calendar == "daily":
        return (today - last).days
    begin = np.datetime64(last) + np.timedelta64(1, "D")
    end = np.datetime64(today)
    if begin >= end:
        return 0
    return int(np.busday_count(begin, end, weekmask=WEEKMASK[calendar]))


def check(last_dates: dict[str, str], today: date) -> list[str]:
    problems: list[str] = []
    for a in ASSETS:
        d = last_dates.get(a.symbol)
        if d is None:
            problems.append(f"{a.symbol}: sem nenhum dado")
            continue
        last = date.fromisoformat(d)
        n = lag(last, today, a.calendar)
        limit = MAX_LAG_CRYPTO_DAYS if a.calendar == "daily" else MAX_LAG_BDAYS
        if n > limit:
            problems.append(f"{a.symbol}: último dado em {d} ({n} dias de pregão sem atualização; limite {limit})")
    for ind in INDICATORS:
        d = last_dates.get(ind.symbol)
        if d is None:
            problems.append(f"{ind.symbol}: sem nenhum dado")
            continue
        last = date.fromisoformat(d)
        if ind.frequency == "monthly":
            n, limit = (today - last).days, MAX_LAG_MONTHLY_DAYS
        else:
            n, limit = lag(last, today, "weekdays"), MAX_LAG_BDAYS + 1
        if n > limit:
            problems.append(f"{ind.symbol}: último dado em {d} ({n} dias sem atualização; limite {limit})")
    return problems


def main() -> int:
    """`python -m pipeline.health`: falha (código 1) se houver dado desatualizado."""
    import sys

    from . import db
    from .collectors import utc_today

    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    with db.connect() as conn:
        problems = check(db.last_dates(conn), utc_today())
    if problems:
        print("Saúde do pipeline: dados desatualizados", file=sys.stderr)
        for p in problems:
            print(f"::error title=Dado desatualizado::{p}", file=sys.stderr)
        return 1
    print("Saúde do pipeline: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
