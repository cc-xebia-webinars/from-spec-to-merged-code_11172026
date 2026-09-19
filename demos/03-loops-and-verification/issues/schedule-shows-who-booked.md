The lobby screen in each office shows the day's schedule from `GET /offices/{code}/schedule`. Reception wants to see who booked each meeting, so they can point visitors to the right person.

## What to change

- Add `booked_by` to each entry in the schedule response, straight after `title`.
- Nothing else about the schedule changes.

## Acceptance criteria

1. `GET /offices/NYC/schedule?date=2026-10-27` lists the Launch rehearsal with `booked_by` set to `Ava Thompson`.
2. Every existing test still passes, unchanged. The new test goes in a new file under `tests/`.

## Constraints

- Keep the change to `roombook/schedule.py`, the `ScheduleEntry` model in `roombook/models.py`, and the new test.
- Don't add a dependency.
