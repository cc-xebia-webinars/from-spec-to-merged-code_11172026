# Plan: Weekly Booking Allowance

Built from `docs/specs/weekly-allowance.md`. The acceptance tests in `tests/acceptance/test_weekly_allowance.py` are the definition of done; criteria 1, 3, 6, and 7 fail today.

## Slice A: The office week

Files: `roombook/timeutils.py`, and a new `tests/test_week_bounds.py`.

- Add `week_bounds(day: date, tz: ZoneInfo) -> tuple[datetime, datetime]`, next to `day_bounds`. It returns the UTC start and end of the office week that contains `day`, from Monday 00:00 to the next Monday 00:00 in local time.
- Build both ends from local midnights, like `day_bounds`, so the week New York's clocks go back in is 169 hours long.
- Test a normal week and both clock-change weeks.

## Slice B: The allowance check

Files: `roombook/db.py`, and a new `roombook/allowance.py`.

- Add `db.person_bookings(conn, office, booked_by, start_utc, end_utc)`: the bookings one person holds in an office that start inside a window, leaving out cancelled ones.
- In `roombook/allowance.py`, add `WEEKLY_HOURS = 6`, an `AllowanceExceeded` exception, and `check(conn, office, booked_by, start, end, *, ignore_booking_id=None)`. It raises `AllowanceExceeded` with the spec's message when the week's hours plus the new booking come to more than 6.
- It calls `timeutils.week_bounds(day, tz)` from slice A. Slices A and B touch different files, so they can be built at the same time against that signature.

## Slice C: Wire it in

Files: `roombook/slots.py`, `roombook/routes/bookings.py`, and `roombook/series.py`. Needs slices A and B.

- `check_slot` takes a new keyword argument, `booked_by`, and calls `allowance.check` after the clash check, passing `ignore_booking_id` through for moves.
- `create_booking`, `move_booking`, and `series.create` pass `booked_by` and turn `AllowanceExceeded` into a `409`. A series lists each failed occurrence with the allowance message as its reason.

## Checks

- `uv run pytest`: every acceptance test passes, and the 62 existing tests pass unchanged.
- No new dependency, setting, or endpoint.
