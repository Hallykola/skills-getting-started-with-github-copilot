from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Should return the in-memory activities mapping
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    # Use a unique test email to avoid colliding with existing participants
    email = "test.user+pytest@example.com"

    # Ensure email not already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up participant
    signup_url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    r = client.post(signup_url)
    assert r.status_code == 200, r.text
    j = r.json()
    assert "Signed up" in j.get("message", "")

    # Verify participant present in GET /activities
    r2 = client.get("/activities")
    assert r2.status_code == 200
    data = r2.json()
    assert email in data[activity]["participants"]

    # Remove the participant
    delete_url = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    r3 = client.delete(delete_url)
    assert r3.status_code == 200, r3.text
    j3 = r3.json()
    assert "Removed" in j3.get("message", "")

    # Verify removal
    r4 = client.get("/activities")
    assert r4.status_code == 200
    data2 = r4.json()
    assert email not in data2[activity]["participants"]
