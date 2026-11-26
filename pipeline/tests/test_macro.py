"""Juro real Brasil × EUA e inflação × meta (macro.json) + parse das fontes dos EUA."""

import pytest

from pipeline import macro, us


def test_fisher_matches_known_values():
    # números de 24/11/2026: SELIC 13,75% e IPCA 12m 4,63%; EFFR 3,88% e CPI 12m 3,74%
    assert macro.fisher(13.75, 4.63) == pytest.approx(8.716, abs=1e-3)
    assert macro.fisher(3.88, 3.74) == pytest.approx(0.135, abs=1e-3)
    assert macro.fisher(10, 0) == pytest.approx(10)


def test_month_helpers():
    assert macro.month_end("2026-02-01") == "2026-02-28"
    assert macro.shift_months("2026-01-01", -12) == "2025-01-01"
    assert macro.shift_months("2026-01-01", -1) == "2025-12-01"
    s = [("2026-09-10", 13.75), ("2026-09-20", 14.0)]
    assert macro.value_at_or_before(s, "2026-09-30") == 14.0
    assert macro.value_at_or_before(s, "2026-09-15") == 13.75
    assert macro.value_at_or_before(s, "2026-09-01") is None


def test_cpi_12m_requires_both_months():
    cpi = {"2025-09-01": 100.0, "2026-09-01": 103.74, "2026-10-01": 104.0}  # out/2025 ausente
    assert macro.cpi_12m(cpi, "2026-09-01") == pytest.approx(3.74)
    assert macro.cpi_12m(cpi, "2026-10-01") is None


def months(start: str, n: int) -> list[str]:
    return [macro.shift_months(start, k) for k in range(n)]


def test_real_rates_latest_and_us_gap():
    ms = months("2024-11-01", 24)  # nov/2024 … out/2026
    selic = [(macro.month_end(m), 13.75) for m in ms]
    ipca12 = [(m, 4.63) for m in ms]
    effr = [(macro.month_end(m), 3.88) for m in ms]
    cpi = {m: 100 * 1.0374 ** (k / 12) for k, m in enumerate(months("2023-11-01", 36))}
    cpi.pop("2025-10-01")  # a BLS não publicou out/2025
    out = macro.real_rates(selic, ipca12, effr, cpi)
    assert out["br"]["month"] == "2026-10-01" and out["br"]["real"] == pytest.approx(8.716, abs=1e-3)
    assert out["us"]["month"] == "2026-09-01"  # out/2026 sem CPI 12m (base out/2025 ausente)
    assert "2025-10-01" in out["usGaps"] and "2026-10-01" in out["usGaps"]
    row = dict((m, (br, u)) for m, br, u in out["series"])
    assert row["2026-10-01"][1] is None and row["2026-10-01"][0] is not None
    assert len(out["series"]) == 24


def test_real_rates_uses_rate_in_force_at_month_end():
    # SELIC cortada no meio do mês: vale a taxa vigente no último dia
    selic = [("2026-09-01", 15.0), ("2026-09-17", 14.25)]
    out = macro.real_rates(selic, [("2026-09-01", 5.0)], [("2026-09-30", 4.0)], {"2025-09-01": 100.0, "2026-09-01": 103.0}, months=1)
    assert out["br"]["nominal"] == 14.25


def test_inflation_target():
    s = [(m, 4.0) for m in months("2024-01-01", 30)]
    t = macro.inflation_target(s)
    assert (t["center"], t["lower"], t["upper"]) == (3.0, 1.5, 4.5)
    assert len(t["series"]) == 24 and t["latest"]["month"] == "2026-06-01"
    with pytest.raises(RuntimeError):
        macro.inflation_target(s[:5])


def test_parse_us_sources():
    effr = {"refRates": [{"effectiveDate": "2026-11-24", "type": "EFFR", "percentRate": 3.88}, {"effectiveDate": "x", "type": "OBFR", "percentRate": 3.8}]}
    assert us.parse_effr(effr) == [("2026-11-24", "effr", 3.88)]
    bls = {"status": "REQUEST_SUCCEEDED", "Results": {"series": [{"data": [
        {"year": "2026", "period": "M10", "value": "337.511"},
        {"year": "2025", "period": "M10", "value": "-"},
        {"year": "2025", "period": "M13", "value": "330.0"},
    ]}]}}
    assert us.parse_cpi(bls) == [("2026-10-01", "cpi", 337.511)]
    with pytest.raises(ValueError):
        us.parse_cpi({"status": "REQUEST_NOT_PROCESSED"})
