"""Unit tests for sp500_engine.py (weights, thresholds, log cap scaling, official rules, deletion scoring)."""

import math

from sp500_engine import SP500RebalanceEngine


def _base_candidate(**overrides):
    cand = {
        "ticker": "TEST",
        "name": "Test Corp",
        "sector": "Industrials",
        "mkt_cap_b": 35.0,
        "fmc_b": 30.0,
        "iwf": 0.86,
        "gaap_4q_pos": True,
        "gaap_q0_pos": True,
        "liq_ratio": 1.25,
        "min_monthly_vol": 1_500_000,
        "ipo_months": 48,
        "feeder": "S&P MidCap 400",
        "us_domicile": True,
    }
    cand.update(overrides)
    return cand


def test_default_weights_unified_35_35_15_15():
    assert SP500RebalanceEngine.DEFAULT_WEIGHTS == {
        "mkt_cap": 0.35,
        "feeder_midcap": 0.35,
        "liquidity": 0.15,
        "sector_representation": 0.15,
    }
    assert math.isclose(sum(SP500RebalanceEngine.DEFAULT_WEIGHTS.values()), 1.0)


def test_era_cap_thresholds_and_default():
    assert SP500RebalanceEngine.DEFAULT_MKT_CAP_THRESHOLD_B == 22.7
    assert SP500RebalanceEngine.get_era_cap_threshold("Q3 2023") == 14.5
    assert SP500RebalanceEngine.get_era_cap_threshold("Q4 2023") == 14.5
    assert SP500RebalanceEngine.get_era_cap_threshold("Q1 2024") == 15.8
    assert SP500RebalanceEngine.get_era_cap_threshold("Q2 2024") == 15.8
    assert SP500RebalanceEngine.get_era_cap_threshold("Q3 2024") == 18.0
    assert SP500RebalanceEngine.get_era_cap_threshold("Q4 2024") == 18.0
    assert SP500RebalanceEngine.get_era_cap_threshold("Q1 2025") == 20.5
    assert SP500RebalanceEngine.get_era_cap_threshold("Q2 2025") == 20.5
    assert SP500RebalanceEngine.get_era_cap_threshold("Q3 2025") == 22.7
    assert SP500RebalanceEngine.get_era_cap_threshold("Q3 2026") == 22.7


def test_log_scaled_market_cap_is_strictly_concave():
    threshold = 22.7
    s1 = SP500RebalanceEngine._compute_log_cap_score(threshold, threshold)
    s2 = SP500RebalanceEngine._compute_log_cap_score(threshold * 2, threshold)
    s4 = SP500RebalanceEngine._compute_log_cap_score(threshold * 4, threshold)
    s_top = SP500RebalanceEngine._compute_log_cap_score(150.0, threshold)

    assert math.isclose(s1, 40.0, rel_tol=1e-6)
    assert math.isclose(s_top, 100.0, rel_tol=1e-6)
    # Logarithmic property: equal multiplicative ratios produce equal score increments
    assert math.isclose(s2 - s1, s4 - s2, rel_tol=1e-6)
    assert s2 > s1 and s4 > s2


def test_fail_closed_defaults_on_missing_core_fields():
    # Missing liq_ratio must fail closed (not default to 1.0)
    no_liq = _base_candidate()
    del no_liq["liq_ratio"]
    res_liq = SP500RebalanceEngine.evaluate_addition_candidate(no_liq)
    assert res_liq["is_eligible"] is False
    assert res_liq["passed_liq"] is False

    # Missing us_domicile must fail closed (not default to True)
    no_dom = _base_candidate()
    del no_dom["us_domicile"]
    res_dom = SP500RebalanceEngine.evaluate_addition_candidate(no_dom)
    assert res_dom["is_eligible"] is False
    assert res_dom["passed_domicile"] is False


def test_official_sp500_rules_enforced():
    # Baseline passes
    ok = SP500RebalanceEngine.evaluate_addition_candidate(_base_candidate())
    assert ok["is_eligible"] is True
    assert ok["fail_reasons"] == []

    # FMC < 0.5 * 22.7 = 11.35 fails
    bad_fmc = SP500RebalanceEngine.evaluate_addition_candidate(_base_candidate(fmc_b=10.0))
    assert bad_fmc["is_eligible"] is False
    assert bad_fmc["passed_fmc"] is False

    # IWF < 0.10 fails
    bad_iwf = SP500RebalanceEngine.evaluate_addition_candidate(_base_candidate(iwf=0.08))
    assert bad_iwf["is_eligible"] is False
    assert bad_iwf["passed_iwf"] is False

    # 6-month min monthly volume < 250,000 fails
    bad_vol = SP500RebalanceEngine.evaluate_addition_candidate(_base_candidate(min_monthly_vol=200_000))
    assert bad_vol["is_eligible"] is False
    assert bad_vol["passed_volume"] is False

    # IPO seasoning < 12 months fails
    bad_ipo = SP500RebalanceEngine.evaluate_addition_candidate(_base_candidate(ipo_months=9))
    assert bad_ipo["is_eligible"] is False
    assert bad_ipo["passed_ipo"] is False

    # GAAP 4Q sum <= 0 uses accurate phrasing (not "consecutive")
    bad_gaap = SP500RebalanceEngine.evaluate_addition_candidate(_base_candidate(gaap_4q_pos=False))
    assert bad_gaap["is_eligible"] is False
    assert any("4Q sum <= 0" in r for r in bad_gaap["fail_reasons"])


def test_deletion_scoring_uses_rank_bottom_and_reaches_high_risk_up_to_95():
    # M&A pending -> 98.0 CERTAIN
    ma = SP500RebalanceEngine.evaluate_deletion_candidate(
        {"ticker": "K", "mkt_cap_b": 28.5, "neg_earnings_streak": 0, "rank_bottom": 95, "ma_pending": True, "acquirer": "Mars"}
    )
    assert ma["risk_score"] == 98.0
    assert "CERTAIN" in ma["risk_label"]

    # Extreme distress reaches 95.0 cap
    extreme = SP500RebalanceEngine.evaluate_deletion_candidate(
        {"ticker": "DIST", "mkt_cap_b": 4.2, "neg_earnings_streak": 4, "rank_bottom": 1}
    )
    assert extreme["risk_score"] == 95.0
    assert "HIGH RISK" in extreme["risk_label"]

    # Genuine high-risk vulnerable stock (< $7.5B with sustained losses) reaches HIGH RISK (>= 75)
    vuln = SP500RebalanceEngine.evaluate_deletion_candidate(
        {"ticker": "CZR", "mkt_cap_b": 6.4, "neg_earnings_streak": 3, "rank_bottom": 1}
    )
    assert vuln["risk_score"] >= 75.0
    assert "HIGH RISK" in vuln["risk_label"]

    # rank_bottom meaningfully affects risk score when mkt_cap and streak are equal
    bottom_1 = SP500RebalanceEngine.evaluate_deletion_candidate(
        {"ticker": "A", "mkt_cap_b": 8.5, "neg_earnings_streak": 1, "rank_bottom": 1}
    )
    bottom_40 = SP500RebalanceEngine.evaluate_deletion_candidate(
        {"ticker": "B", "mkt_cap_b": 8.5, "neg_earnings_streak": 1, "rank_bottom": 40}
    )
    assert bottom_1["risk_score"] > bottom_40["risk_score"] + 10.0
