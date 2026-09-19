# Spec: Weekly Booking Allowance

## Goal

A few people book far more meeting-room time than anyone else, and the office managers want to share the rooms out more fairly. Each person gets a weekly allowance of booked hours in each office.

## Context

- Every new or moved booking, and every occurrence of a series, goes through `check_slot` in `roombook/slots.py`, which applies the booking rules and checks for clashes.
- Times in requests are local to the room's office. Both offices change their clocks during the sample data: Amsterdam on Sunday 25 October and New York on Sunday 1 November 2026.
- The `roombook-facts` MCP server answers questions about the sample data and the clock changes. Check facts there rather than working them out by hand.

## The Rule

- A person can hold at most **6 hours** of bookings in each office in any one week. A person is identified by the `booked_by` name, exactly as written.
- A week runs from Monday 00:00 to the next Monday 00:00 in the office's local time. A booking belongs to the week its start falls in.
- Confirmed and pending bookings both count, because a pending boardroom booking still holds the room. Cancelled bookings don't count.
- The allowance applies when a booking is made, when it's moved, and to every occurrence of a series. A booking that's being moved doesn't count against itself.
- The allowance is checked after the booking rules and the clash check. A request that would take someone over the allowance gets a `409`, and its `detail` is: `<booked_by> would go over the weekly allowance of 6 hours in this office.` In a series, that message is the `reason` for each occurrence that fails.

## Constraints

- Apply the allowance through `check_slot`, so new bookings, moves, and series all get it. Put the allowance logic in a new module, `roombook/allowance.py`, and the week calculation in `roombook/timeutils.py`, next to `day_bounds`.
- The allowance is 6 hours for everyone, set by the office managers. It isn't configurable.
- Don't add a dependency, a setting, or an endpoint.
- Don't change the booking rules in `roombook/policies.py`, the clash check, or any existing test.

## Acceptance Criteria

1. Ava Thompson booking Chelsea (room 7) on Thursday 29 October 2026 from 13:00 to 15:00 is rejected with `409` and the allowance message, because her week in New York would reach 6.5 hours. Nothing is saved.
2. The same booking from 13:00 to 14:30 is accepted with `201`, because it brings her week to exactly 6 hours.
3. Ava booking Hudson (room 6) on Sunday 1 November from 19:00 to 21:00 is rejected with `409` and the allowance message. In New York time that evening is still in the week of 26 October, even though it's already Monday 2 November in UTC.
4. Ava booking Herengracht (room 1) in Amsterdam on Thursday 29 October from 14:00 to 16:00 is accepted with `201`, because each office has its own allowance.
5. After Ava's Partner workshop on 30 October is cancelled, the booking from criterion 1 is accepted with `201`.
6. Moving Ava's Town hall dry run on 3 November to Thursday 29 October from 13:00 to 15:00 is rejected with `409` and the allowance message. Moving her Partner workshop on 30 October to 13:00 to 16:00 the same day is accepted with `200`, because a booking doesn't count against itself.
7. A three-week series for Ava in Chelsea on Thursdays from 29 October, 13:00 to 15:00, is rejected with `409`. The only failed occurrence listed is 29 October, with the allowance message as its reason, and nothing is saved.
8. Every existing test still passes, unchanged, and each criterion above has a test in `tests/acceptance/test_weekly_allowance.py`.

## Out of Scope

- A way to see how many hours someone has left in a week.
- Different allowances for different people, rooms, or offices.
- Counting hours across offices, or notifying anyone.
- Changing bookings that already exist. Rebuild the sample database with `uv run python -m roombook.seed --reset`.
