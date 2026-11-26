"""IBGE · SIDRA (API pública, sem chave): IPCA por grupo e taxa de desemprego.

- IPCA por grupo — tabela 7060: variação mensal (v63), peso mensal (v66) e
  variação acumulada em 12 meses (v2265), índice geral + 9 grupos (classificação 315).
- Desemprego — tabela 6381: taxa de desocupação (v4099), PNAD Contínua, trimestre móvel.

Formato do SIDRA: uma lista em que o 1º item é o cabeçalho (rótulos das colunas) e
os demais são as linhas; o período vem em D3C ("202610"); valores ausentes vêm como
"...", "-", "X" etc. Busca sempre uma janela (incremental por natureza) e grava com upsert.
"""

from __future__ import annotations

import sqlite3

import requests

BASE = "https://apisidra.ibge.gov.br/values"

IPCA_TABLE = 7060
IPCA_VARS = {"63": "mensal", "66": "peso", "2265": "12m"}
IPCA_GROUPS: dict[str, str] = {
    "7169": "Índice geral",
    "7170": "Alimentação e bebidas",
    "7445": "Habitação",
    "7486": "Artigos de residência",
    "7558": "Vestuário",
    "7625": "Transportes",
    "7660": "Saúde e cuidados pessoais",
    "7712": "Despesas pessoais",
    "7766": "Educação",
    "7786": "Comunicação",
}
UNEMPLOYMENT_TABLE = 6381
UNEMPLOYMENT_VAR = "4099"
UNEMPLOYMENT_SERIES = "desocupacao"

IPCA_URL = (
    f"{BASE}/t/{IPCA_TABLE}/n1/all/v/{','.join(IPCA_VARS)}/p/last%2013/c315/{','.join(IPCA_GROUPS)}"
)
UNEMPLOYMENT_URL = f"{BASE}/t/{UNEMPLOYMENT_TABLE}/n1/all/v/{UNEMPLOYMENT_VAR}/p/last%2036"


def _period_to_date(code: str) -> str:
    """'202610' → '2026-10-01'."""
    if len(code) != 6 or not code.isdigit():
        raise ValueError(f"período inesperado do SIDRA: {code!r}")
    return f"{code[:4]}-{code[4:]}-01"


def _value(raw: str) -> float | None:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None  # "...", "-", "X": sem dado / sigiloso


def parse_ipca(payload: list[dict]) -> list[tuple[str, str, float]]:
    """Linhas (date, series, value) a partir da resposta da tabela 7060."""
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("SIDRA 7060: resposta vazia ou fora do formato")
    out = []
    for r in payload[1:]:  # o 1º item é o cabeçalho
        var, group, v = r.get("D2C"), r.get("D4C"), _value(r.get("V"))
        if var not in IPCA_VARS or group not in IPCA_GROUPS or v is None:
            continue
        out.append((_period_to_date(r["D3C"]), f"ipca:{group}:{IPCA_VARS[var]}", v))
    return out


def parse_unemployment(payload: list[dict]) -> list[tuple[str, str, float]]:
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("SIDRA 6381: resposta vazia ou fora do formato")
    out = []
    for r in payload[1:]:
        v = _value(r.get("V"))
        if r.get("D2C") == UNEMPLOYMENT_VAR and v is not None:
            out.append((_period_to_date(r["D3C"]), UNEMPLOYMENT_SERIES, v))
    return out


def _get(url: str) -> list[dict]:
    resp = requests.get(url, timeout=30, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def fetch_ipca() -> list[tuple[str, str, float]]:
    return parse_ipca(_get(IPCA_URL))


def fetch_unemployment() -> list[tuple[str, str, float]]:
    return parse_unemployment(_get(UNEMPLOYMENT_URL))


def upsert(conn: sqlite3.Connection, rows: list[tuple[str, str, float]]) -> int:
    conn.executemany(
        """
        INSERT INTO ibge_series (date, series, value) VALUES (?, ?, ?)
        ON CONFLICT(series, date) DO UPDATE SET value = excluded.value
        """,
        rows,
    )
    return len(rows)


def last_dates(conn: sqlite3.Connection) -> dict[str, str]:
    return dict(conn.execute("SELECT series, MAX(date) FROM ibge_series GROUP BY series").fetchall())


def series(conn: sqlite3.Connection, name: str) -> list[tuple[str, float]]:
    return conn.execute("SELECT date, value FROM ibge_series WHERE series = ? ORDER BY date", (name,)).fetchall()


def build_export(conn: sqlite3.Connection) -> dict:
    """Documento ibge.json consumido pela tela Brasil."""
    # IPCA por grupo no mês mais recente com o índice geral publicado.
    general = series(conn, "ipca:7169:mensal")
    if not general:
        raise RuntimeError("IBGE: IPCA por grupo sem dados")
    month = general[-1][0]

    def at(name: str) -> float | None:
        row = conn.execute("SELECT value FROM ibge_series WHERE series = ? AND date = ?", (name, month)).fetchone()
        return None if row is None else row[0]

    groups = []
    for code, label in IPCA_GROUPS.items():
        if code == "7169":
            continue
        m, w, y = at(f"ipca:{code}:mensal"), at(f"ipca:{code}:peso"), at(f"ipca:{code}:12m")
        if m is None or w is None or y is None:
            continue
        # Impacto no IPCA do mês, em pontos percentuais: peso × variação (convenção do IBGE).
        groups.append({"code": code, "name": label, "monthly": m, "weight": w, "yoy": y, "impact": round(w * m / 100, 4)})
    if len(groups) < 9:
        raise RuntimeError(f"IBGE: só {len(groups)} de 9 grupos do IPCA em {month}")

    unemp = series(conn, UNEMPLOYMENT_SERIES)
    if len(unemp) < 13:
        raise RuntimeError("IBGE: série de desemprego curta demais")
    last_date, last_value = unemp[-1]
    year_ago = next((v for d, v in unemp if d == f"{int(last_date[:4]) - 1}{last_date[4:]}"), None)

    return {
        "source": "IBGE · SIDRA",
        "ipca": {
            "month": month,
            "general": {"monthly": at("ipca:7169:mensal"), "yoy": at("ipca:7169:12m")},
            "groups": groups,
        },
        "unemployment": {
            "date": last_date,  # último mês do trimestre móvel
            "value": last_value,
            "yearAgo": year_ago,
            "series": [[d, v] for d, v in unemp[-24:]],
        },
    }
