"""Pipeline diário: coleta → limpeza → analytics → saúde → export JSON.

Uso:
    python -m pipeline.run               # tudo
    python -m pipeline.run --skip-collect  # só recalcula e exporta a partir do banco
    python -m pipeline.run --no-health     # não falha por dado desatualizado (uso local)

Saída != 0 quando: mais da metade das coletas falha (provável instabilidade
da fonte — nada é gravado nem exportado), ou o passo de saúde encontra ativo
sem dado novo além do limite. Nesses casos o site publicado continua o anterior.
"""

from __future__ import annotations

import argparse
import sys
import time

import pandas as pd

from . import db, export, health
from .assets import ASSETS, INDICATORS
from .collectors import CollectResult, clean_rows, fetch_bcb, fetch_yahoo, utc_today, window_start, with_retry

KEEP_DAYS = 400


def collect(conn, today) -> CollectResult:
    """Busca todas as séries ANTES de gravar qualquer coisa."""
    result = CollectResult()
    start = window_start(today)
    fetched: dict[str, list[tuple[str, float]]] = {}
    for a in ASSETS:
        try:
            rows = clean_rows(with_retry(lambda: fetch_yahoo(a.symbol, start), a.symbol), today)
            if not rows:
                raise RuntimeError("nenhuma linha válida")
            fetched[a.symbol] = rows
        except Exception as exc:  # noqa: BLE001
            result.failed[a.symbol] = str(exc)
        time.sleep(0.3)  # gentileza com a fonte
    for ind in INDICATORS:
        try:
            rows = clean_rows(with_retry(lambda: fetch_bcb(ind.bcb_code, start, today), ind.symbol), today)
            fetched[ind.symbol] = rows
        except Exception as exc:  # noqa: BLE001
            result.failed[ind.symbol] = str(exc)

    total = len(ASSETS) + len(INDICATORS)
    if len(result.failed) > total / 2:
        raise RuntimeError(f"{len(result.failed)}/{total} coletas falharam; nada foi gravado: {result.failed}")

    for symbol, rows in fetched.items():
        result.ok[symbol] = db.upsert_prices(conn, symbol, rows)
    return result


def sync_metadata(conn) -> None:
    rows = [(a.symbol, a.name, a.category, a.sector) for a in ASSETS]
    rows += [(i.symbol, i.name, "Macro", "Economia BR") for i in INDICATORS]
    db.upsert_metadata(conn, rows)


def recalc_variations(conn) -> None:
    """Variação dia a dia por símbolo (mesma fórmula da V1: analytics.calculate_variations)."""
    df = pd.read_sql_query("SELECT rowid, symbol, date, price FROM assets_history ORDER BY symbol, date", conn)
    if df.empty:
        return
    df["variation"] = df.groupby("symbol")["price"].pct_change().mul(100).fillna(0).round(4)
    conn.executemany("UPDATE assets_history SET variation = ? WHERE rowid = ?",
                     zip(df["variation"].tolist(), df["rowid"].tolist()))


def purge(conn, today) -> int:
    cutoff = pd.Timestamp(today) - pd.Timedelta(days=KEEP_DAYS)
    return conn.execute("DELETE FROM assets_history WHERE date < ?", (cutoff.strftime("%Y-%m-%d"),)).rowcount


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-collect", action="store_true")
    ap.add_argument("--no-health", action="store_true")
    ap.add_argument("--no-export", action="store_true")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # Windows: console em cp1252

    t0 = time.time()
    today = utc_today()
    print(f"Radar Financeiro · pipeline · {today} (UTC) · banco: {db.db_path()}")

    with db.connect() as conn:
        db.initialize(conn)
        sync_metadata(conn)

    result = CollectResult()
    if not args.skip_collect:
        try:
            with db.connect() as conn:  # uma transação: ou grava tudo que foi coletado, ou nada
                result = collect(conn, today)
        except Exception as exc:
            with db.connect() as conn:
                db.log_update(conn, "Erro", str(exc)[:500])
            print(f"ERRO na coleta: {exc}", file=sys.stderr)
            return 2
        print(f"Coleta: {len(result.ok)} ok, {len(result.failed)} com falha")
        for sym, why in result.failed.items():
            print(f"  ✗ {sym}: {why}", file=sys.stderr)

    with db.connect() as conn:
        removed = purge(conn, today)
        recalc_variations(conn)
        conn.execute("ANALYZE")
        last = db.last_dates(conn)
    print(f"Limpeza: {removed} registro(s) com mais de {KEEP_DAYS} dias removido(s)")

    problems = health.check(last, today)
    status = "Sucesso"
    if problems:
        print("Saúde do pipeline: PROBLEMAS", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        status = "Erro"
    else:
        print("Saúde do pipeline: ok (todos os ativos e indicadores atualizados)")

    if not args.no_export:
        try:
            with db.connect() as conn:
                docs = export.build(conn)
            export.write(docs)
        except Exception as exc:  # noqa: BLE001 — falha clara; os JSON anteriores ficam intactos
            with db.connect() as conn:
                db.log_update(conn, "Erro", f"export: {exc}"[:500])
            print(f"ERRO no export (JSON anteriores mantidos): {exc}", file=sys.stderr)
            return 3
        print(f"Export: {len(docs)} arquivos JSON em {export.OUT_DIR}")

    details = (f"{len(result.ok)} séries coletadas, {len(result.failed)} falhas, "
               f"{len(problems)} alertas de saúde, {time.time() - t0:.1f}s")
    with db.connect() as conn:
        db.log_update(conn, status, details)
    print(details)

    if problems and not args.no_health:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
