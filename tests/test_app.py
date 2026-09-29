from copy import deepcopy
import importlib

import pytest
from fastapi.testclient import TestClient


app_module = importlib.import_module("src.app")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(app_module.activities))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_seeded_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_normalized_email(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "  New.Student@Example.com  "},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up new.student@example.com for Chess Club"
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert "new.student@example.com" in participants


@pytest.mark.parametrize(
    "duplicate_email",
    ["New.Student@example.com", "  NEW.STUDENT@example.COM  "],
)
def test_signup_rejects_duplicate_email_regardless_of_case_or_whitespace(
    client, duplicate_email
):
    signup_url = "/activities/Chess%20Club/signup"
    client.post(signup_url, params={"email": "New.Student@example.com"})

    response = client.post(signup_url, params={"email": duplicate_email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert participants.count("new.student@example.com") == 1


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_accepts_email_case_and_whitespace_variants(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "  MICHAEL@MERGINGTON.EDU  "},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert "michael@mergington.edu" not in participants


def test_remove_participant_returns_404_when_not_registered(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_participant_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"