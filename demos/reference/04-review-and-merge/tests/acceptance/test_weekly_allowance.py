"""Acceptance tests for docs/specs/weekly-allowance.md, one per acceptance criterion.

The expected values come from the spec, and the sample data was checked with the roombook-facts
MCP server: Ava Thompson holds 4.5 hours of bookings in New York in the week of 26 October 2026,
and New York's clocks go back on Sunday 1 November.

Criterion 8, that every existing test still passes unchanged, is checked by running the whole suite.
"""

ALLOWANCE_MESSAGE = "Ava Thompson would go over the weekly allowance of 6 hours in this office."


def book(client, room_id, start, end, title="Planning"):
    return client.post(
        "/bookings",
        json={
            "room_id": room_id,
            "title": title,
            "booked_by": "Ava Thompson",
            "start": start,
            "end": end,
        },
    )


def booking_id(client, room_id, day, title):
    """Find an existing booking through the API, the way a person would."""
    bookings = client.get(f"/rooms/{room_id}/bookings", params={"day": day}).json()
    return next(b["id"] for b in bookings if b["title"] == title)


def titles_in_room(client, room_id, day):
    return [
        b["title"] for b in client.get(f"/rooms/{room_id}/bookings", params={"day": day}).json()
    ]


def test_criterion_1_a_booking_over_the_allowance_is_rejected(client):
    """Ava Thompson booking Chelsea (room 7) on Thursday 29 October 2026 from 13:00 to 15:00 is
    rejected with 409 and the allowance message, because her week in New York would reach 6.5
    hours. Nothing is saved."""
    response = book(client, 7, "2026-10-29T13:00", "2026-10-29T15:00")

    assert response.status_code == 409
    assert response.json()["detail"] == ALLOWANCE_MESSAGE
    assert "Planning" not in titles_in_room(client, 7, "2026-10-29")


def test_criterion_2_a_booking_that_reaches_exactly_six_hours_is_accepted(client):
    """The same booking from 13:00 to 14:30 is accepted with 201, because it brings her week to
    exactly 6 hours."""
    response = book(client, 7, "2026-10-29T13:00", "2026-10-29T14:30")

    assert response.status_code == 201


def test_criterion_3_the_week_is_the_offices_local_week(client):
    """Ava booking Hudson (room 6) on Sunday 1 November from 19:00 to 21:00 is rejected with 409 and
    the allowance message. In New York time that evening is still in the week of 26 October, even
    though it's already Monday 2 November in UTC."""
    response = book(client, 6, "2026-11-01T19:00", "2026-11-01T21:00")

    assert response.status_code == 409
    assert response.json()["detail"] == ALLOWANCE_MESSAGE


def test_criterion_4_each_office_has_its_own_allowance(client):
    """Ava booking Herengracht (room 1) in Amsterdam on Thursday 29 October from 14:00 to 16:00 is
    accepted with 201, because each office has its own allowance."""
    response = book(client, 1, "2026-10-29T14:00", "2026-10-29T16:00")

    assert response.status_code == 201


def test_criterion_5_cancelled_bookings_dont_count(client):
    """After Ava's Partner workshop on 30 October is cancelled, the booking from criterion 1 is
    accepted with 201."""
    workshop = booking_id(client, 10, "2026-10-30", "Partner workshop")
    assert client.delete(f"/bookings/{workshop}").status_code == 204

    response = book(client, 7, "2026-10-29T13:00", "2026-10-29T15:00")

    assert response.status_code == 201


def test_criterion_6_moves_count_but_a_booking_doesnt_count_against_itself(client):
    """Moving Ava's Town hall dry run on 3 November to Thursday 29 October from 13:00 to 15:00 is
    rejected with 409 and the allowance message. Moving her Partner workshop on 30 October to 13:00
    to 16:00 the same day is accepted with 200, because a booking doesn't count against itself."""
    town_hall = booking_id(client, 10, "2026-11-03", "Town hall dry run")
    workshop = booking_id(client, 10, "2026-10-30", "Partner workshop")

    rejected = client.patch(
        f"/bookings/{town_hall}", json={"start": "2026-10-29T13:00", "end": "2026-10-29T15:00"}
    )
    accepted = client.patch(
        f"/bookings/{workshop}", json={"start": "2026-10-30T13:00", "end": "2026-10-30T16:00"}
    )

    assert rejected.status_code == 409
    assert rejected.json()["detail"] == ALLOWANCE_MESSAGE
    assert accepted.status_code == 200


def test_criterion_7_a_series_is_rejected_when_one_week_is_over(client):
    """A three-week series for Ava in Chelsea on Thursdays from 29 October, 13:00 to 15:00, is
    rejected with 409. The only failed occurrence listed is 29 October, with the allowance message
    as its reason, and nothing is saved."""
    response = client.post(
        "/bookings/series",
        json={
            "room_id": 7,
            "title": "Planning",
            "booked_by": "Ava Thompson",
            "start": "2026-10-29T13:00",
            "end": "2026-10-29T15:00",
            "weeks": 3,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == [{"start": "2026-10-29T13:00", "reason": ALLOWANCE_MESSAGE}]
    for day in ("2026-10-29", "2026-11-05", "2026-11-12"):
        assert "Planning" not in titles_in_room(client, 7, day)
