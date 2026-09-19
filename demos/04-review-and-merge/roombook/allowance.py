"""The weekly allowance: how many hours of bookings one person can hold in an office each week.

The office managers set the allowance to share the rooms out fairly. The spec is
docs/specs/weekly-allowance.md.
"""

import sqlite3
from datetime import datetime, timedelta

from roombook import db
from roombook.offices import OFFICES
from roombook.timeutils import from_db, to_db, week_bounds

WEEKLY_HOURS = 6


class AllowanceExceeded(Exception):
    """The booking would take its owner over the weekly allowance in this office."""


def check(
    conn: sqlite3.Connection,
    office: str,
    booked_by: str,
    start: datetime,
    end: datetime,
    *,
    ignore_booking_id: int | None = None,
) -> None:
    """Raise AllowanceExceeded if booking start to end would put booked_by over the allowance.

    start and end carry the office's time zone. The week is the office's week, so a Sunday evening
    booking in New York counts towards the week it's in locally, even when it's already Monday in
    UTC. A booking that's being moved passes its own id, so it doesn't count against itself.
    """
    tz = OFFICES[office].tz
    week_start, week_end = week_bounds(start.astimezone(tz).date(), tz)
    booked = timedelta()
    for row in db.person_bookings(conn, office, booked_by, to_db(week_start), to_db(week_end)):
        if row["id"] != ignore_booking_id:
            booked += from_db(row["end_utc"]) - from_db(row["start_utc"])
    if booked + (end - start) > timedelta(hours=WEEKLY_HOURS):
        raise AllowanceExceeded(
            f"{booked_by} would go over the weekly allowance of {WEEKLY_HOURS} hours in this office."
        )
