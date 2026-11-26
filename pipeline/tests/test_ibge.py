"""IBGE · SIDRA: parse do formato, gravação idempotente, export e saúde."""

from datetime import date

import pytest

from pipeline import db, health, ibge

HEADER = {"NC": "Nível Territorial (Código)", "D2C": "Variável (Código)", "D3C": "Mês (Código)", "D4C": "Geral, grupo... (Código)", "V": "Valor"}


def row(var, period, group, value):
    return {"D2C": var, "D3C": period, "D4C": group, "V": value}


def ipca_payload(period="202610"):
    rows = [HEADER]
    for code in ibge.IPCA_GROUPS:
        rows += [row("63", period, code, "0.50"), row("66", period, code, "10.0"), row("2265", period, code, "4.00")]
    rows[1]["V"] = "0.14"  # índice geral, mensal
    return rows


def test_parse_ipca_skips_header_and_missing_values():
    payload = ipca_payload()
    payload.append(row("63", "202610", "7170", "..."))  # sem dado → ignorado
    payload.append(row("63", "202610", "9999", "1.0"))  # grupo fora da lista → ignorado
    out = ibge.parse_ipca(payload)
    assert len(out) == 3 * len(ibge.IPCA_GROUPS)
    assert ("2026-10-01", "ipca:7169:mensal", 0.14) in out
    assert all(d == "2026-10-01" for d, _, _ in out)


def test_parse_unemployment_and_bad_period():
    payload = [HEADER, row("4099", "202609", None, "5.2"), row("4099", "202608", None, "-")]
    assert ibge.parse_unemployment(payload) == [("2026-09-01", "desocupacao", 5.2)]
    with pytest.raises(ValueError):
        ibge.parse_unemployment([HEADER, row("4099", "2026-09", None, "5.2")])


def test_parse_rejects_empty_response():
    with pytest.raises(ValueError):
        ibge.parse_ipca([HEADER])


def fill(conn):
    ibge.upsert(conn, ibge.parse_ipca(ipca_payload("202609")))
    ibge.upsert(conn, ibge.parse_ipca(ipca_payload("202610")))
    unemp = [(f"{2024 + (m - 1) // 12}-{(m - 1) % 12 + 1:02d}-01", "desocupacao", 6.0 - m * 0.02) for m in range(9, 34)]
    ibge.upsert(conn, unemp)


@pytest.fixture
def conn(tmp_path):
    with db.connect(tmp_path / "t.db") as c:
        db.initialize(c)
        yield c


def test_upsert_is_idempotent_and_corrects_revisions(conn):
    rows = ibge.parse_ipca(ipca_payload())
    ibge.upsert(conn, rows)
    ibge.upsert(conn, rows)
    assert conn.execute("SELECT COUNT(*) FROM ibge_series").fetchone()[0] == len(rows)
    ibge.upsert(conn, [("2026-10-01", "ipca:7169:mensal", 0.15)])  # IBGE revisou
    assert ibge.series(conn, "ipca:7169:mensal") == [("2026-10-01", 0.15)]


def test_export_latest_month_groups_and_impact(conn):
    fill(conn)
    doc = ibge.build_export(conn)
    assert doc["ipca"]["month"] == "2026-10-01"
    assert doc["ipca"]["general"] == {"monthly": 0.14, "yoy": 4.0}
    assert len(doc["ipca"]["groups"]) == 9
    g = doc["ipca"]["groups"][0]
    assert g["impact"] == pytest.approx(g["weight"] * g["monthly"] / 100)
    u = doc["unemployment"]
    assert u["date"] == "2026-09-01" and len(u["series"]) == 25  # histórico completo
    # mesmo mês do ano anterior (set/2025 = m 21 na série sintética: 6,0 − 21 × 0,02)
    assert u["yearAgo"] == pytest.approx(6.0 - 21 * 0.02)


def test_export_fails_clearly_without_groups(conn):
    ibge.upsert(conn, [("2026-10-01", "ipca:7169:mensal", 0.14)])
    with pytest.raises(RuntimeError):
        ibge.build_export(conn)


def test_health_ibge():
    today = date(2026, 11, 25)
    assert health.check_ibge({"ipca:7169:mensal": "2026-10-01", "desocupacao": "2026-09-01"}, today) == []
    problems = health.check_ibge({"ipca:7169:mensal": "2026-07-01"}, today)
    assert any("ipca" in p for p in problems) and any("desocupacao" in p for p in problems)
