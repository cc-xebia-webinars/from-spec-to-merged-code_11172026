"""The checks every new or moved booking goes through before it's saved."""

import sqlite3
from datetime import datetime

from roombook import allowance, availability, policies
from roombook.offices import OFFICES
from roombook.policies import PolicyError
from roombook.timeutils import localize


class SlotTaken(Exception):
    """The room is already booked for part of the requested time."""


def check_slot(
    conn: sqlite3.Connection,
    room: sqlite3.Row,
    start: datetime,
    end: datetime,
    *,
    now: datetime,
    ignore_booking_id: int | None = None,
    booked_by: str | None = None,
) -> tuple[datetime, datetime]:
    """Check a requested time for a room, and return it with the office's time zone attached.

    start and end are the wall-clock times from the request. Raises PolicyError if the time
    breaks a booking rule, and SlotTaken if another booking is in the way. When booked_by is
    given, it also checks the weekly allowance and raises allowance.AllowanceExceeded.
    """
    if start.tzinfo is not None or end.tzinfo is not None:
        raise PolicyError("Send times in the office's local time, without an offset.")
    tz = OFFICES[room["office"]].tz
    start, end = localize(start, tz), localize(end, tz)
    policies.check_booking(start, end, now=now)
    clashes = availability.conflicts(conn, room["id"], start, end, ignore_booking_id)
    if clashes:
        raise SlotTaken(f"{room['name']} is already booked then: {clashes[0]['title']}.")
    if booked_by is not None:
        allowance.check(
            conn, room["office"], booked_by, start, end, ignore_booking_id=ignore_booking_id
        )
    return start, end
