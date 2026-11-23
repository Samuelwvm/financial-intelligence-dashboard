import math
from statistics import stdev

import pytest

from pipeline.metrics import align_ffill, base100, daily_change, period_stats, period_window, volatility

# Pregões de seg a sex (sem sábado/domingo), como uma ação.
STOCK = [
    ("2026-01-01", 100.0), ("2026-01-02", 102.0),
    ("2026-01-05", 101.0), ("2026-01-06", 104.0), ("2026-01-07", 103.0),
    ("2026-01-08", 106.0), ("2026-01-09", 108.0),
    ("2026-01-12", 107.0), ("2026-01-13", 110.0),
]


def test_daily_change_is_last_vs_previous_trading_day():
    assert daily_change(STOCK) == pytest.approx((110 / 107 - 1) * 100)
    assert daily_change(STOCK[:1]) == 0.0


def test_window_uses_calendar_days_and_base_on_or_before_start():
    # último = 13/01; 7 dias -> início 06/01; base = último preço com data <= 06/01
    w = period_window(STOCK, 7)
    assert w[0] == ("2026-01-06", 104.0)
    assert w[-1] == ("2026-01-13", 110.0)


def test_window_base_falls_back_to_previous_trading_day():
    # 10 dias -> início 03/01 (sábado): base = sexta 02/01
    assert period_window(STOCK, 10)[0] == ("2026-01-02", 102.0)


def test_window_longer_than_history_uses_first_point():
    assert period_window(STOCK, 365)[0] == STOCK[0]


def test_period_return_matches_base100_last_point():
    st = period_stats(STOCK, "7d")
    assert st.ret == pytest.approx((110 / 104 - 1) * 100)
    b = base100(st.points)
    assert b[0][1] == pytest.approx(100.0)
    assert b[-1][1] - 100 == pytest.approx(st.ret)


def test_today_period_return_is_daily_change_with_7d_chart():
    st = period_stats(STOCK, "1d")
    assert st.ret == pytest.approx(daily_change(STOCK))
    assert st.points == period_window(STOCK, 7)


def test_volatility_is_sample_std_annualized_252():
    pts = period_window(STOCK, 7)
    prices = [p for _, p in pts]
    rets = [prices[i] / prices[i - 1] - 1 for i in range(1, len(prices))]
    assert volatility(pts) == pytest.approx(stdev(rets) * math.sqrt(252) * 100)
    assert volatility(pts[:2]) == 0.0  # um único retorno: indefinido -> 0 (como a V1)


def test_high_low_within_window():
    st = period_stats(STOCK, "7d")
    assert (st.high, st.low) == (110.0, 103.0)


def test_align_ffill_union_of_dates():
    dates, cols = align_ffill({"a": [("d1", 100.0), ("d3", 110.0)], "b": [("d2", 100.0), ("d3", 90.0)]})
    assert dates == ["d1", "d2", "d3"]
    assert cols["a"] == [100.0, 100.0, 110.0]
    assert cols["b"] == [None, 100.0, 90.0]
