"""
S&P 500 Rebalance Timeline & Milestone Engine
Calculates the exact quarterly reconstitution schedule, milestone countdowns,
and current stage in the S&P Dow Jones Indices (S&P DJI) rebalance cycle.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional


def get_first_friday(year: int, month: int) -> date:
    """Returns the first Friday of a given year and month."""
    d = date(year, month, 1)
    # Friday is weekday 4
    days_to_friday = (4 - d.weekday()) % 7
    return d + timedelta(days=days_to_friday)


def get_third_friday(year: int, month: int) -> date:
    """Returns the third Friday of a given year and month (S&P 500 Effective Date)."""
    first_friday = get_first_friday(year, month)
    return first_friday + timedelta(weeks=2)


def get_month_end(year: int, month: int) -> date:
    """Returns the last day of a given month."""
    if month == 12:
        return date(year, 12, 31)
    next_month_start = date(year, month + 1, 1)
    return next_month_start - timedelta(days=1)


class RebalanceTimelineManager:
    """
    Manages the annual S&P 500 Quarterly Reconstitution cycle:
    - March (Q1), June (Q2), September (Q3), December (Q4)
    - Cutoff Date: End of month preceding rebalance month (Data freeze)
    - Announcement Date: First Friday of rebalance month (after 5:15 PM ET)
    - Effective Date: Third Friday of rebalance month (effective at close)
    """

    REBALANCE_MONTHS = [3, 6, 9, 12]

    @classmethod
    def get_quarter_schedule(cls, year: int, quarter: int) -> Dict[str, Any]:
        """Calculates exact milestones for a specific quarter (1 to 4)."""
        rebal_month = cls.REBALANCE_MONTHS[quarter - 1]
        
        # Cutoff month is preceding month
        if rebal_month == 3:
            cutoff_year, cutoff_month = year, 2
        elif rebal_month == 6:
            cutoff_year, cutoff_month = year, 5
        elif rebal_month == 9:
            cutoff_year, cutoff_month = year, 8
        else: # 12
            cutoff_year, cutoff_month = year, 11

        cutoff_date = get_month_end(cutoff_year, cutoff_month)
        announcement_date = get_first_friday(year, rebal_month)
        effective_date = get_third_friday(year, rebal_month)

        return {
            "quarter_label": f"Q{quarter} {year}",
            "year": year,
            "quarter": quarter,
            "rebal_month": rebal_month,
            "cutoff_date": cutoff_date,
            "announcement_date": announcement_date,
            "effective_date": effective_date,
            "trading_days_announcement_to_effective": 10
        }

    @classmethod
    def get_timeline_status(cls, ref_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Determines current position in the S&P rebalance cycle, upcoming milestones,
        and visual progress percentage.
        """
        if ref_date is None:
            ref_date = date.today()

        year = ref_date.year
        schedules = []
        for y in [year - 1, year, year + 1]:
            for q in [1, 2, 3, 4]:
                schedules.append(cls.get_quarter_schedule(y, q))

        # Find previous and next effective dates
        past_schedules = [s for s in schedules if s["effective_date"] < ref_date]
        future_schedules = [s for s in schedules if s["effective_date"] >= ref_date]

        last_rebalance = past_schedules[-1] if past_schedules else schedules[0]
        next_rebalance = future_schedules[0] if future_schedules else schedules[-1]
        following_rebalance = future_schedules[1] if len(future_schedules) > 1 else None

        cutoff = next_rebalance["cutoff_date"]
        announcement = next_rebalance["announcement_date"]
        effective = next_rebalance["effective_date"]

        days_to_cutoff = (cutoff - ref_date).days
        days_to_announcement = (announcement - ref_date).days
        days_to_effective = (effective - ref_date).days

        # Stage determination
        if ref_date <= cutoff:
            stage = "PRE_CUTOFF"
            stage_zh = "数据窗口期 (Pre-Cutoff Accumulation)"
            stage_desc = f"S&P 委员会正追踪标的，距数据冻结截止日还有 {days_to_cutoff} 天。"
            progress = max(5, int((1 - days_to_effective / 90) * 100))
            action_hint = "重点布局潜在纳入第一梯队龙头，提前建立套利底仓。"
            stage_color = "#3b82f6" # blue
        elif ref_date <= announcement:
            stage = "COMMITTEE_EVALUATION"
            stage_zh = "委员会评议期 (Committee Deliberation)"
            stage_desc = f"底层数据已冻结，委员会闭门审查中，距公告日还有 {days_to_announcement} 天。"
            progress = 70
            action_hint = "数据基本锁定，博弈高确定性名单，收窄候选组合。"
            stage_color = "#f59e0b" # amber
        elif ref_date <= effective:
            stage = "POST_ANNOUNCEMENT"
            stage_zh = "公告冲刺期 (Announcement to Effective Window)"
            stage_desc = f"名单已正式公布！距被动指数基金被动换仓生效还有 {days_to_effective} 天。"
            progress = 90
            action_hint = "执行指数效应配对套利 (Long Inclusions / Short Deletions)，关注被动买盘冲击。"
            stage_color = "#10b981" # emerald green
        else:
            stage = "POST_EFFECTIVE"
            stage_zh = "换仓结算期 (Post-Effective Cool-down)"
            stage_desc = "本期换仓已全部生效，等待进入下一季度周期。"
            progress = 100
            action_hint = "平仓了结事件驱动仓位，防范流动性均值回归。"
            stage_color = "#64748b" # slate

        return {
            "current_date": ref_date,
            "stage": stage,
            "stage_zh": stage_zh,
            "stage_desc": stage_desc,
            "stage_color": stage_color,
            "action_hint": action_hint,
            "progress": min(100, max(5, progress)),
            "next_quarter_label": next_rebalance["quarter_label"],
            "days_to_cutoff": days_to_cutoff,
            "days_to_announcement": days_to_announcement,
            "days_to_effective": days_to_effective,
            "cutoff_date": cutoff,
            "announcement_date": announcement,
            "effective_date": effective,
            "last_rebalance": last_rebalance,
            "next_rebalance": next_rebalance,
            "following_rebalance": following_rebalance,
            "full_schedule_upcoming": future_schedules[:4]
        }


if __name__ == "__main__":
    status = RebalanceTimelineManager.get_timeline_status()
    print("S&P 500 Timeline Status:")
    print(f"Target Quarter: {status['next_quarter_label']}")
    print(f"Current Stage: {status['stage_zh']} ({status['stage']})")
    print(f"Days to Cutoff ({status['cutoff_date']}): {status['days_to_cutoff']} days")
    print(f"Days to Announcement ({status['announcement_date']}): {status['days_to_announcement']} days")
    print(f"Days to Effective ({status['effective_date']}): {status['days_to_effective']} days")
