"""EUA, fontes oficiais e sem chave:

- EFFR (taxa efetiva dos Fed Funds) — New York Fed Markets API, diária.
- CPI-U (todos os itens, sem ajuste sazonal, série CUUR0000SA0) — BLS API v1, mensal.

A API v1 da BLS dispensa cadastro (com limite diário de consultas, suficiente para
uma coleta por dia). Meses sem valor vêm como "-" — ex.: out/2025 não foi publicado —
e são descartados; o CPI 12 meses só é calculado quando os dois meses existem.
"""

from __future__ import annotations

import sqlite3
from datetime import date

import requests

EFFR_URL = "https://markets.newyorkfed.org/api/rates/unsecured/effr/search.json"
BLS_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
CPI_SERIES = "CUUR0000SA0"


def parse_effr(payload: dict) -> list[tuple[str, str, float]]:
    rates = payload.get("refRates") if isinstance(payload, dict) else None
    if not rates:
        raise ValueError("NY Fed: resposta sem refRates")
    out = []
    for r in rates:
        if r.get("type") != "EFFR":
            continue
        try:
            out.append((r["effectiveDate"], "effr", float(r["percentRate"])))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def parse_cpi(payload: dict) -> list[tuple[str, str, float]]:
    if not isinstance(payload, dict) or payload.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError(f"BLS: {payload.get('status') if isinstance(payload, dict) else 'resposta inválida'}")
    series = payload["Results"]["series"][0]["data"]
    out = []
    for d in series:
        period = d.get("period", "")
        if not period.startswith("M") or period == "M13":  # M13 = média anual
            continue
        try:
            value = float(d["value"])
        except (KeyError, TypeError, ValueError):
            continue  # "-": mês não publicado
        out.append((f"{d['year']}-{period[1:]}-01", "cpi", value))
    return out


def fetch_effr(start: date, end: date) -> list[tuple[str, str, float]]:
    resp = requests.get(EFFR_URL, params={"startDate": start.isoformat(), "endDate": end.isoformat()}, timeout=30)
    resp.raise_for_status()
    return parse_effr(resp.json())


def fetch_cpi(start_year: int, end_year: int) -> list[tuple[str, str, float]]:
    body = {"seriesid": [CPI_SERIES], "startyear": str(start_year), "endyear": str(end_year)}
    resp = requests.post(BLS_URL, json=body, timeout=30)
    resp.raise_for_status()
    return parse_cpi(resp.json())


def upsert(conn: sqlite3.Connection, rows: list[tuple[str, str, float]]) -> int:
    conn.executemany(
        """
        INSERT INTO us_series (date, series, value) VALUES (?, ?, ?)
        ON CONFLICT(series, date) DO UPDATE SET value = excluded.value
        """,
        rows,
    )
    return len(rows)


def series(conn: sqlite3.Connection, name: str) -> list[tuple[str, float]]:
    return conn.execute("SELECT date, value FROM us_series WHERE series = ? ORDER BY date", (name,)).fetchall()


def last_dates(conn: sqlite3.Connection) -> dict[str, str]:
    return dict(conn.execute("SELECT series, MAX(date) FROM us_series GROUP BY series").fetchall())
