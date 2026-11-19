"""
S&P 500 Rebalance Timeline & Milestone Engine
Calculates the exact quarterly reconstitution schedule, milestone countdowns,
and current stage in the S&P Dow Jones Indices (S&P DJI) rebalance cycle.
"""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Set
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")
POST_EFFECTIVE_COOLDOWN_DAYS = 5


def _observed_holiday(d: date) -> date:
    """Adjusts a fixed-date US holiday to Friday if Saturday, Monday if Sunday."""
    if d.weekday() == 5:  # Saturday -> observed Friday
        return d - timedelta(days=1)
    if d.weekday() == 6:  # Sunday -> observed Monday
        return d + timedelta(days=1)
    return d


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """Returns the n-th occurrence (1-indexed) of `weekday` (0=Mon..6=Sun) in (year, month)."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + (n - 1) * 7)


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """Returns the last occurrence of `weekday` (0=Mon..6=Sun) in (year, month)."""
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    offset = (last.weekday() - weekday) % 7
    return last - timedelta(days=offset)


def _easter_sunday(year: int) -> date:
    """Computes Gregorian Easter Sunday using the Meeus/Jones/Butcher algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_nyse_holidays(year: int) -> Set[date]:
    """
    Returns major NYSE full-day market closure holidays for a given calendar year.
    Includes observed New Year's Day (including Dec 31 when Jan 1 of year+1 is Saturday),
    MLK Day, Presidents' Day, Good Friday, Memorial Day, Juneteenth (>= 2022),
    Independence Day, Labor Day, Thanksgiving, and Christmas Day.
    """
    holidays: Set[date] = set()

    # New Year's Day (this year, plus Dec 31 if next year's Jan 1 falls on Saturday)
    nyd = _observed_holiday(date(year, 1, 1))
    if nyd.year == year:
        holidays.add(nyd)
    next_nyd = _observed_holiday(date(year + 1, 1, 1))
    if next_nyd.year == year:
        holidays.add(next_nyd)

    # MLK Day (3rd Monday of Jan) & Presidents' Day (3rd Monday of Feb)
    holidays.add(_nth_weekday_of_month(year, 1, 0, 3))
    holidays.add(_nth_weekday_of_month(year, 2, 0, 3))

    # Good Friday (2 days before Easter Sunday)
    holidays.add(_easter_sunday(year) - timedelta(days=2))

    # Memorial Day (last Monday of May)
    holidays.add(_last_weekday_of_month(year, 5, 0))

    # Juneteenth National Independence Day (NYSE holiday since 2022)
    if year >= 2022:
        holidays.add(_observed_holiday(date(year, 6, 19)))

    # Independence Day (July 4)
    holidays.add(_observed_holiday(date(year, 7, 4)))

    # Labor Day (1st Monday of September)
    holidays.add(_nth_weekday_of_month(year, 9, 0, 1))

    # Thanksgiving Day (4th Thursday of November)
    holidays.add(_nth_weekday_of_month(year, 11, 3, 4))

    # Christmas Day (Dec 25)
    holidays.add(_observed_holiday(date(year, 12, 25)))

    return holidays


def is_nyse_trading_day(d: date) -> bool:
    """Returns True if `d` is a weekday and not a major NYSE holiday."""
    if d.weekday() >= 5:
        return False
    return d not in get_nyse_holidays(d.year)


def previous_nyse_trading_day(d: date) -> date:
    """Returns `d` if it is a NYSE trading day, otherwise steps backward to the last one."""
    cur = d
    while not is_nyse_trading_day(cur):
        cur -= timedelta(days=1)
    return cur


def count_trading_days(start_date: date, end_date: date) -> int:
    """Counts NYSE trading days strictly after `start_date` up to and including `end_date`."""
    if end_date <= start_date:
        return 0
    count = 0
    cur = start_date + timedelta(days=1)
    while cur <= end_date:
        if is_nyse_trading_day(cur):
            count += 1
        cur += timedelta(days=1)
    return count


