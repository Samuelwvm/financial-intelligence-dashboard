"""Coleta: Yahoo Finance (preços) e Banco Central do Brasil (indicadores).

Diferenças em relação à V1 (auditoria §1.5 e §2):
- retry com backoff exponencial em cada fonte;
- nada de `except: print` — falhas são devolvidas e o pipeline decide;
- sempre busca a janela inteira (400 dias) e grava com upsert: o mesmo número
  de requisições da V1, mas recupera dias perdidos e corrige preços parciais;
- linhas sem fechamento (NaN) são descartadas, em vez de abortar o ativo.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Callable

import requests

HISTORY_DAYS = 400  # mesma retenção da V1 (cleaners.purge_old_records)
RETRIES = 3
BACKOFF_SECONDS = 2.0


class CollectError(RuntimeError):
    pass


@dataclass
class CollectResult:
    ok: dict[str, int] = field(default_factory=dict)       # símbolo -> linhas gravadas
    failed: dict[str, str] = field(default_factory=dict)   # símbolo -> motivo


def with_retry(fn: Callable[[], list[tuple[str, float]]], label: str,
               retries: int = RETRIES, backoff: float = BACKOFF_SECONDS,
               sleep: Callable[[float], None] = time.sleep) -> list[tuple[str, float]]:
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            rows = fn()
            if not rows:
                raise CollectError(f"{label}: resposta vazia")
            return rows
        except Exception as exc:  # noqa: BLE001 — qualquer falha conta como tentativa
            last = exc
            if attempt < retries:
                sleep(backoff * 2 ** (attempt - 1))
    raise CollectError(f"{label}: falhou após {retries} tentativas ({last})")


def clean_rows(rows: list[tuple[str, float]], today: date) -> list[tuple[str, float]]:
    """Remove NaN, valores não positivos e datas futuras."""
    out = []
    for d, p in rows:
        if p is None or (isinstance(p, float) and math.isnan(p)) or p <= 0:
            continue
        if date.fromisoformat(d) > today:
            continue
        out.append((d, float(p)))
    return out


def fetch_yahoo(symbol: str, start: date) -> list[tuple[str, float]]:
    import yfinance as yf  # import tardio: os testes não precisam do yfinance

    df = yf.Ticker(symbol).history(start=start.isoformat(), auto_adjust=True)
    if df is None or df.empty:
        return []
    return [(idx.strftime("%Y-%m-%d"), float(v)) for idx, v in df["Close"].items()]


def _bcb_get(url: str) -> list[tuple[str, float]]:
    # O BCB às vezes responde 304 com corpo vazio (cache intermediário): exigimos 200 e pedimos no-cache.
    resp = requests.get(url, timeout=20, headers={"Accept": "application/json", "Cache-Control": "no-cache"})
    if resp.status_code != 200 or not resp.content:
        raise CollectError(f"BCB: HTTP {resp.status_code}, {len(resp.content)} bytes")
    data = resp.json()
    if not isinstance(data, list):
        raise CollectError("BCB: formato inesperado")
    rows = []
    for item in data:
        d, m, y = item["data"].split("/")
        rows.append((f"{y}-{m}-{d}", float(str(item["valor"]).replace(",", "."))))
    return rows


def fetch_bcb(code: int, start: date, end: date) -> list[tuple[str, float]]:
    """Janela inteira por datas; se o BCB falhar, cai para os últimos 20 valores
    (suficiente para séries mensais e, nas diárias, o upsert preserva o histórico)."""
    base = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"
    try:
        return _bcb_get(f"{base}?formato=json&dataInicial={start:%d/%m/%Y}&dataFinal={end:%d/%m/%Y}")
    except Exception:  # noqa: BLE001
        return _bcb_get(f"{base}/ultimos/20?formato=json")


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def window_start(today: date) -> date:
    return today - timedelta(days=HISTORY_DAYS)
