"""CDI e IPCA acumulados (referências do gráfico de desempenho da carteira)."""

from datetime import date, timedelta

import pytest

from pipeline.metrics import cdi_index, ipca_index


def business_days(start: date, n: int) -> list[str]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d += timedelta(days=1)
    return out


def test_cdi_10pct_for_252_business_days_gives_10pct():
    days = business_days(date(2026, 1, 5), 253)  # dia-base + 252 dias úteis
    cdi = [(d, 10.0) for d in days]
    idx = cdi_index(days, cdi)
    assert idx[0] == 100.0
    assert idx[-1] == pytest.approx(110.0, rel=1e-9)


def test_cdi_holiday_inside_history_does_not_accrue():
    dates = ["2026-11-18", "2026-11-19", "2026-11-20", "2026-11-23"]
    cdi = [("2026-11-18", 13.65), ("2026-11-19", 13.65), ("2026-11-23", 13.65)]  # 20/11 feriado
    f = (1 + 13.65 / 100) ** (1 / 252)
    assert cdi_index(dates, cdi) == pytest.approx([100, 100 * f, 100 * f, 100 * f**2])


def test_cdi_unpublished_recent_weekdays_use_last_rate():
    dates = ["2026-11-19", "2026-11-24"]  # 20 (sex), 23 (seg), 24 (ter) sem taxa publicada
    cdi = [("2026-11-19", 13.65)]
    f = (1 + 13.65 / 100) ** (1 / 252)
    assert cdi_index(dates, cdi)[-1] == pytest.approx(100 * f**3)


def test_cdi_aligned_with_weekend_dates_stays_flat_on_weekend():
    dates = ["2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23"]  # sex, sáb, dom, seg
    cdi = [("2026-11-20", 12.0), ("2026-11-23", 12.0)]
    idx = cdi_index(dates, cdi)
    assert idx[1] == idx[2] == idx[0]
    assert idx[3] > idx[2]


def test_ipca_full_month_compounds_to_monthly_rate():
    dates = ["2026-08-31", "2026-09-30"]  # base no último dia de agosto → setembro inteiro
    idx = ipca_index(dates, [("2026-09-01", 1.0)])
    assert idx[-1] == pytest.approx(101.0, rel=1e-9)


def test_ipca_pro_rata_half_month():
    idx = ipca_index(["2026-09-30", "2026-10-15"], [("2026-10-01", 1.0)])  # 15 de 31 dias
    assert idx[-1] == pytest.approx(100 * 1.01 ** (15 / 31))


def test_ipca_deflation_month_lowers_index():
    idx = ipca_index(["2026-07-31", "2026-08-31"], [("2026-08-01", -0.32)])
    assert idx[-1] == pytest.approx(99.68, rel=1e-9)


def test_ipca_unpublished_month_uses_last_known():
    # novembro ainda não divulgado → usa outubro (0,14%)
    idx = ipca_index(["2026-10-31", "2026-11-30"], [("2026-10-01", 0.14)])
    assert idx[-1] == pytest.approx(100.14, rel=1e-9)
