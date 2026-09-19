# Reference: The Finished Run and the Team Build

This folder holds two things that live outside the demo folders on purpose:

- `04-review-and-merge/` is a finished version of Roombook at the end of [Demo 4](../04-review-and-merge/README.md), after both pull requests are merged. It's here so no agent finds it while it's working on a demo.
- `team-build/` is the agent team's first pass at the feature, which [Demo 3](../03-loops-and-verification/README.md) copies over its code. It's here so it isn't part of the repository Demo 3 publishes.

## The Finished Run

| What | Where |
|------|-------|
| The weekly allowance | `04-review-and-merge/roombook/allowance.py` |
| The office week it's counted in | `week_bounds` in `04-review-and-merge/roombook/timeutils.py` |
| Where every booking, move, and occurrence is checked | `check_slot` in `04-review-and-merge/roombook/slots.py` |
| One test per acceptance criterion | `04-review-and-merge/tests/acceptance/test_weekly_allowance.py` |
| The test for pending bookings, added after the verifier's review | `04-review-and-merge/tests/test_allowance.py` |
| The cloud agent's change to the office schedule | `booked_by` in `04-review-and-merge/roombook/schedule.py`, and `tests/test_schedule_booked_by.py` |

The detail to look for is in `week_bounds`. Both ends of the week come from local midnights in the office's time zone, the same way `day_bounds` works for a day. That's why a booking at 19:00 on Sunday 1 November in New York counts towards the week of 26 October, even though it's already Monday in UTC. Working the week out from the UTC date puts it in the following week, and the test for criterion 3 catches it.

The fix pull request from Copilot's code review isn't included, because its content depends on what the review found.

To run the finished version's tests, open a terminal in this folder's `04-review-and-merge` subfolder and install its dependencies:

```
uv sync
```

Then run the tests:

```
uv run pytest
```

All 76 pass: the 62 that Roombook started with, unchanged, the 7 acceptance tests, 5 tests for the office week, the test for pending bookings, and the test for the schedule change.

## The Team Build for Demo 3

`team-build/` holds only the files the agent team changed or added, in the same layout as a demo folder, including its `pyproject.toml` and `uv.lock`. Demo 3's Step 5 copies it over the code on a new branch. It's a plausible first pass of the kind agents produce: it handles new bookings, but not moves or series, so two acceptance tests fail. It also has problems that no test catches, which Demo 3's verifier finds, and Demo 3's Step 10 lists them. Don't use it as an example of finished code; the finished version is in `04-review-and-merge/`.
