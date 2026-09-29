from urllib.parse import quote


def activity_url(activity_name):
    return quote(activity_name, safe="")


def participant_url(email):
    return quote(email, safe="")


def test_root_redirects_to_static_index(client):
    response = client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert {
        "description",
        "schedule",
        "max_participants",
        "participants",
    } <= activities["Chess Club"].keys()


def test_signup_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{activity_url('Chess Club')}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        f"/activities/{activity_url('Unknown Club')}/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        f"/activities/{activity_url('Chess Club')}/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant(client):
    activity = activity_url("Chess Club")
    email = participant_url("michael@mergington.edu")

    response = client.delete(f"/activities/{activity}/participants/{email}")

    assert response.status_code == 200
    assert "michael@mergington.edu" not in client.get("/activities").json()["Chess Club"]["participants"]


def test_remove_participant_rejects_unknown_participant(client):
    response = client.delete(
        f"/activities/{activity_url('Chess Club')}/participants/{participant_url('unknown@mergington.edu')}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_participant_rejects_unknown_activity(client):
    response = client.delete(
        f"/activities/{activity_url('Unknown Club')}/participants/{participant_url('student@mergington.edu')}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
