import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.mark.django_db
def test_public_policy_and_account_entry(client):
    login = client.get("/accounts/login/").content.decode()
    assert 'href="/accounts/create/"' in login
    assert 'href="/data-policy/"' in login
    assert "Credentials stay" not in login
    policy = client.get("/data-policy/")
    assert policy.status_code == 200
    for text in (
        "installation owner",
        "backup copies",
        "Completion is not mastery",
        "separate choice",
    ):
        assert text in policy.content.decode()
    assert "no-cache" in policy["Cache-Control"]
    assert client.get("/profile/").status_code == 302


@pytest.mark.django_db
def test_registration_labels_match_the_browser_entry_points(client):
    response = client.get("/accounts/create/")
    assert response.status_code == 200
    for field_id, label in (
        ("id_username", "Username:"),
        ("id_password1", "Password:"),
        ("id_password2", "Password confirmation:"),
    ):
        assert f'<label for="{field_id}">{label}</label>' in response.content.decode()


@pytest.mark.django_db
def test_registration_creates_only_an_ordinary_account(client):
    response = client.post(
        "/accounts/create/",
        {
            "username": "new-person",
            "password1": "Unrelated-phrase-83947!",
            "password2": "Unrelated-phrase-83947!",
            "is_staff": "true",
            "is_superuser": "true",
            "next": "https://example.org/",
        },
    )
    assert response.status_code == 302
    assert response.url == "/accounts/login/"
    account = get_user_model().objects.get(username="new-person")
    assert not account.is_staff and not account.is_superuser
    assert account.check_password("Unrelated-phrase-83947!")
    assert "_auth_user_id" not in client.session
    assert client.login(username="new-person", password="Unrelated-phrase-83947!")


@pytest.mark.django_db
def test_invalid_duplicate_and_disabled_registration(client, user, settings):
    data = {"username": user.username, "password1": "short", "password2": "different"}
    assert client.post("/accounts/create/", data).status_code == 200
    assert get_user_model().objects.count() == 1
    settings.ALLOW_REGISTRATION = False
    assert b"closed new registrations" in client.get("/accounts/create/").content
    data["username"] = "blocked"
    client.post("/accounts/create/", data)
    assert not get_user_model().objects.filter(username="blocked").exists()
    client.force_login(user)
    assert client.get("/accounts/create/").url == "/"


@pytest.mark.django_db
def test_registration_requires_csrf_and_does_not_create_developmental_records():
    from growth.models import AssessmentRun, EvidenceEvent, PracticeSprint

    client = Client(enforce_csrf_checks=True)
    response = client.post("/accounts/create/", {"username": "csrf-test"})
    assert response.status_code == 403
    assert not get_user_model().objects.filter(username="csrf-test").exists()
    assert (
        AssessmentRun.objects.count()
        == EvidenceEvent.objects.count()
        == PracticeSprint.objects.count()
        == 0
    )
