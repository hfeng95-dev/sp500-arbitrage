"""Unit tests for timeline_manager.py (NYSE business days, holidays, cooldown, monotonic progress)."""

from datetime import date, timedelta

from timeline_manager import (
    POST_EFFECTIVE_COOLDOWN_DAYS,
    RebalanceTimelineManager,
    count_trading_days,
    get_month_end,
    get_nyse_holidays,
    is_nyse_trading_day,
)


def test_get_month_end_skips_weekends():
    # May 31, 2026 is Sunday -> Fri May 29
    assert get_month_end(2026, 5) == date(2026, 5, 29)
    # Feb 28, 2026 is Saturday -> Fri Feb 27
    assert get_month_end(2026, 2) == date(2026, 2, 27)
    # Nov 30, 2025 is Sunday -> Fri Nov 28
    assert get_month_end(2025, 11) == date(2025, 11, 28)
    # Aug 31, 2026 is Monday -> stays Aug 31
    assert get_month_end(2026, 8) == date(2026, 8, 31)


def test_get_month_end_skips_us_holidays():
    # Jan 1, 2022 is Saturday -> New Year's Day observed on Fri Dec 31, 2021
    assert date(2021, 12, 31) in get_nyse_holidays(2021)
    assert not is_nyse_trading_day(date(2021, 12, 31))
    assert get_month_end(2021, 12) == date(2021, 12, 30)


def test_post_effective_cooldown_is_reachable_and_bounded():
    q1_2026 = RebalanceTimelineManager.get_quarter_schedule(2026, 1)
    eff = q1_2026["effective_date"]

    # On effective date itself: still POST_ANNOUNCEMENT at 100.0%
    st_eff = RebalanceTimelineManager.get_timeline_status(ref_date=eff)
    assert st_eff["stage"] == "POST_ANNOUNCEMENT"
    assert st_eff["progress"] == 100.0

    # Days 1..5 after effective date: POST_EFFECTIVE cooldown
    for delta in range(1, POST_EFFECTIVE_COOLDOWN_DAYS + 1):
        st = RebalanceTimelineManager.get_timeline_status(ref_date=eff + timedelta(days=delta))
        assert st["stage"] == "POST_EFFECTIVE", f"Expected POST_EFFECTIVE on day +{delta}"
        assert st["days_since_last_effective"] == delta

    # Day 6 after effective date: transitions to PRE_CUTOFF
    st_after = RebalanceTimelineManager.get_timeline_status(
        ref_date=eff + timedelta(days=POST_EFFECTIVE_COOLDOWN_DAYS + 1)
    )
    assert st_after["stage"] == "PRE_CUTOFF"


def test_progress_is_strictly_monotonic_across_full_cycle():
    q1_2026 = RebalanceTimelineManager.get_quarter_schedule(2026, 1)
    q2_2026 = RebalanceTimelineManager.get_quarter_schedule(2026, 2)

    start_day = q1_2026["effective_date"] + timedelta(days=1)
    end_day = q2_2026["effective_date"]

    prev_progress = -1.0
    stages_seen = set()
    cur = start_day
    while cur <= end_day:
        st = RebalanceTimelineManager.get_timeline_status(ref_date=cur)
        prog = st["progress"]
        assert 0.0 <= prog <= 100.0
        assert prog > prev_progress, f"Non-monotonic progress on {cur}: {prog} <= {prev_progress}"
        prev_progress = prog
        stages_seen.add(st["stage"])
        cur += timedelta(days=1)

    assert prev_progress == 100.0
    assert stages_seen == {
        "POST_EFFECTIVE",
        "PRE_CUTOFF",
        "COMMITTEE_EVALUATION",
        "POST_ANNOUNCEMENT",
    }


def test_trading_days_between_announcement_and_effective_accounts_for_holidays():
    # Regular quarter (March 2025): no NYSE holidays between 1st Fri (Mar 7) and 3rd Fri (Mar 21) -> 10 trading days
    q1_2025 = RebalanceTimelineManager.get_quarter_schedule(2025, 1)
    assert q1_2025["trading_days_announcement_to_effective"] == 10

    # June 2025: Juneteenth falls on Thu Jun 19 between Fri Jun 6 and Fri Jun 20 -> 9 trading days
    q2_2025 = RebalanceTimelineManager.get_quarter_schedule(2025, 2)
    assert q2_2025["trading_days_announcement_to_effective"] == 9

    # June 2026: 3rd Friday is Jun 19 (Juneteenth holiday) -> shifted to Thu Jun 18, 9 trading days
    q2_2026 = RebalanceTimelineManager.get_quarter_schedule(2026, 2)
    assert q2_2026["effective_date"] == date(2026, 6, 18)
    assert is_nyse_trading_day(q2_2026["effective_date"])
    assert q2_2026["trading_days_announcement_to_effective"] == 9
    assert count_trading_days(q2_2026["announcement_date"], q2_2026["effective_date"]) == 9


def test_default_ref_date_returns_valid_status():
    st = RebalanceTimelineManager.get_timeline_status()
    assert isinstance(st["current_date"], date)
    assert st["stage"] in {
        "POST_EFFECTIVE",
        "PRE_CUTOFF",
        "COMMITTEE_EVALUATION",
        "POST_ANNOUNCEMENT",
    }
    assert 0.0 <= st["progress"] <= 100.0
