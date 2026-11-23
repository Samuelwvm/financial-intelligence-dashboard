"""Acesso ao SQLite (fonte da verdade dos dados)."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "data" / "finance.db"
SCHEMA = Path(__file__).with_name("schema.sql")


def db_path() -> Path:
    return Path(os.environ.get("RADAR_DB_PATH", DEFAULT_DB))


@contextmanager
def connect(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Conexão com commit no sucesso e rollback em qualquer erro."""
    p = path or db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))


def upsert_metadata(conn: sqlite3.Connection, rows: Iterable[tuple[str, str, str, str]]) -> None:
    conn.executemany(
        """
        INSERT INTO assets_metadata (symbol, name, category, sector) VALUES (?, ?, ?, ?)
        ON CONFLICT(symbol) DO UPDATE SET
            name = excluded.name, category = excluded.category, sector = excluded.sector
        """,
        rows,
    )


def upsert_prices(conn: sqlite3.Connection, symbol: str, rows: Iterable[tuple[str, float]]) -> int:
    """Grava (date, price) com upsert: corrige o dia gravado antes do fechamento
    e regrava o histórico com o ajuste atual da fonte (auditoria §2.3)."""
    data = [(d, symbol, float(p)) for d, p in rows]
    conn.executemany(
        """
        INSERT INTO assets_history (date, symbol, price, variation) VALUES (?, ?, ?, 0.0)
        ON CONFLICT(date, symbol) DO UPDATE SET price = excluded.price
        """,
        data,
    )
    return len(data)


def log_update(conn: sqlite3.Connection, status: str, details: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO update_logs (date, status, details) VALUES (?, ?, ?)", (now, status, details))


def price_series(conn: sqlite3.Connection, symbol: str) -> list[tuple[str, float]]:
    return conn.execute(
        "SELECT date, price FROM assets_history WHERE symbol = ? ORDER BY date", (symbol,)
    ).fetchall()


def last_dates(conn: sqlite3.Connection) -> dict[str, str]:
    return dict(conn.execute("SELECT symbol, MAX(date) FROM assets_history GROUP BY symbol").fetchall())
