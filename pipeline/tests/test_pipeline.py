"""Coleta idempotente, limpeza de linhas ruins, retry e saúde."""

import math
from datetime import date

import pytest

from pipeline import db, health
from pipeline.assets import ASSETS, INDICATORS
from pipeline.collectors import CollectError, clean_rows, with_retry


@pytest.fixture
def conn(tmp_path):
    with db.connect(tmp_path / "t.db") as c:
        db.initialize(c)
        db.upsert_metadata(c, [("AAA", "Teste", "Ação BR", "X")])
        yield c


def count(c):
    return c.execute("SELECT COUNT(*) FROM assets_history").fetchone()[0]


def test_upsert_is_idempotent(conn):
    rows = [("2026-01-02", 10.0), ("2026-01-05", 11.0)]
    db.upsert_prices(conn, "AAA", rows)
    db.upsert_prices(conn, "AAA", rows)
    assert count(conn) == 2


def test_upsert_corrects_partial_price_and_fills_gap(conn):
    db.upsert_prices(conn, "AAA", [("2026-01-02", 10.0), ("2026-01-06", 12.5)])  # 05/01 perdido, 06/01 parcial
    db.upsert_prices(conn, "AAA", [("2026-01-02", 10.0), ("2026-01-05", 11.0), ("2026-01-06", 12.0)])
    assert db.price_series(conn, "AAA") == [("2026-01-02", 10.0), ("2026-01-05", 11.0), ("2026-01-06", 12.0)]


def test_foreign_key_enforced(conn):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        db.upsert_prices(conn, "NAO_CADASTRADO", [("2026-01-02", 1.0)])


def test_schema_has_symbol_date_index(conn):
    plan = conn.execute("EXPLAIN QUERY PLAN SELECT price FROM assets_history WHERE symbol='AAA' ORDER BY date DESC LIMIT 1").fetchall()
    assert "idx_history_symbol_date" in " ".join(r[3] for r in plan)


def test_clean_rows_drops_nan_nonpositive_and_future():
    rows = [("2026-01-02", 10.0), ("2026-01-05", math.nan), ("2026-01-06", 0.0), ("2026-01-07", -1.0), ("2030-01-01", 5.0)]
    assert clean_rows(rows, date(2026, 1, 10)) == [("2026-01-02", 10.0)]


def test_retry_recovers_then_gives_up():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("rate limit")
        return [("2026-01-02", 1.0)]

    assert with_retry(flaky, "X", sleep=lambda s: None) == [("2026-01-02", 1.0)]
    with pytest.raises(CollectError):
        with_retry(lambda: [], "VAZIO", sleep=lambda s: None)


def fresh_dates(today_iso="2026-11-20"):
    d = {a.symbol: today_iso for a in ASSETS}
    d.update({i.symbol: today_iso for i in INDICATORS})
    d["IPCA"] = d["IPCA12M"] = "2026-10-01"
    return d


def test_health_ok_when_fresh():
    assert health.check(fresh_dates(), date(2026, 11, 21)) == []


def test_health_flags_stale_asset_like_v1_dow_jones():
    d = fresh_dates()
    d["^DJI"] = "2026-04-02"
    problems = health.check(d, date(2026, 11, 21))
    assert len(problems) == 1 and problems[0].startswith("^DJI")


def test_health_flags_frozen_monthly_ipca_like_v1():
    d = fresh_dates()
    d["IPCA12M"] = "2026-02-01"
    assert any(p.startswith("IPCA12M") for p in health.check(d, date(2026, 11, 21)))


def test_health_tolerates_weekend_and_short_holiday():
    # última sexta 13/11, job roda terça 17/11 01:17 UTC: falta só segunda (1 pregão)
    assert health.lag(date(2026, 11, 13), date(2026, 11, 17), "weekdays") == 1
    assert health.lag(date(2026, 11, 16), date(2026, 11, 17), "weekdays") == 0
    # Aramco negocia dom–qui: quinta 19/11 -> domingo 22/11 ainda sem atraso
    assert health.lag(date(2026, 11, 19), date(2026, 11, 22), "sun-thu") == 0
