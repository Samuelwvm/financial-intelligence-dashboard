"""Juro real no mundo (BIS) e inflação × meta (macro.json)."""

import pytest

from pipeline import bis, macro


def test_fisher_matches_known_values():
    # BIS set/2026: Brasil 13,75% e 4,576%; EUA 3,875% e 3,738%
    assert macro.fisher(13.75, 4.576) == pytest.approx(8.772, abs=1e-3)
    assert macro.fisher(3.875, 3.738) == pytest.approx(0.132, abs=1e-3)
    assert macro.fisher(10, 0) == pytest.approx(10)


def test_shift_months():
    assert macro.shift_months("2026-01-01", -12) == "2025-01-01"
    assert macro.shift_months("2026-01-01", -1) == "2025-12-01"


def months(start: str, n: int) -> list[str]:
    return [macro.shift_months(start, k) for k in range(n)]


def full(value_policy=5.0, value_cpi=3.0, n=30, start="2024-04-01"):
    ms = months(start, n)
    policy = {c: {m: value_policy for m in ms} for c in bis.COUNTRIES}
    cpi = {c: {m: value_cpi for m in ms} for c in bis.COUNTRIES}
    return policy, cpi


def test_world_ranking_uses_latest_common_month_and_sorts():
    policy, cpi = full()
    policy["BR"] = {m: 13.75 for m in policy["BR"]}
    policy["IN"].pop("2026-09-01")  # a Índia ainda não tem a taxa de set/26
    out = macro.world_real_rates(policy, cpi)
    assert out["month"] == "2026-08-01"  # último mês que TODOS têm
    assert out["ranking"][0]["code"] == "BR"
    reals = [r["real"] for r in out["ranking"]]
    assert reals == sorted(reals, reverse=True)
    assert len(out["series"]["US"]) == 24 and out["series"]["US"][-1][0] == "2026-08-01"


def test_world_requires_every_country():
    policy, cpi = full()
    del policy["CL"]
    with pytest.raises(RuntimeError, match="CL"):
        macro.world_real_rates(policy, cpi)


def test_inflation_target():
    s = [(m, 4.0) for m in months("2024-01-01", 30)]
    t = macro.inflation_target(s)
    assert (t["center"], t["lower"], t["upper"]) == (3.0, 1.5, 4.5)
    assert len(t["series"]) == 24 and t["latest"]["month"] == "2026-06-01"
    with pytest.raises(RuntimeError):
        macro.inflation_target(s[:5])


def test_parse_bis_csv():
    text = (
        "FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE\n"
        "M,BR,2026-09,13.75\n"
        "M,US,2026-09,3.875\n"
        "M,XX,2026-09,1.0\n"  # país fora da lista
        "M,MX,2026-09,\n"  # sem valor
        "M,JP,2026-09,NaN\n"
    )
    assert bis.parse_csv(text, "policy") == [("2026-09-01", "policy:BR", 13.75), ("2026-09-01", "policy:US", 3.875)]
    with pytest.raises(ValueError):
        bis.parse_csv("a,b\n1,2\n", "cpi")


def test_bis_urls_cover_all_countries():
    from datetime import date

    url = bis.cpi_url(date(2023, 11, 1))
    assert "WS_LONG_CPI" in url and url.count("+") == len(bis.COUNTRIES) - 1 and ".771/" in url
    assert "startPeriod=2023-11" in url
