"""The office week that the weekly allowance is counted in."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from roombook.timeutils import week_bounds

NYC = ZoneInfo("America/New_York")
AMS = ZoneInfo("Europe/Amsterdam")


def test_a_new_york_week_runs_from_monday_midnight_to_monday_midnight():
    start, end = week_bounds(date(2026, 10, 29), NYC)

    assert start == datetime(2026, 10, 26, 4, 0, tzinfo=UTC)
    assert end == datetime(2026, 11, 2, 5, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("day", "tz", "hours"),
    [
        (date(2026, 11, 4), NYC, 168),
        (date(2026, 11, 1), NYC, 169),  # New York's clocks go back on this Sunday
        (date(2026, 10, 25), AMS, 169),  # Amsterdam's clocks go back on this Sunday
        (date(2027, 3, 14), NYC, 167),  # New York's clocks go forward on this Sunday
    ],
)
def test_a_week_is_as_long_as_the_office_clock_says(day, tz, hours):
    start, end = week_bounds(day, tz)

    assert end - start == timedelta(hours=hours)
