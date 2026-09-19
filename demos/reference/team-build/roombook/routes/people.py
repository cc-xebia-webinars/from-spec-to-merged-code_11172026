"""What each person has booked."""

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from roombook import allowance, db
from roombook.deps import Conn
from roombook.offices import OFFICES
from roombook.timeutils import from_db, to_db, week_bounds

router = APIRouter(prefix="/people", tags=["people"])


class Allowance(BaseModel):
    booked_by: str
    office: str
    week_start: date
    hours_booked: float
    hours_left: float


@router.get("/{name}/allowance", response_model=Allowance)
def person_allowance(
    name: str, office: str, day: Annotated[date, Query(alias="date")], conn: Conn
) -> Allowance:
    """How much of their weekly allowance someone has used, so they can plan their bookings."""
    office = office.upper()
    if office not in OFFICES:
        raise HTTPException(404, "Office not found.")
    start, end = week_bounds(day, OFFICES[office].tz)
    rows = db.person_bookings(conn, office, name, to_db(start), to_db(end))
    booked = sum(
        (from_db(row["end_utc"]) - from_db(row["start_utc"]) for row in rows), timedelta()
    ) / timedelta(hours=1)
    return Allowance(
        booked_by=name,
        office=office,
        week_start=day - timedelta(days=day.weekday()),
        hours_booked=booked,
        hours_left=max(allowance.WEEKLY_HOURS - booked, 0),
    )
