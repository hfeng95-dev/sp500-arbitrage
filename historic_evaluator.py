"""
Independent Evaluator Agent & Backtest Engine for S&P 500 Arbitrage
Audits historical quarterly reconstitution decisions against S&P Dow Jones Indices actions.
Uses era-accurate S&P DJI market-cap thresholds, Precision@K, MRR, Recall@K,
dataset integrity verification, small-pool saturation caveats, and expanding-window
walk-forward out-of-sample validation.
"""

from datetime import date
from typing import Dict, Any, List, Optional

from data_loader import (
    get_historical_rebalances,
    get_point_in_time_data,
    validate_dataset_integrity,
)
from sp500_engine import SP500RebalanceEngine


def _quarter_sort_key(quarter_label: str):
    """Parses 'Q3 2023' into (2023, 3) for strict chronological walk-forward ordering."""
    parts = quarter_label.strip().split()
    if len(parts) == 2 and parts[0].startswith("Q"):
        return (int(parts[1]), int(parts[0][1:]))
    return (0, 0)


def _compute_mrr(actual_tickers: List[str], ranked_tickers: List[str]) -> float:
    """Computes Mean Reciprocal Rank (MRR) of actual outcomes within a ranked list."""
    if not actual_tickers:
        return 0.0
    rank_map = {ticker: idx for idx, ticker in enumerate(ranked_tickers, 1)}
    rr_sum = sum(1.0 / rank_map[t] for t in actual_tickers if t in rank_map)
    return round(rr_sum / len(actual_tickers), 3)


