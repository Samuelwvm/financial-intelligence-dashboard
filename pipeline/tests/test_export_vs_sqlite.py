"""Compara os JSON exportados com um cálculo independente feito direto no SQLite
(SQL + pandas, sem passar por pipeline.metrics).

Roda contra o banco real (data/finance.db) quando ele existe, e sempre contra
um banco sintético.
"""

import math
import random
import sqlite3
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from pipeline import db, export
from pipeline.assets import ASSETS, INDICATORS

PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}


def independent(conn: sqlite3.Connection, symbol: str, days: int) -> dict:
    last_date, last_price = conn.execute(
        "SELECT date, price FROM assets_history WHERE symbol=? ORDER BY date DESC LIMIT 1", (symbol,)).fetchone()
    start = conn.execute("SELECT date(?, ?)", (last_date, f"-{days} days")).fetchone()[0]
    row = conn.execute("SELECT date FROM assets_history WHERE symbol=? AND date<=? ORDER BY date DESC LIMIT 1",
                       (symbol, start)).fetchone()
    base_date = row[0] if row else conn.execute(
        "SELECT MIN(date) FROM assets_history WHERE symbol=?", (symbol,)).fetchone()[0]
    df = pd.read_sql_query("SELECT date, price FROM assets_history WHERE symbol=? AND date>=? ORDER BY date",
                           conn, params=(symbol, base_date))
    vol = df["price"].pct_change().std() * np.sqrt(252) * 100
    return {
        "ret": (last_price / df["price"].iloc[0] - 1) * 100,
        "vol": 0.0 if pd.isna(vol) else vol,
        "high": df["price"].max(),
        "low": df["price"].min(),
        "n": len(df),
    }


def check_docs(conn, docs, symbols):
    summary = {a["symbol"]: a for a in docs["summary.json"]["assets"]}
    by_sym = {a.symbol: a for a in ASSETS}
    for sym in symbols:
        for period, days in PERIOD_DAYS.items():
            exp = independent(conn, sym, days)
            got = summary[sym]["stats"][period]
            assert got["ret"] == pytest.approx(exp["ret"], abs=1e-3), (sym, period)
            assert got["vol"] == pytest.approx(exp["vol"], abs=1e-3), (sym, period)
            assert got["high"] == pytest.approx(exp["high"], abs=1e-3), (sym, period)
            assert got["low"] == pytest.approx(exp["low"], abs=1e-3), (sym, period)
            pts = docs[f"series/{by_sym[sym].slug}.json"]["periods"][period]["points"]
            assert len(pts) == exp["n"], (sym, period)
            # base 100 da carteira termina no retorno do card
            port = docs[f"portfolio/{period}.json"]["series"].get(by_sym[sym].slug)
            if port:
                assert port[-1] - 100 == pytest.approx(exp["ret"], abs=1e-2), (sym, period)


def make_synthetic(path):
    rnd = random.Random(42)
    with db.connect(path) as conn:
        db.initialize(conn)
        rows = [(a.symbol, a.name, a.category, a.sector) for a in ASSETS]
        rows += [(i.symbol, i.name, "Macro", "Economia BR") for i in INDICATORS]
        db.upsert_metadata(conn, rows)
        d0 = date(2025, 10, 1)
        for a in ASSETS:
            p, series = 100.0, []
            for k in range(420):
                d = d0 + timedelta(days=k)
                if a.calendar == "weekdays" and d.weekday() >= 5:
                    continue
                if rnd.random() < 0.02:  # lacunas aleatórias (feriados)
                    continue
                p *= math.exp(rnd.gauss(0, 0.02))
                series.append((d.isoformat(), p))
            db.upsert_prices(conn, a.symbol, series)
        for i in INDICATORS:
            db.upsert_prices(conn, i.symbol, [("2026-10-01", 4.5), ("2026-11-20", 13.75)])


def test_export_matches_independent_calc_synthetic(tmp_path):
    path = tmp_path / "syn.db"
    make_synthetic(path)
    with db.connect(path) as conn:
        docs = export.build(conn)
        check_docs(conn, docs, [a.symbol for a in ASSETS])


@pytest.mark.skipif(not db.DEFAULT_DB.exists(), reason="sem data/finance.db local")
def test_export_matches_independent_calc_real_db():
    with db.connect(db.DEFAULT_DB) as conn:
        docs = export.build(conn)
        sample = ["PETR4.SA", "^BVSP", "AAPL", "USDBRL=X", "BTC-USD", "2222.SR", "^DJI"]
        check_docs(conn, docs, sample)


def test_export_contract_shape(tmp_path):
    path = tmp_path / "syn.db"
    make_synthetic(path)
    with db.connect(path) as conn:
        docs = export.build(conn)
    s = docs["summary.json"]
    assert s["schemaVersion"] == export.SCHEMA_VERSION
    assert set(s["macro"]) == {"selic", "selicDaily", "cdi", "ipca12m", "ipcaMonthly"}
    assert len(s["pulse"]) == 5 and len(s["assets"]) == len(ASSETS)
    for a in s["assets"]:
        assert set(a["stats"]) == {"1d", "7d", "30d", "90d", "1y"}
        assert f"series/{a['slug']}.json" in docs
    for period in ("1d", "7d", "30d", "90d", "1y"):
        p = docs[f"portfolio/{period}.json"]
        assert all(len(v) == len(p["dates"]) for v in p["series"].values())
    assert len(docs["glossary.json"]["terms"]) >= 20