def get_first_friday(year: int, month: int) -> date:
    """Returns the first Friday of a given year and month."""
    d = date(year, month, 1)
    days_to_friday = (4 - d.weekday()) % 7
    return d + timedelta(days=days_to_friday)


def get_third_friday(year: int, month: int) -> date:
    """Returns the third Friday of a given year and month."""
    first_friday = get_first_friday(year, month)
    return first_friday + timedelta(weeks=2)


def get_month_end(year: int, month: int) -> date:
    """Returns the last NYSE business day of a given month (skipping weekends & US market holidays)."""
    if month == 12:
        last_cal = date(year, 12, 31)
    else:
        last_cal = date(year, month + 1, 1) - timedelta(days=1)
    return previous_nyse_trading_day(last_cal)


class RebalanceTimelineManager:
    """
    Manages the annual S&P 500 Quarterly Reconstitution cycle:
    - March (Q1), June (Q2), September (Q3), December (Q4)
    - Cutoff Date: Last NYSE business day of preceding month (Data freeze)
    - Announcement Date: First Friday of rebalance month (after 5:15 PM ET; shifted back if holiday)
    - Effective Date: Third Friday of rebalance month close (shifted to prior trading day if NYSE holiday,
      e.g., Juneteenth or Good Friday)
    """

    REBALANCE_MONTHS = [3, 6, 9, 12]

    @classmethod
    def get_quarter_schedule(cls, year: int, quarter: int) -> Dict[str, Any]:
        """Calculates exact milestones for a specific quarter (1 to 4)."""
        if quarter not in (1, 2, 3, 4):
            raise ValueError(f"quarter must be 1..4, got {quarter}")

        rebal_month = cls.REBALANCE_MONTHS[quarter - 1]
        cutoff_year, cutoff_month = year, rebal_month - 1

        cutoff_date = get_month_end(cutoff_year, cutoff_month)
        announcement_date = previous_nyse_trading_day(get_first_friday(year, rebal_month))
        effective_date = previous_nyse_trading_day(get_third_friday(year, rebal_month))
        trading_days = count_trading_days(announcement_date, effective_date)

        return {
            "quarter_label": f"Q{quarter} {year}",
            "year": year,
            "quarter": quarter,
            "rebal_month": rebal_month,
            "cutoff_date": cutoff_date,
            "announcement_date": announcement_date,
            "effective_date": effective_date,
            "trading_days_announcement_to_effective": trading_days,
        }

    @classmethod
    def get_timeline_status(cls, ref_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Determines current position in the S&P rebalance cycle, upcoming milestones,
        and strictly monotonic visual progress percentage (0.0 - 100.0%).
        Defaults to the current calendar date in America/New_York.
        """
        if ref_date is None:
            ref_date = datetime.now(NY_TZ).date()

        year = ref_date.year
        schedules: List[Dict[str, Any]] = []
        for y in [year - 1, year, year + 1]:
            for q in [1, 2, 3, 4]:
                schedules.append(cls.get_quarter_schedule(y, q))

        past_schedules = [s for s in schedules if s["effective_date"] < ref_date]
        future_schedules = [s for s in schedules if s["effective_date"] >= ref_date]

        last_rebalance = past_schedules[-1] if past_schedules else schedules[0]
        next_rebalance = future_schedules[0] if future_schedules else schedules[-1]
        following_rebalance = future_schedules[1] if len(future_schedules) > 1 else None

        last_effective = last_rebalance["effective_date"]
        cutoff = next_rebalance["cutoff_date"]
        announcement = next_rebalance["announcement_date"]
        effective = next_rebalance["effective_date"]

        days_since_last_effective = (ref_date - last_effective).days
        days_to_cutoff = (cutoff - ref_date).days
        days_to_announcement = (announcement - ref_date).days
        days_to_effective = (effective - ref_date).days

        # Strictly monotonic progress across the full cycle: (last_effective, next_effective]
        total_cycle_days = max(1, (effective - last_effective).days)
        progress = round(
            min(100.0, max(0.0, (days_since_last_effective / total_cycle_days) * 100.0)),
            1,
        )

        # Stage determination (includes reachable 5-day POST_EFFECTIVE cooldown)
        if 0 < days_since_last_effective <= POST_EFFECTIVE_COOLDOWN_DAYS:
            stage = "POST_EFFECTIVE"
            stage_zh = "换仓结算期 (Post-Effective Cool-down)"
            stage_desc = (
                f"{last_rebalance['quarter_label']} 换仓已于 {days_since_last_effective} 天前生效，"
                f"正处于 5 日均值回归冷静期，下一目标季度为 {next_rebalance['quarter_label']}。"
            )
            action_hint = "平仓了结事件驱动仓位，防范被动买盘退潮后的流动性均值回归。"
            stage_color = "#64748b"  # slate
        elif ref_date <= cutoff:
            stage = "PRE_CUTOFF"
            stage_zh = "数据窗口期 (Pre-Cutoff Accumulation)"
            stage_desc = f"S&P 委员会正追踪标的，距数据冻结截止日还有 {days_to_cutoff} 天。"
            action_hint = "重点布局潜在纳入第一梯队龙头，提前建立套利底仓。"
            stage_color = "#3b82f6"  # blue
        elif ref_date <= announcement:
            stage = "COMMITTEE_EVALUATION"
            stage_zh = "委员会评议期 (Committee Deliberation)"
            stage_desc = f"底层数据已冻结，委员会闭门审查中，距公告日还有 {days_to_announcement} 天。"
            action_hint = "数据基本锁定，博弈高确定性名单，收窄候选组合。"
            stage_color = "#f59e0b"  # amber
        else:
            stage = "POST_ANNOUNCEMENT"
            stage_zh = "公告冲刺期 (Announcement to Effective Window)"
            stage_desc = (
                f"名单已正式公布！距被动指数基金换仓生效还有 {days_to_effective} 天"
                f"（窗口共 {next_rebalance['trading_days_announcement_to_effective']} 个交易日）。"
            )
            action_hint = "执行指数效应配对套利 (Long Inclusions / Short Deletions)，关注被动买盘冲击。"
            stage_color = "#10b981"  # emerald green

        return {
            "current_date": ref_date,
            "stage": stage,
            "stage_zh": stage_zh,
            "stage_desc": stage_desc,
            "stage_color": stage_color,
            "action_hint": action_hint,
            "progress": progress,
            "next_quarter_label": next_rebalance["quarter_label"],
            "days_since_last_effective": days_since_last_effective,
            "days_to_cutoff": days_to_cutoff,
            "days_to_announcement": days_to_announcement,
            "days_to_effective": days_to_effective,
            "cutoff_date": cutoff,
            "announcement_date": announcement,
            "effective_date": effective,
            "trading_days_announcement_to_effective": next_rebalance["trading_days_announcement_to_effective"],
            "last_rebalance": last_rebalance,
            "next_rebalance": next_rebalance,
            "following_rebalance": following_rebalance,
            "full_schedule_upcoming": future_schedules[:4],
        }


if __name__ == "__main__":
    status = RebalanceTimelineManager.get_timeline_status()
    print("S&P 500 Timeline Status (America/New_York):")
    print(f"Reference Date: {status['current_date']}")
    print(f"Target Quarter: {status['next_quarter_label']}")
    print(f"Current Stage:  {status['stage_zh']} ({status['stage']}) | Progress: {status['progress']}%")
    print(f"Days to Cutoff ({status['cutoff_date']}): {status['days_to_cutoff']} days")
    print(f"Days to Announcement ({status['announcement_date']}): {status['days_to_announcement']} days")
    print(f"Days to Effective ({status['effective_date']}): {status['days_to_effective']} days")
    print(f"Announcement -> Effective Trading Days: {status['trading_days_announcement_to_effective']}")
