import copy
from urllib.parse import quote

import pytest 
from fastapi.testclient import TestClient

from src.app import app, activities as activity_db

INITIAL_ACTIVITIES = copy.deepcopy(activity_db)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activity_db.clear()
    activity_db.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    email = "testuser@example.com"
    response = client.post(f"/activities/{quote('Chess Club')}/signup?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activity_db["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    existing_email = "michael@mergington.edu"
    response = client.post(f"/activities/{quote('Chess Club')}/signup?email={quote(existing_email)}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    email = "tempuser@example.com"
    activity_db["Chess Club"]["participants"].append(email)

    response = client.delete(f"/activities/{quote('Chess Club')}/participants?email={quote(email)}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Chess Club"
    assert email not in activity_db["Chess Club"]["participants"]


def test_remove_nonexistent_participant():
    response = client.delete(f"/activities/{quote('Chess Club')}/participants?email={quote('missing@example.com')}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
