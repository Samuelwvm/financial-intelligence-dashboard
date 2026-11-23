"""Exporta JSON estáticos para o frontend (web/public/data/).

O site não calcula métricas: tudo sai daqui, uma vez por dia.
Contrato espelhado em web/lib/schema.ts (validado com Zod no build).
"""

from __future__ import annotations

import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from . import db
from .assets import ASSETS, BY_SYMBOL, DEFAULT_PORTFOLIO, INDICATORS, PORTFOLIO_CANDIDATES, PULSE
from .glossary import CATEGORIES, GLOSSARY
from .metrics import PERIODS, align_ffill, base100, daily_change, period_stats

SCHEMA_VERSION = 1
OUT_DIR = db.ROOT / "web" / "public" / "data"
BENCHMARK = "^BVSP"


def _r(x: float, nd: int = 4) -> float:
    return round(float(x), nd)


def _asset_summary(a, series) -> dict:
    stats = {}
    for period in PERIODS:
        s = period_stats(series, period)
        stats[period] = {"ret": _r(s.ret), "vol": _r(s.vol), "high": _r(s.high), "low": _r(s.low)}
    return {
        "symbol": a.symbol, "slug": a.slug, "name": a.name, "ticker": a.ticker,
        "group": a.group, "kind": a.kind, "currency": a.currency, "market": a.market,
        "lastDate": series[-1][0], "price": _r(series[-1][1]), "change": _r(daily_change(series)),
        "stats": stats,
    }


def _macro(conn: sqlite3.Connection) -> dict:
    out = {}
    keys = {"SELIC_META": "selic", "SELIC": "selicDaily", "CDI": "cdi", "IPCA12M": "ipca12m", "IPCA": "ipcaMonthly"}
    for ind in INDICATORS:
        row = conn.execute(
            "SELECT date, price FROM assets_history WHERE symbol = ? ORDER BY date DESC LIMIT 1", (ind.symbol,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"indicador sem dados: {ind.symbol}")
        out[keys[ind.symbol]] = {"value": _r(row[1], 6), "date": row[0]}
    return out


def build(conn: sqlite3.Connection, generated_at: datetime | None = None) -> dict[str, object]:
    """Monta todos os documentos em memória: {caminho relativo: conteúdo}."""
    generated_at = generated_at or datetime.now(timezone.utc)
    series_by_symbol = {}
    for a in ASSETS:
        s = db.price_series(conn, a.symbol)
        if len(s) < 2:
            raise RuntimeError(f"ativo sem histórico suficiente: {a.symbol}")
        series_by_symbol[a.symbol] = s

    summaries = [_asset_summary(a, series_by_symbol[a.symbol]) for a in ASSETS]
    by_symbol = {s["symbol"]: s for s in summaries}
    docs: dict[str, object] = {}

    docs["summary.json"] = {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "asOf": max(s["lastDate"] for s in summaries),
        "pulse": [by_symbol[sym]["slug"] for sym in PULSE],
        "portfolio": {
            "candidates": [BY_SYMBOL[s].slug for s in PORTFOLIO_CANDIDATES],
            "default": [BY_SYMBOL[s].slug for s in DEFAULT_PORTFOLIO],
            "benchmark": BY_SYMBOL[BENCHMARK].slug,
        },
        "macro": _macro(conn),
        "assets": summaries,
    }

    for a in ASSETS:
        series = series_by_symbol[a.symbol]
        periods = {}
        for period in PERIODS:
            st = period_stats(series, period)
            periods[period] = {"base": _r(st.base), "points": [[d, _r(p)] for d, p in st.points]}
        docs[f"series/{a.slug}.json"] = {"slug": a.slug, "periods": periods}

    members = list(PORTFOLIO_CANDIDATES) + [BENCHMARK]
    for period in PERIODS:
        cols = {BY_SYMBOL[s].slug: base100(period_stats(series_by_symbol[s], period).points) for s in members}
        dates, aligned = align_ffill(cols)
        docs[f"portfolio/{period}.json"] = {
            "period": period,
            "dates": dates,
            "series": {k: [None if v is None else round(v, 3) for v in vals] for k, vals in aligned.items()},
        }

    docs["glossary.json"] = {"categories": CATEGORIES, "terms": GLOSSARY}
    return docs


def write(docs: dict[str, object], out_dir: Path = OUT_DIR) -> None:
    """Escreve num diretório temporário e troca de uma vez (nunca deixa export pela metade)."""
    tmp = out_dir.with_name(out_dir.name + ".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    for rel, doc in docs.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    tmp.rename(out_dir)
