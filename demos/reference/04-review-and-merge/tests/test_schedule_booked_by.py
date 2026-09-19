"""The office schedule shows who booked each meeting, for the issue in issues/."""


def test_the_schedule_shows_who_booked_each_meeting(client):
    schedule = client.get("/offices/NYC/schedule", params={"date": "2026-10-27"}).json()

    entry = next(e for e in schedule["bookings"] if e["title"] == "Launch rehearsal")
    assert entry["booked_by"] == "Ava Thompson"
