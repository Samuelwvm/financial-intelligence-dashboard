"""Métricas da V2 — fórmulas da V1 com a janela corrigida (auditoria §3.3 e §5).

Funções puras sobre listas (date ISO, price), ordenadas por data.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from statistics import stdev

# Rótulo do período -> dias corridos. "1d" = "Hoje" (variação do último pregão;
# gráfico, volatilidade e máx/mín na janela de 7 dias, como o gráfico da V1).
PERIODS: dict[str, int] = {"1d": 7, "7d": 7, "30d": 30, "90d": 90, "1y": 365}
ANNUALIZATION = 252  # V1: √252 para todos os ativos

Series = list[tuple[str, float]]


@dataclass(frozen=True)
class PeriodStats:
    ret: float          # retorno no período, em %
    vol: float          # volatilidade anualizada, em %
    high: float
    low: float
    base: float         # preço-base do período (= 100 no base 100)
    points: Series      # série do período, começando pelo preço-base


def daily_change(series: Series) -> float:
    """Variação do último pregão em % (a `variation` da V1)."""
    if len(series) < 2:
        return 0.0
    return (series[-1][1] / series[-2][1] - 1) * 100


def period_window(series: Series, days: int) -> Series:
    """Preço-base (último preço com data <= início) + preços com data > início."""
    if not series:
        return []
    last = date.fromisoformat(series[-1][0])
    start = (last - timedelta(days=days)).isoformat()
    base_idx = 0
    for i, (d, _) in enumerate(series):
        if d <= start:
            base_idx = i
        else:
            break
    return series[base_idx:]


def volatility(points: Series) -> float:
    """std amostral dos retornos diários × √252 × 100 (V1)."""
    prices = [p for _, p in points]
    rets = [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]
    if len(rets) < 2:
        return 0.0
    v = stdev(rets) * math.sqrt(ANNUALIZATION) * 100
    return 0.0 if math.isnan(v) else v


def period_stats(series: Series, period: str) -> PeriodStats:
    points = period_window(series, PERIODS[period])
    if len(points) < 2:
        p = points[-1][1] if points else 0.0
        return PeriodStats(0.0, 0.0, p, p, p, points)
    base = points[0][1]
    last = points[-1][1]
    ret = daily_change(series) if period == "1d" else (last / base - 1) * 100
    prices = [p for _, p in points]
    return PeriodStats(ret, volatility(points), max(prices), min(prices), base, points)


def base100(points: Series) -> list[tuple[str, float]]:
    if not points:
        return []
    base = points[0][1]
    return [(d, p / base * 100) for d, p in points]


def align_ffill(columns: dict[str, list[tuple[str, float]]]) -> tuple[list[str], dict[str, list[float | None]]]:
    """Alinha várias séries por data (união) com preenchimento para a frente.
    Antes do primeiro ponto de uma série o valor é None."""
    dates = sorted({d for col in columns.values() for d, _ in col})
    out: dict[str, list[float | None]] = {}
    for key, col in columns.items():
        lookup = dict(col)
        cur: float | None = None
        vals: list[float | None] = []
        for d in dates:
            if d in lookup:
                cur = lookup[d]
            vals.append(cur)
        out[key] = vals
    return dates, out
