"""BIS (Banco de Compensações Internacionais) — fonte única do juro real no mundo.

API SDMX pública, sem chave, em CSV:
- WS_CBPOL: taxas básicas dos bancos centrais (mensal, valor do fim do mês);
- WS_LONG_CPI, medida 771: inflação ao consumidor, variação em 12 meses (mensal).

Usar uma fonte só para os 10 países garante a mesma frequência e metodologia na
comparação. Substituiu o New York Fed (EFFR) e a BLS (CPI), que cobriam só os EUA.
O BIS publica com cerca de 1 mês de atraso em relação às fontes nacionais.
"""

from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date

import requests

BASE = "https://stats.bis.org/api/v1/data"

# Ordem e nomes de exibição. Grandes economias, BRICS e vizinhos da América Latina.
COUNTRIES: dict[str, str] = {
    "BR": "Brasil",
    "US": "EUA",
    "XM": "Zona do Euro",
    "GB": "Reino Unido",
    "JP": "Japão",
    "CN": "China",
    "IN": "Índia",
    "ZA": "África do Sul",
    "MX": "México",
    "CL": "Chile",
}


def _url(flow: str, key: str, start: date) -> str:
    return f"{BASE}/{flow}/{key}/all?startPeriod={start:%Y-%m}&format=csv"


def policy_url(start: date) -> str:
    return _url("WS_CBPOL", f"M.{'+'.join(COUNTRIES)}", start)


def cpi_url(start: date) -> str:
    return _url("WS_LONG_CPI", f"M.{'+'.join(COUNTRIES)}.771", start)


def parse_csv(text: str, kind: str) -> list[tuple[str, str, float]]:
    """CSV do BIS → linhas (date, '<kind>:<país>', valor). Valores vazios ou 'NaN' são descartados."""
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not {"REF_AREA", "TIME_PERIOD", "OBS_VALUE"} <= set(reader.fieldnames):
        raise ValueError("BIS: CSV fora do formato esperado")
    out = []
    for r in reader:
        country, period, raw = r["REF_AREA"], r["TIME_PERIOD"], r["OBS_VALUE"]
        if country not in COUNTRIES or len(period) != 7:
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if value != value:  # NaN
            continue
        out.append((f"{period}-01", f"{kind}:{country}", value))
    return out


def _get(url: str) -> str:
    resp = requests.get(url, timeout=60, headers={"Accept": "text/csv"})
    resp.raise_for_status()
    return resp.text


def fetch_policy(start: date) -> list[tuple[str, str, float]]:
    return parse_csv(_get(policy_url(start)), "policy")


def fetch_cpi(start: date) -> list[tuple[str, str, float]]:
    return parse_csv(_get(cpi_url(start)), "cpi")


def upsert(conn: sqlite3.Connection, rows: list[tuple[str, str, float]]) -> int:
    conn.executemany(
        """
        INSERT INTO bis_series (date, series, value) VALUES (?, ?, ?)
        ON CONFLICT(series, date) DO UPDATE SET value = excluded.value
        """,
        rows,
    )
    return len(rows)


def series(conn: sqlite3.Connection, name: str) -> list[tuple[str, float]]:
    return conn.execute("SELECT date, value FROM bis_series WHERE series = ? ORDER BY date", (name,)).fetchall()


def last_dates(conn: sqlite3.Connection) -> dict[str, str]:
    return dict(conn.execute("SELECT series, MAX(date) FROM bis_series GROUP BY series").fetchall())
