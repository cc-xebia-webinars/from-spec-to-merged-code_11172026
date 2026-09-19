"""The allowance summary for one person."""


def test_shows_the_hours_booked_and_left_in_the_week(client):
    response = client.get(
        "/people/Ava Thompson/allowance", params={"office": "NYC", "date": "2026-10-29"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "booked_by": "Ava Thompson",
        "office": "NYC",
        "week_start": "2026-10-26",
        "hours_booked": 4.5,
        "hours_left": 1.5,
    }


def test_an_unknown_office_is_not_found(client):
    response = client.get(
        "/people/Ava Thompson/allowance", params={"office": "LON", "date": "2026-10-29"}
    )

    assert response.status_code == 404
