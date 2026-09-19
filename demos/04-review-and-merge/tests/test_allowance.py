"""Rules from docs/specs/weekly-allowance.md that no acceptance criterion covers."""


def test_pending_bookings_count_towards_the_allowance(client):
    # Robert Kim's Quarterly business review on 4 November is pending until a manager confirms it,
    # and it still holds 3 hours of his week in New York.
    response = client.post(
        "/bookings",
        json={
            "room_id": 8,
            "title": "Planning",
            "booked_by": "Robert Kim",
            "start": "2026-11-05T09:00",
            "end": "2026-11-05T12:30",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Robert Kim would go over the weekly allowance of 6 hours in this office."
    )
