"""
S&P 500 Eligibility & Rebalance Arbitrage Scoring Engine
Implements official S&P Dow Jones Indices (S&P DJI) inclusion/deletion rules,
eligibility filters, and multi-factor ranking algorithms.
"""

from typing import Dict, Any, List, Tuple


class SP500RebalanceEngine:
    """
    S&P DJI Index Committee Rule Engine:
    1. Market Capitalization: >= $18.0B (can be adapted by era).
    2. Financial Viability: 4 consecutive quarters GAAP net income > 0 AND Q0 > 0.
    3. Liquidity: Annual Dollar Value Traded / Float-Adjusted Mkt Cap >= 0.75.
    4. Domicile: United States (primary listing NYSE, NASDAQ, or Cboe).
    5. Feeder Preference: S&P MidCap 400 members historically receive highest priority.
    """

    DEFAULT_WEIGHTS = {
        "mkt_cap": 0.40,
        "feeder_midcap": 0.25,
        "liquidity": 0.15,
        "sector_representation": 0.20
    }

    # S&P 500 Sector weights vs Total Market (approximate deficit / priority mapping)
    # The committee often prioritizes underrepresented sectors to preserve index balance
    SECTOR_DEFICIT_PRIORITY = {
        "Financials": 1.20,
        "Information Technology": 1.15,
        "Industrials": 1.10,
        "Health Care": 1.05,
        "Consumer Discretionary": 1.00,
        "Communication Services": 0.95,
        "Consumer Staples": 0.90,
        "Energy": 0.90,
        "Real Estate": 0.85,
        "Materials": 0.85,
        "Utilities": 0.80
    }

    @classmethod
    def evaluate_addition_candidate(
        cls,
        candidate: Dict[str, Any],
        mkt_cap_threshold_b: float = 18.0,
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a single addition candidate against S&P DJI criteria and calculates
        its inclusion probability score (0 - 100%).
        """
        w = weights or cls.DEFAULT_WEIGHTS
        mkt_cap = candidate.get("mkt_cap_b", 0.0)
        gaap_4q = candidate.get("gaap_4q_pos", False)
        gaap_q0 = candidate.get("gaap_q0_pos", False)
        liq = candidate.get("liq_ratio", 1.0)
        us_domicile = candidate.get("us_domicile", True)
        feeder = candidate.get("feeder", "Non-Index")
        sector = candidate.get("sector", "Industrials")

        # 1. Hard Eligibility Filters
        passed_cap = (mkt_cap >= mkt_cap_threshold_b)
        passed_gaap = bool(gaap_4q and gaap_q0)
        passed_liq = bool(liq >= 0.75)
        passed_domicile = bool(us_domicile)

        is_eligible = (passed_cap and passed_gaap and passed_liq and passed_domicile)

        fail_reasons = []
        if not passed_cap:
            fail_reasons.append(f"市值未达标 (${mkt_cap:.1f}B < ${mkt_cap_threshold_b}B)")
        if not passed_gaap:
            if not gaap_4q and not gaap_q0:
                fail_reasons.append("连续4季度与最近季度 GAAP 均为负值")
            elif not gaap_4q:
                fail_reasons.append("连续4季度 GAAP 累计净利润为负")
            else:
                fail_reasons.append("最近季度 GAAP 净利润为负")
        if not passed_liq:
            fail_reasons.append(f"流动性换手不足 ({liq:.2f} < 0.75)")
        if not passed_domicile:
            fail_reasons.append("注册地非美国本土企业")

        # 2. Multi-Factor Scoring (0 - 100)
        if not is_eligible:
            score = max(0.0, min(35.0, (mkt_cap / max(1.0, mkt_cap_threshold_b)) * 20.0))
            prob_label = "DISQUALIFIED"
            prob_color = "#ef4444"
        else:
            # Market Cap component (log scale normalized up to $150B)
            cap_score = min(100.0, max(0.0, (mkt_cap - mkt_cap_threshold_b) / 80.0 * 60.0 + 40.0))
            # Feeder preference component
            feeder_score = 100.0 if "MidCap 400" in feeder else 70.0
            # Liquidity score
            liq_score = min(100.0, max(50.0, liq / 2.0 * 100.0))
            # Sector fit
            sec_mult = cls.SECTOR_DEFICIT_PRIORITY.get(sector, 1.0)
            sec_score = min(100.0, 75.0 * sec_mult)

            raw_score = (
                cap_score * w["mkt_cap"] +
                feeder_score * w["feeder_midcap"] +
                liq_score * w["liquidity"] +
                sec_score * w["sector_representation"]
            )
            score = round(raw_score, 1)

            if score >= 80.0:
                prob_label = "VERY HIGH (第一顺位)"
                prob_color = "#10b981"
            elif score >= 68.0:
                prob_label = "HIGH (主要候选)"
                prob_color = "#3b82f6"
            elif score >= 55.0:
                prob_label = "MODERATE (观察名单)"
                prob_color = "#f59e0b"
            else:
                prob_label = "LOW (候补梯队)"
                prob_color = "#94a3b8"

        return {
            "ticker": candidate["ticker"],
            "name": candidate.get("name", candidate["ticker"]),
            "sector": sector,
            "mkt_cap_b": mkt_cap,
            "is_eligible": is_eligible,
            "passed_cap": passed_cap,
            "passed_gaap": passed_gaap,
            "passed_liq": passed_liq,
            "passed_domicile": passed_domicile,
            "feeder": feeder,
            "fail_reasons": fail_reasons,
            "score": score,
            "prob_label": prob_label,
            "prob_color": prob_color
        }

    @classmethod
    def evaluate_deletion_candidate(cls, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates current S&P 500 member's vulnerability to deletion.
        """
        mkt_cap = candidate.get("mkt_cap_b", 10.0)
        neg_streak = candidate.get("neg_earnings_streak", 0)
        ma_pending = candidate.get("ma_pending", False)
        acquirer = candidate.get("acquirer", "")

        # M&A cases have near 100% deletion certainty
        if ma_pending:
            risk_score = 98.0
            risk_label = "CERTAIN (被并购移除)"
            risk_color = "#ef4444"
            reason = f"已公告被 {acquirer} 并购，交割日前后将强制剔除"
        else:
            # Score based on small market cap (< $8B is vulnerable, < $5B is critical danger)
            if mkt_cap <= 5.0:
                cap_risk = 90.0
            elif mkt_cap <= 7.5:
                cap_risk = 75.0
            elif mkt_cap <= 10.0:
                cap_risk = 50.0
            else:
                cap_risk = max(10.0, 40.0 - (mkt_cap - 10.0) * 2.0)

            # Negative earnings drag
            earnings_risk = min(50.0, neg_streak * 15.0)

            risk_score = round(min(95.0, cap_risk * 0.7 + earnings_risk * 0.3), 1)

            if risk_score >= 75.0:
                risk_label = "HIGH RISK (高危剔除)"
                risk_color = "#ef4444"
                reason = f"市值已滑落至 ${mkt_cap:.1f}B，且连续 {neg_streak} 季亏损，严重违背 S&P 500 代表性标准"
            elif risk_score >= 50.0:
                risk_label = "ELEVATED (剔除预警)"
                risk_color = "#f59e0b"
                reason = f"市值处于标普末尾5%梯队 (${mkt_cap:.1f}B)，排名垫底"
            else:
                risk_label = "LOW RISK (相对安全)"
                risk_color = "#10b981"
                reason = "虽处后段但流动性与财务仍满足最低维持基准"

        return {
            "ticker": candidate["ticker"],
            "name": candidate.get("name", candidate["ticker"]),
            "sector": candidate.get("sector", "Unknown"),
            "mkt_cap_b": mkt_cap,
            "neg_earnings_streak": neg_streak,
            "ma_pending": ma_pending,
            "acquirer": acquirer,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "risk_color": risk_color,
            "reason": reason
        }

    @classmethod
    def rank_addition_candidates(
        cls,
        candidates: List[Dict[str, Any]],
        mkt_cap_threshold_b: float = 18.0,
        weights: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """Ranks additions by score descending."""
        evaluated = [cls.evaluate_addition_candidate(c, mkt_cap_threshold_b, weights) for c in candidates]
        evaluated.sort(key=lambda x: (x["is_eligible"], x["score"]), reverse=True)
        for idx, item in enumerate(evaluated, 1):
            item["rank"] = idx
        return evaluated

    @classmethod
    def rank_deletion_candidates(cls, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks deletions by risk score descending."""
        evaluated = [cls.evaluate_deletion_candidate(c) for c in candidates]
        evaluated.sort(key=lambda x: x["risk_score"], reverse=True)
        for idx, item in enumerate(evaluated, 1):
            item["rank"] = idx
        return evaluated