class HistoricArbitrageEvaluator:
    """
    Independent Auditor: Evaluates algorithm predictive accuracy across past quarters.
    Calculates Top-3 / Top-5 / Top-10 Recall, Precision@K, and Mean Reciprocal Rank (MRR)
    for both additions and deletions across 3 full years (13 quarters), with transparent
    small-pool caveats and expanding-window walk-forward validation.
    """

    @classmethod
    def get_pit_cap_threshold(cls, quarter: str) -> float:
        """
        Returns the official S&P DJI minimum unadjusted market-cap guideline ($B) for the era:
        - 2023: $14.5B
        - H1 2024: $15.8B
        - H2 2024: $18.0B
        - H1 2025: $20.5B
        - H2 2025+: $22.7B
        """
        return SP500RebalanceEngine.get_era_cap_threshold(quarter)

    @classmethod
    def _check_dates_valid(cls, cutoff: Any, announce: Any, effective: Any) -> bool:
        """Safely validates Cutoff < Announcement < Effective, guarding None or non-date values."""
        if not (isinstance(cutoff, date) and isinstance(announce, date) and isinstance(effective, date)):
            return False
        return bool(cutoff < announce < effective)

    @classmethod
    def evaluate_quarter(
        cls,
        quarter: str,
        weights: Optional[Dict[str, float]] = None,
        mkt_cap_threshold_b: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates a single past quarter strictly using point-in-time frozen metrics
        and era-accurate S&P DJI market-cap thresholds.
        """
        if mkt_cap_threshold_b is None:
            mkt_cap_threshold_b = cls.get_pit_cap_threshold(quarter)

        pit = get_point_in_time_data(quarter)
        meta = pit.get("metadata", {})
        add_candidates = pit.get("addition_candidates", [])
        del_candidates = pit.get("deletion_candidates", [])

        actual_additions = [a["ticker"] for a in meta.get("actual_additions", [])]
        actual_deletions = [d["ticker"] for d in meta.get("actual_deletions", [])]

        # 1. Rank additions using point-in-time data and era threshold
        ranked_additions = SP500RebalanceEngine.rank_addition_candidates(
            add_candidates,
            mkt_cap_threshold_b=mkt_cap_threshold_b,
            weights=weights,
        )
        ranked_add_tickers = [c["ticker"] for c in ranked_additions]

        top_3_add_tickers = ranked_add_tickers[:3]
        top_5_add_tickers = ranked_add_tickers[:5]
        top_10_add_tickers = ranked_add_tickers[:10]

        hits_top_3 = [t for t in actual_additions if t in top_3_add_tickers]
        hits_top_5 = [t for t in actual_additions if t in top_5_add_tickers]
        hits_top_10 = [t for t in actual_additions if t in top_10_add_tickers]

        add_recall_top_3 = len(hits_top_3) / max(1, len(actual_additions))
        add_recall_top_5 = len(hits_top_5) / max(1, len(actual_additions))
        add_recall_top_10 = len(hits_top_10) / max(1, len(actual_additions))

        add_precision_top_3 = len(hits_top_3) / max(1, len(top_3_add_tickers))
        add_precision_top_5 = len(hits_top_5) / max(1, len(top_5_add_tickers))
        add_mrr = _compute_mrr(actual_additions, ranked_add_tickers)

        # 2. Rank deletions using point-in-time data and era threshold
        ranked_deletions = SP500RebalanceEngine.rank_deletion_candidates(
            del_candidates,
            mkt_cap_threshold_b=mkt_cap_threshold_b,
        )
        ranked_del_tickers = [c["ticker"] for c in ranked_deletions]

        top_3_del_tickers = ranked_del_tickers[:3]
        top_5_del_tickers = ranked_del_tickers[:5]

        del_hits_top_3 = [t for t in actual_deletions if t in top_3_del_tickers]
        del_hits_top_5 = [t for t in actual_deletions if t in top_5_del_tickers]

        del_recall_top_3 = len(del_hits_top_3) / max(1, len(actual_deletions))
        del_recall_top_5 = len(del_hits_top_5) / max(1, len(actual_deletions))
        del_precision_top_3 = len(del_hits_top_3) / max(1, len(top_3_del_tickers))
        del_precision_top_5 = len(del_hits_top_5) / max(1, len(top_5_del_tickers))
        del_mrr = _compute_mrr(actual_deletions, ranked_del_tickers)

        # 3. Pool-size & saturation diagnostics
        add_pool_size = len(add_candidates)
        del_pool_size = len(del_candidates)
        add_top5_saturated = add_pool_size <= 5
        add_top10_saturated = add_pool_size <= 10
        del_top5_saturated = del_pool_size <= 5

        caveats: List[str] = []
        if add_top10_saturated:
            caveats.append(f"Addition pool ({add_pool_size}) <= 10: Top-10 recall is trivially 100%")
        if add_top5_saturated:
            caveats.append(f"Addition pool ({add_pool_size}) <= 5: Top-5 recall is trivially 100%")
        if del_top5_saturated:
            caveats.append(f"Deletion pool ({del_pool_size}) <= 5: Top-5 deletion recall is trivially 100%")

        # 4. Overall Quarter Score (0 - 10 scale)
        # 60% weight on addition Top-5 recall, 40% on deletion Top-5 recall
        quarter_accuracy = (add_recall_top_5 * 0.60 + del_recall_top_5 * 0.40) * 10.0
        quarter_score = round(quarter_accuracy, 1)

        cutoff_date = meta.get("cutoff_date")
        announcement_date = meta.get("announcement_date")
        effective_date = meta.get("effective_date")
        time_valid = cls._check_dates_valid(cutoff_date, announcement_date, effective_date)

        return {
            "quarter": quarter,
            "era_cap_threshold_b": mkt_cap_threshold_b,
            "cutoff_date": cutoff_date,
            "announcement_date": announcement_date,
            "effective_date": effective_date,
            "dates_valid": time_valid,
            "add_pool_size": add_pool_size,
            "del_pool_size": del_pool_size,
            "add_top5_saturated": add_top5_saturated,
            "add_top10_saturated": add_top10_saturated,
            "del_top5_saturated": del_top5_saturated,
            "small_pool_caveats": caveats,
            "actual_additions": actual_additions,
            "actual_deletions": actual_deletions,
            "top_3_predicted_additions": top_3_add_tickers,
            "top_5_predicted_additions": top_5_add_tickers,
            "top_3_predicted_deletions": top_3_del_tickers,
            "top_5_predicted_deletions": top_5_del_tickers,
            "addition_hits_top_3": hits_top_3,
            "addition_hits_top_5": hits_top_5,
            "addition_hits_top_10": hits_top_10,
            "deletion_hits_top_3": del_hits_top_3,
            "deletion_hits_top_5": del_hits_top_5,
            "add_recall_top_3": add_recall_top_3,
            "add_recall_top_5": add_recall_top_5,
            "add_recall_top_10": add_recall_top_10,
            "add_precision_top_3": add_precision_top_3,
            "add_precision_top_5": add_precision_top_5,
            "add_mrr": add_mrr,
            "del_recall_top_3": del_recall_top_3,
            "del_recall_top_5": del_recall_top_5,
            "del_precision_top_3": del_precision_top_3,
            "del_precision_top_5": del_precision_top_5,
            "del_mrr": del_mrr,
            "quarter_score": quarter_score,
            "all_ranked_additions": ranked_additions,
            "all_ranked_deletions": ranked_deletions,
        }

    @classmethod
    def run_full_historical_audit(
        cls,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Runs point-in-time audit across all historical quarters (3 full years),
        combining timestamp checks, dataset membership integrity validation,
        Recall@K, Precision@K, MRR, and small-pool saturation transparency.
        """
        used_weights = weights or SP500RebalanceEngine.DEFAULT_WEIGHTS
        quarters = list(get_historical_rebalances().keys())
        integrity_report = validate_dataset_integrity(raise_on_error=False)

        results: List[Dict[str, Any]] = []
        total_score = 0.0

        total_actual_adds = 0
        total_hits_top_3_adds = 0
        total_hits_top_5_adds = 0
        total_hits_top_10_adds = 0
        total_add_top3_slots = 0
        total_add_top5_slots = 0
        sum_add_mrr = 0.0

        total_actual_dels = 0
        total_hits_top_3_dels = 0
        total_hits_top_5_dels = 0
        total_del_top3_slots = 0
        total_del_top5_slots = 0
        sum_del_mrr = 0.0

        saturated_add_top10_quarters = 0
        saturated_del_top5_quarters = 0
        leakage_checks: List[Dict[str, Any]] = []

        for q in quarters:
            q_res = cls.evaluate_quarter(q, weights=used_weights)
            results.append(q_res)
            total_score += q_res["quarter_score"]

            total_actual_adds += len(q_res["actual_additions"])
            total_hits_top_3_adds += len(q_res["addition_hits_top_3"])
            total_hits_top_5_adds += len(q_res["addition_hits_top_5"])
            total_hits_top_10_adds += len(q_res["addition_hits_top_10"])
            total_add_top3_slots += len(q_res["top_3_predicted_additions"])
            total_add_top5_slots += len(q_res["top_5_predicted_additions"])
            sum_add_mrr += q_res["add_mrr"]

            total_actual_dels += len(q_res["actual_deletions"])
            total_hits_top_3_dels += len(q_res["deletion_hits_top_3"])
            total_hits_top_5_dels += len(q_res["deletion_hits_top_5"])
            total_del_top3_slots += len(q_res["top_3_predicted_deletions"])
            total_del_top5_slots += len(q_res["top_5_predicted_deletions"])
            sum_del_mrr += q_res["del_mrr"]

            if q_res["add_top10_saturated"]:
                saturated_add_top10_quarters += 1
            if q_res["del_top5_saturated"]:
                saturated_del_top5_quarters += 1

            time_valid = q_res["dates_valid"]
            leakage_checks.append({
                "quarter": q,
                "cutoff": str(q_res["cutoff_date"]),
                "announce": str(q_res["announcement_date"]),
                "effective": str(q_res["effective_date"]),
                "cutoff_before_announce": time_valid,
                "verified_zero_leakage": time_valid and integrity_report["is_valid"],
            })

        n_q = max(1, len(quarters))
        avg_score = round(total_score / n_q, 1)

        composite_add_recall_top_3 = round(total_hits_top_3_adds / max(1, total_actual_adds) * 100, 1)
        composite_add_recall_top_5 = round(total_hits_top_5_adds / max(1, total_actual_adds) * 100, 1)
        composite_add_recall_top_10 = round(total_hits_top_10_adds / max(1, total_actual_adds) * 100, 1)
        composite_add_precision_top_3 = round(total_hits_top_3_adds / max(1, total_add_top3_slots) * 100, 1)
        composite_add_precision_top_5 = round(total_hits_top_5_adds / max(1, total_add_top5_slots) * 100, 1)
        mean_add_mrr = round(sum_add_mrr / n_q, 3)

        composite_del_recall_top_3 = round(total_hits_top_3_dels / max(1, total_actual_dels) * 100, 1)
        composite_del_recall_top_5 = round(total_hits_top_5_dels / max(1, total_actual_dels) * 100, 1)
        composite_del_precision_top_3 = round(total_hits_top_3_dels / max(1, total_del_top3_slots) * 100, 1)
        composite_del_precision_top_5 = round(total_hits_top_5_dels / max(1, total_del_top5_slots) * 100, 1)
        mean_del_mrr = round(sum_del_mrr / n_q, 3)

        all_dates_valid = all(chk["cutoff_before_announce"] for chk in leakage_checks)
        all_integrity_passed = all_dates_valid and integrity_report["is_valid"]

        avg_add_pool = round(sum(r["add_pool_size"] for r in results) / n_q, 1)
        avg_del_pool = round(sum(r["del_pool_size"] for r in results) / n_q, 1)

        small_pool_summary = (
            f"Curated PIT pool sizes average {avg_add_pool} addition contenders and {avg_del_pool} deletion contenders per quarter. "
            f"Top-10 addition recall is pool-saturated in {saturated_add_top10_quarters}/{len(quarters)} quarters "
            f"and Top-5 deletion recall is pool-saturated in {saturated_del_top5_quarters}/{len(quarters)} quarters. "
            f"Use Precision@K and MRR (Add MRR={mean_add_mrr:.3f}, Del MRR={mean_del_mrr:.3f}) for non-saturated ranking quality."
        )

        is_high_accuracy = (avg_score >= 8.5) and all_integrity_passed

        return {
            "weights_used": dict(used_weights),
            "evaluation_rating": f"{avg_score}/10",
            "numeric_rating": avg_score,
            "is_high_accuracy": is_high_accuracy,
            "total_quarters_tested": len(quarters),
            "quarters_evaluated": quarters,
            "composite_add_recall_top_3": f"{composite_add_recall_top_3}%",
            "composite_add_recall_top_5": f"{composite_add_recall_top_5}%",
            "composite_add_recall_top_10": f"{composite_add_recall_top_10}%",
            "composite_add_precision_top_3": f"{composite_add_precision_top_3}%",
            "composite_add_precision_top_5": f"{composite_add_precision_top_5}%",
            "mean_add_mrr": mean_add_mrr,
            "composite_del_recall_top_3": f"{composite_del_recall_top_3}%",
            "composite_del_recall_top_5": f"{composite_del_recall_top_5}%",
            "composite_del_precision_top_3": f"{composite_del_precision_top_3}%",
            "composite_del_precision_top_5": f"{composite_del_precision_top_5}%",
            "mean_del_mrr": mean_del_mrr,
            "avg_add_pool_size": avg_add_pool,
            "avg_del_pool_size": avg_del_pool,
            "saturated_add_top10_quarters": saturated_add_top10_quarters,
            "saturated_del_top5_quarters": saturated_del_top5_quarters,
            "small_pool_caveat": small_pool_summary,
            "all_dates_valid": all_dates_valid,
            "all_integrity_checks_passed": all_integrity_passed,
            "dataset_integrity": integrity_report,
            "quarterly_results": results,
            "leakage_audit": leakage_checks,
        }

    @classmethod
    def optimize_and_tune_loop(
        cls,
        target_rating: float = 9.0,
        min_train_quarters: int = 4,
    ) -> Dict[str, Any]:
        """
        Expanding-window walk-forward validation (strictly chronological):
        For each held-out quarter `t` starting at `min_train_quarters`, selects the best
        weight vector using ONLY prior quarters `[0 .. t-1]` (ranked by composite training
        objective: MRR + Top-5 Precision + Top-5 Recall), then evaluates out-of-sample on `t`.
        """
        weight_candidates = [
            dict(SP500RebalanceEngine.DEFAULT_WEIGHTS),  # 35/35/15/15 canonical default
            {"mkt_cap": 0.40, "feeder_midcap": 0.30, "liquidity": 0.15, "sector_representation": 0.15},
            {"mkt_cap": 0.45, "feeder_midcap": 0.25, "liquidity": 0.15, "sector_representation": 0.15},
            {"mkt_cap": 0.30, "feeder_midcap": 0.40, "liquidity": 0.15, "sector_representation": 0.15},
        ]

        chronological_quarters = sorted(get_historical_rebalances().keys(), key=_quarter_sort_key)
        min_train = max(1, min(min_train_quarters, len(chronological_quarters) - 1))

        # Precompute per-quarter metrics for each candidate weight set
        cache: Dict[int, Dict[str, Dict[str, Any]]] = {}
        for idx, w in enumerate(weight_candidates):
            cache[idx] = {q: cls.evaluate_quarter(q, weights=w) for q in chronological_quarters}

        walk_forward_folds: List[Dict[str, Any]] = []
        weight_selection_counts: Dict[int, int] = {i: 0 for i in range(len(weight_candidates))}

        for t in range(min_train, len(chronological_quarters)):
            train_quarters = chronological_quarters[:t]
            test_quarter = chronological_quarters[t]

            best_idx = 0
            best_train_obj = -1.0
            for idx in range(len(weight_candidates)):
                train_evals = [cache[idx][q] for q in train_quarters]
                avg_recall = sum(e["add_recall_top_5"] for e in train_evals) / len(train_evals)
                avg_prec = sum(e["add_precision_top_5"] for e in train_evals) / len(train_evals)
                avg_mrr = sum(e["add_mrr"] for e in train_evals) / len(train_evals)
                train_obj = avg_recall * 0.45 + avg_mrr * 0.35 + avg_prec * 0.20
                if train_obj > best_train_obj:
                    best_train_obj = train_obj
                    best_idx = idx

            weight_selection_counts[best_idx] += 1
            oos_eval = cache[best_idx][test_quarter]
            walk_forward_folds.append({
                "test_quarter": test_quarter,
                "train_quarters_count": len(train_quarters),
                "selected_weights": weight_candidates[best_idx],
                "oos_quarter_score": oos_eval["quarter_score"],
                "oos_add_recall_top_5": round(oos_eval["add_recall_top_5"] * 100, 1),
                "oos_add_precision_top_5": round(oos_eval["add_precision_top_5"] * 100, 1),
                "oos_add_mrr": oos_eval["add_mrr"],
                "oos_del_recall_top_5": round(oos_eval["del_recall_top_5"] * 100, 1),
                "oos_del_mrr": oos_eval["del_mrr"],
            })

        n_folds = max(1, len(walk_forward_folds))
        oos_avg_score = round(sum(f["oos_quarter_score"] for f in walk_forward_folds) / n_folds, 1)
        oos_avg_add_recall_5 = round(sum(f["oos_add_recall_top_5"] for f in walk_forward_folds) / n_folds, 1)
        oos_avg_add_precision_5 = round(sum(f["oos_add_precision_top_5"] for f in walk_forward_folds) / n_folds, 1)
        oos_avg_add_mrr = round(sum(f["oos_add_mrr"] for f in walk_forward_folds) / n_folds, 3)

        # Consensus weights chosen most often across walk-forward folds (ties favor DEFAULT_WEIGHTS)
        consensus_idx = max(
            range(len(weight_candidates)),
            key=lambda i: (weight_selection_counts[i], -i),
        )
        optimal_weights = weight_candidates[consensus_idx]
        final_audit = cls.run_full_historical_audit(weights=optimal_weights)

        return {
            "validation_method": "expanding_window_walk_forward",
            "target_rating": target_rating,
            "min_train_quarters": min_train,
            "folds_evaluated": len(walk_forward_folds),
            "iterations_run": len(weight_candidates),
            "optimal_weights": optimal_weights,
            "oos_avg_score": oos_avg_score,
            "oos_add_recall_top_5": f"{oos_avg_add_recall_5}%",
            "oos_add_precision_top_5": f"{oos_avg_add_precision_5}%",
            "oos_mean_add_mrr": oos_avg_add_mrr,
            "walk_forward_folds": walk_forward_folds,
            "final_audit": final_audit,
        }


if __name__ == "__main__":
    print("\n=================== RUNNING 3-YEAR S&P 500 HISTORICAL AUDIT (13 QUARTERS) ===================")
    tune_res = HistoricArbitrageEvaluator.optimize_and_tune_loop(target_rating=9.0)
    audit = tune_res["final_audit"]
    integrity = audit["dataset_integrity"]

    print(f"Validation Method:  {tune_res['validation_method']} ({tune_res['folds_evaluated']} OOS folds)")
    print(f"Consensus Weights:  {tune_res['optimal_weights']}")
    print(f"Dataset Integrity:  {'PASSED' if integrity['is_valid'] else 'FAILED'} ({integrity['error_count']} errors, {integrity['warning_count']} warnings)")
    print(f"OOS Walk-Forward:   Score={tune_res['oos_avg_score']}/10 | Add Recall@5={tune_res['oos_add_recall_top_5']} | Add Prec@5={tune_res['oos_add_precision_top_5']} | Add MRR={tune_res['oos_mean_add_mrr']:.3f}")
    print(f"Full-Sample Rating: {audit['evaluation_rating']} (Passed Benchmark: {audit['is_high_accuracy']})")
    print(f"Additions:          Recall@3={audit['composite_add_recall_top_3']} | Recall@5={audit['composite_add_recall_top_5']} | Recall@10={audit['composite_add_recall_top_10']} | Prec@5={audit['composite_add_precision_top_5']} | MRR={audit['mean_add_mrr']:.3f}")
    print(f"Deletions:          Recall@3={audit['composite_del_recall_top_3']} | Recall@5={audit['composite_del_recall_top_5']} | Prec@5={audit['composite_del_precision_top_5']} | MRR={audit['mean_del_mrr']:.3f}")
    print(f"Date Order Checks:  {sum(1 for c in audit['leakage_audit'] if c['cutoff_before_announce'])} / {len(audit['leakage_audit'])} Passed")
    print(f"Small-Pool Caveat:  {audit['small_pool_caveat']}")
    print("\nDetailed Quarterly Performance (Era-Accurate Thresholds):")
    for r in audit["quarterly_results"]:
        print(
            f"  [{r['quarter']:8s}] Threshold: ${r['era_cap_threshold_b']:4.1f}B | Cutoff: {r['cutoff_date']} | "
            f"Pool: {r['add_pool_size']}A/{r['del_pool_size']}D | Score: {r['quarter_score']:>4.1f}/10 | "
            f"Add P@5={r['add_precision_top_5']*100:4.0f}% MRR={r['add_mrr']:.2f} | Del MRR={r['del_mrr']:.2f}"
        )
        print(f"     Actual Adds: {r['actual_additions']} -> Top-5 Hits: {r['addition_hits_top_5']}")
        print(f"     Actual Dels: {r['actual_deletions']} -> Top-5 Hits: {r['deletion_hits_top_5']}")
