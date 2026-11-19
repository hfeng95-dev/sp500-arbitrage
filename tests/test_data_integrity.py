"""Integrity and historical evaluator tests for data_loader.py and historic_evaluator.py."""

from data_loader import (
    CURRENT_FEEDER_CANDIDATES,
    CURRENT_VULNERABLE_CONSTITUENTS,
    HISTORICAL_REBALANCES,
    validate_dataset_integrity,
)
from historic_evaluator import HistoricArbitrageEvaluator
from sp500_engine import SP500RebalanceEngine


def test_dataset_integrity_passes_with_zero_errors():
    report = validate_dataset_integrity(raise_on_error=True)
    assert report["is_valid"] is True
    assert report["error_count"] == 0
    assert report["errors"] == []
    assert report["quarters_checked"] == 13


def test_current_pools_have_no_already_included_or_already_deleted_stocks():
    live_add_tickers = {c["ticker"] for c in CURRENT_FEEDER_CANDIDATES}
    live_del_tickers = {c["ticker"] for c in CURRENT_VULNERABLE_CONSTITUENTS}

    already_included = {"APO", "APP", "COIN", "VRT", "WSM", "HOOD", "RDDT", "FICO"}
    already_deleted = {"VFC", "FOX", "DFS", "HES", "MHK", "FRT", "SEDG", "WHR"}

    assert live_add_tickers.isdisjoint(already_included)
    assert live_del_tickers.isdisjoint(already_deleted)
    assert live_add_tickers.isdisjoint(live_del_tickers)


def test_no_duplicate_historical_deletions_for_sedg_or_whr():
    del_counts = {}
    for meta in HISTORICAL_REBALANCES.values():
        for d in meta["actual_deletions"]:
            del_counts[d["ticker"]] = del_counts.get(d["ticker"], 0) + 1

    assert del_counts.get("SEDG", 0) == 1
    assert del_counts.get("WHR", 0) == 1
    assert all(cnt == 1 for cnt in del_counts.values())


def test_evaluator_era_thresholds_and_none_date_guard():
    assert HistoricArbitrageEvaluator.get_pit_cap_threshold("Q3 2023") == 14.5
    assert HistoricArbitrageEvaluator.get_pit_cap_threshold("Q1 2024") == 15.8
    assert HistoricArbitrageEvaluator.get_pit_cap_threshold("Q4 2024") == 18.0
    assert HistoricArbitrageEvaluator.get_pit_cap_threshold("Q1 2025") == 20.5
    assert HistoricArbitrageEvaluator.get_pit_cap_threshold("Q3 2025") == 22.7
    assert HistoricArbitrageEvaluator.get_pit_cap_threshold("Q3 2026") == 22.7

    # None date guard must return False without raising TypeError
    assert HistoricArbitrageEvaluator._check_dates_valid(None, None, None) is False
    missing_q = HistoricArbitrageEvaluator.evaluate_quarter("Q9 2099")
    assert missing_q["dates_valid"] is False


def test_full_historical_audit_reports_precision_mrr_and_caveats():
    audit = HistoricArbitrageEvaluator.run_full_historical_audit()
    assert audit["weights_used"] == SP500RebalanceEngine.DEFAULT_WEIGHTS
    assert audit["all_integrity_checks_passed"] is True
    assert audit["all_dates_valid"] is True
    assert audit["total_quarters_tested"] == 13
    assert 0.0 < audit["mean_add_mrr"] <= 1.0
    assert 0.0 < audit["mean_del_mrr"] <= 1.0
    assert "%" in audit["composite_add_precision_top_5"]
    assert "%" in audit["composite_del_precision_top_5"]
    assert "pool" in audit["small_pool_caveat"].lower()


def test_walk_forward_expanding_window_validation():
    wf = HistoricArbitrageEvaluator.optimize_and_tune_loop(target_rating=9.0, min_train_quarters=4)
    assert wf["validation_method"] == "expanding_window_walk_forward"
    assert wf["folds_evaluated"] == 9  # 13 quarters - 4 warm-up quarters
    assert len(wf["walk_forward_folds"]) == 9

    # Verify expanding training window size grows strictly by 1 each fold
    train_counts = [f["train_quarters_count"] for f in wf["walk_forward_folds"]]
    assert train_counts == list(range(4, 13))
    assert 0.0 <= wf["oos_avg_score"] <= 10.0
    assert 0.0 <= wf["oos_mean_add_mrr"] <= 1.0
