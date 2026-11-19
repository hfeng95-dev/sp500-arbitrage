"""
S&P 500 Eligibility & Rebalance Arbitrage Scoring Engine
Implements official S&P Dow Jones Indices (S&P DJI) inclusion/deletion rules,
eligibility filters, and multi-factor ranking algorithms.
"""

import math
from typing import Dict, Any, List, Optional


class SP500RebalanceEngine:
    """
    S&P DJI Index Committee Rule Engine:
    1. Unadjusted Market Capitalization: >= $22.7B (effective Jul 2025; era-adjusted historically).
    2. Float-Adjusted Market Cap (FMC): >= 50% of unadjusted threshold (checked when supplied).
    3. Investable Weight Factor (IWF / Public Float): >= 0.10 (10%, checked when supplied).
    4. Financial Viability: Trailing 4-quarter sum of GAAP net income > 0 AND most recent quarter (Q0) > 0.
    5. Liquidity: Annual Dollar Value Traded / Float-Adjusted Mkt Cap >= 0.75, and
       minimum monthly trading volume >= 250,000 shares for each of the prior 6 months (when supplied).
    6. IPO Seasoning: >= 12 months post-IPO (when supplied).
    7. Domicile: United States (primary listing NYSE, NASDAQ, or Cboe).
    8. Feeder Preference: S&P MidCap 400 members historically receive highest committee priority.
    """

    DEFAULT_MKT_CAP_THRESHOLD_B = 22.7
    MIN_LIQ_RATIO = 0.75
    MIN_IWF = 0.10
    MIN_MONTHLY_VOLUME = 250_000
    MIN_IPO_MONTHS = 12
    LOG_CAP_CEILING_B = 150.0

    # Single source of truth across engine, evaluator, UI, and documentation
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "mkt_cap": 0.35,
        "feeder_midcap": 0.35,
        "liquidity": 0.15,
        "sector_representation": 0.15,
    }

    # S&P 500 Sector weights vs Total Market (approximate deficit / priority mapping)
    SECTOR_DEFICIT_PRIORITY: Dict[str, float] = {
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
        "Utilities": 0.80,
    }

    @classmethod
    def get_era_cap_threshold(cls, quarter: str) -> float:
        """
        Returns the official S&P DJI minimum unadjusted market-cap guideline ($B) for a quarter:
        - 2023: $14.5B
        - H1 2024 (Q1–Q2 2024): $15.8B
        - H2 2024 (Q3–Q4 2024): $18.0B
        - H1 2025 (Q1–Q2 2025): $20.5B
        - H2 2025+ (Q3 2025 onward): $22.7B
        """
        q_str = (quarter or "").strip().upper()
        if "2023" in q_str:
            return 14.5
        if "Q1 2024" in q_str or "Q2 2024" in q_str:
            return 15.8
        if "Q3 2024" in q_str or "Q4 2024" in q_str:
            return 18.0
        if "Q1 2025" in q_str or "Q2 2025" in q_str:
            return 20.5
        return cls.DEFAULT_MKT_CAP_THRESHOLD_B

    @classmethod
    def _compute_log_cap_score(cls, mkt_cap_b: float, threshold_b: float) -> float:
        """
        True log-scaled market-cap score mapped onto [40.0, 100.0]:
        log(mkt_cap / threshold) / log(150.0 / threshold).
        """
        eff_threshold = max(1.0, float(threshold_b))
        ceiling = max(cls.LOG_CAP_CEILING_B, eff_threshold * 2.0)
        eff_cap = max(eff_threshold, float(mkt_cap_b))
        log_ratio = math.log(eff_cap / eff_threshold) / math.log(ceiling / eff_threshold)
        return min(100.0, max(40.0, 40.0 + 60.0 * log_ratio))

    @classmethod
    def evaluate_addition_candidate(
        cls,
        candidate: Dict[str, Any],
        mkt_cap_threshold_b: float = DEFAULT_MKT_CAP_THRESHOLD_B,
        weights: Optional[Dict[str, float]] = None,
        strict_official_rules: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluates a single addition candidate against S&P DJI criteria and calculates
        its inclusion probability score (0 - 100).

        Core eligibility fields (`mkt_cap_b`, `gaap_4q_pos`, `gaap_q0_pos`, `liq_ratio`,
        `us_domicile`) fail closed when missing or None. Extended official S&P 500 rules
        (`fmc_b`, `iwf`, `min_monthly_vol`, `ipo_months`) are enforced whenever supplied
        (or fail closed when `strict_official_rules=True`).
        """
        w = weights or cls.DEFAULT_WEIGHTS
        mkt_cap = candidate.get("mkt_cap_b")
        mkt_cap_val = float(mkt_cap) if mkt_cap is not None else 0.0
        gaap_4q = candidate.get("gaap_4q_pos")
        gaap_q0 = candidate.get("gaap_q0_pos")
        liq = candidate.get("liq_ratio")
        us_domicile = candidate.get("us_domicile")
        feeder = candidate.get("feeder", "Non-Index")
        sector = candidate.get("sector", "Industrials")

        # Extended official S&P 500 rule fields
        fmc_b = candidate.get("fmc_b")
        iwf = candidate.get("iwf")
        min_monthly_vol = candidate.get("min_monthly_vol")
        ipo_months = candidate.get("ipo_months")

        # 1. Hard Eligibility Filters (fail-closed on missing core fields)
        passed_cap = (mkt_cap is not None) and (mkt_cap_val >= mkt_cap_threshold_b)
        passed_gaap = (gaap_4q is True) and (gaap_q0 is True)
        passed_liq = (liq is not None) and (float(liq) >= cls.MIN_LIQ_RATIO)
        passed_domicile = (us_domicile is True)

        min_fmc_b = 0.5 * mkt_cap_threshold_b
        if fmc_b is None:
            passed_fmc = not strict_official_rules
        else:
            passed_fmc = float(fmc_b) >= min_fmc_b

        if iwf is None:
            passed_iwf = not strict_official_rules
        else:
            passed_iwf = float(iwf) >= cls.MIN_IWF

        if min_monthly_vol is None:
            passed_volume = not strict_official_rules
        else:
            passed_volume = float(min_monthly_vol) >= cls.MIN_MONTHLY_VOLUME

        if ipo_months is None:
            passed_ipo = not strict_official_rules
        else:
            passed_ipo = float(ipo_months) >= cls.MIN_IPO_MONTHS

        is_eligible = (
            passed_cap
            and passed_gaap
            and passed_liq
            and passed_domicile
            and passed_fmc
            and passed_iwf
            and passed_volume
            and passed_ipo
        )

        fail_reasons: List[str] = []
        if not passed_cap:
            fail_reasons.append(f"市值未达标 (${mkt_cap_val:.1f}B < ${mkt_cap_threshold_b:.1f}B)")
        if not passed_gaap:
            if gaap_4q is not True and gaap_q0 is not True:
                fail_reasons.append("过去4季度累计 GAAP 净利润之和与最近季度 (Q0) 均未转正")
            elif gaap_4q is not True:
                fail_reasons.append("过去4季度累计 GAAP 净利润之和 <= 0 (4Q sum <= 0)")
            else:
                fail_reasons.append("最近季度 GAAP 净利润 <= 0 (Q0 <= 0)")
        if not passed_liq:
            if liq is None:
                fail_reasons.append("缺少流动性换手率数据 (liq_ratio missing)")
            else:
                fail_reasons.append(f"流动性换手不足 ({float(liq):.2f} < {cls.MIN_LIQ_RATIO:.2f})")
        if not passed_domicile:
            if us_domicile is None:
                fail_reasons.append("缺少美国注册地验证字段 (us_domicile missing)")
            else:
                fail_reasons.append("注册地非美国本土企业")
        if not passed_fmc:
            if fmc_b is None:
                fail_reasons.append("缺少流通调整市值数据 (fmc_b missing)")
            else:
                fail_reasons.append(
                    f"流通调整市值不足 (FMC ${float(fmc_b):.1f}B < ${min_fmc_b:.1f}B)"
                )
        if not passed_iwf:
            if iwf is None:
                fail_reasons.append("缺少公众流通股比例数据 (iwf missing)")
            else:
                fail_reasons.append(f"公众流通股比例不足 (IWF {float(iwf):.2f} < {cls.MIN_IWF:.2f})")
        if not passed_volume:
            if min_monthly_vol is None:
                fail_reasons.append("缺少过去6个月最低月成交量数据 (min_monthly_vol missing)")
            else:
                fail_reasons.append(
                    f"月成交量未达标 ({int(min_monthly_vol):,} < {cls.MIN_MONTHLY_VOLUME:,})"
                )
        if not passed_ipo:
            if ipo_months is None:
                fail_reasons.append("缺少上市满12个月校验数据 (ipo_months missing)")
            else:
                fail_reasons.append(f"IPO 上市时间不足 12 个月 ({ipo_months}m < {cls.MIN_IPO_MONTHS}m)")

        # 2. Multi-Factor Scoring (0 - 100)
        if not is_eligible:
            score = round(
                max(0.0, min(35.0, (mkt_cap_val / max(1.0, mkt_cap_threshold_b)) * 20.0)),
                1,
            )
            prob_label = "DISQUALIFIED"
            prob_color = "#ef4444"
        else:
            cap_score = cls._compute_log_cap_score(mkt_cap_val, mkt_cap_threshold_b)
            feeder_score = 100.0 if "MidCap 400" in feeder else 70.0
            liq_score = min(100.0, max(50.0, float(liq) / 2.0 * 100.0))
            sec_mult = cls.SECTOR_DEFICIT_PRIORITY.get(sector, 1.0)
            sec_score = min(100.0, 75.0 * sec_mult)

            raw_score = (
                cap_score * w["mkt_cap"]
                + feeder_score * w["feeder_midcap"]
                + liq_score * w["liquidity"]
                + sec_score * w["sector_representation"]
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
            "mkt_cap_b": mkt_cap_val,
            "fmc_b": fmc_b,
            "iwf": iwf,
            "liq_ratio": float(liq) if liq is not None else None,
            "min_monthly_vol": min_monthly_vol,
            "ipo_months": ipo_months,
            "is_eligible": is_eligible,
            "passed_cap": passed_cap,
            "passed_gaap": passed_gaap,
            "passed_liq": passed_liq,
            "passed_domicile": passed_domicile,
            "passed_fmc": passed_fmc,
            "passed_iwf": passed_iwf,
            "passed_volume": passed_volume,
            "passed_ipo": passed_ipo,
            "feeder": feeder,
            "fail_reasons": fail_reasons,
            "score": score,
            "prob_label": prob_label,
            "prob_color": prob_color,
        }

    @classmethod
    def evaluate_deletion_candidate(
        cls,
        candidate: Dict[str, Any],
        mkt_cap_threshold_b: float = DEFAULT_MKT_CAP_THRESHOLD_B,
    ) -> Dict[str, Any]:
        """
        Evaluates a current S&P 500 member's vulnerability to deletion using:
        - Pending M&A takeover (98.0 CERTAIN)
        - Market cap ratio relative to era S&P DJI threshold (`mkt_cap_b / threshold`)
        - Bottom rank inside S&P 500 (`rank_bottom`, 1 = smallest constituent)
        - Consecutive negative GAAP quarters (`neg_earnings_streak`)

        Calibrated so genuine high-risk stocks (< $7.5B with sustained losses) reach
        HIGH RISK (>= 75.0) up to 95.0.
        """
        mkt_cap = float(candidate.get("mkt_cap_b", 10.0))
        neg_streak = max(0, int(candidate.get("neg_earnings_streak", 0)))
        rank_bottom = max(1, int(candidate.get("rank_bottom", 50)))
        ma_pending = bool(candidate.get("ma_pending", False))
        acquirer = candidate.get("acquirer", "")
        cap_ratio = round(mkt_cap / max(1.0, float(mkt_cap_threshold_b)), 3)

        if ma_pending:
            risk_score = 98.0
            risk_label = "CERTAIN (被并购移除)"
            risk_color = "#ef4444"
            reason = f"已公告被 {acquirer or '外部收购方'} 并购，交割日前后将强制剔除"
        else:
            # 1. Cap-ratio vulnerability (0 - 95)
            if cap_ratio <= 0.22:
                cap_risk = 95.0
            elif cap_ratio <= 0.35:
                cap_risk = 95.0 - ((cap_ratio - 0.22) / 0.13) * 15.0
            elif cap_ratio <= 0.55:
                cap_risk = 80.0 - ((cap_ratio - 0.35) / 0.20) * 30.0
            else:
                cap_risk = max(10.0, 50.0 - (cap_ratio - 0.55) * 60.0)

            # 2. Index bottom-rank vulnerability (0 - 95)
            if rank_bottom <= 5:
                rank_risk = 95.0 - (rank_bottom - 1) * 3.0
            elif rank_bottom <= 15:
                rank_risk = 80.0 - (rank_bottom - 5) * 2.5
            elif rank_bottom <= 30:
                rank_risk = 55.0 - (rank_bottom - 15) * 2.0
            else:
                rank_risk = max(5.0, 25.0 - (rank_bottom - 30) * 0.5)

            # 3. Consecutive GAAP loss drag (0 - 100)
            earnings_risk = min(100.0, neg_streak * 25.0)

            combined = cap_risk * 0.50 + rank_risk * 0.25 + earnings_risk * 0.25
            risk_score = round(min(95.0, max(0.0, combined)), 1)

            if risk_score >= 75.0:
                risk_label = "HIGH RISK (高危剔除)"
                risk_color = "#ef4444"
                reason = (
                    f"市值滑落至 ${mkt_cap:.1f}B (仅为门槛 {cap_ratio * 100:.0f}%)，"
                    f"标普尾部倒数第 {rank_bottom} 位，连续 {neg_streak} 季亏损"
                )
            elif risk_score >= 50.0:
                risk_label = "ELEVATED (剔除预警)"
                risk_color = "#f59e0b"
                reason = (
                    f"市值处于标普尾部梯队 (${mkt_cap:.1f}B，倒数第 {rank_bottom} 位)，"
                    f"距新纳入门槛存在明显缺口"
                )
            else:
                risk_label = "LOW RISK (相对安全)"
                risk_color = "#10b981"
                reason = "虽处后段但市值与盈利仍满足最低维持基准"

        return {
            "ticker": candidate["ticker"],
            "name": candidate.get("name", candidate["ticker"]),
            "sector": candidate.get("sector", "Unknown"),
            "mkt_cap_b": mkt_cap,
            "cap_ratio": cap_ratio,
            "rank_bottom": rank_bottom,
            "neg_earnings_streak": neg_streak,
            "ma_pending": ma_pending,
            "acquirer": acquirer,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "risk_color": risk_color,
            "reason": reason,
        }

    @classmethod
    def rank_addition_candidates(
        cls,
        candidates: List[Dict[str, Any]],
        mkt_cap_threshold_b: float = DEFAULT_MKT_CAP_THRESHOLD_B,
        weights: Optional[Dict[str, float]] = None,
        strict_official_rules: bool = False,
    ) -> List[Dict[str, Any]]:
        """Ranks additions by eligibility then score descending."""
        evaluated = [
            cls.evaluate_addition_candidate(
                c,
                mkt_cap_threshold_b=mkt_cap_threshold_b,
                weights=weights,
                strict_official_rules=strict_official_rules,
            )
            for c in candidates
        ]
        evaluated.sort(key=lambda x: (x["is_eligible"], x["score"], x["mkt_cap_b"]), reverse=True)
        for idx, item in enumerate(evaluated, 1):
            item["rank"] = idx
        return evaluated

    @classmethod
    def rank_deletion_candidates(
        cls,
        candidates: List[Dict[str, Any]],
        mkt_cap_threshold_b: float = DEFAULT_MKT_CAP_THRESHOLD_B,
    ) -> List[Dict[str, Any]]:
        """Ranks deletions by risk score descending."""
        evaluated = [
            cls.evaluate_deletion_candidate(c, mkt_cap_threshold_b=mkt_cap_threshold_b)
            for c in candidates
        ]
        evaluated.sort(key=lambda x: (x["risk_score"], -x["rank_bottom"]), reverse=True)
        for idx, item in enumerate(evaluated, 1):
            item["rank"] = idx
        return evaluated
