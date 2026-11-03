import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.urls import reverse


def test_actual_progressive_script_error_focus_and_draft_preservation():
    import subprocess
    from pathlib import Path

    result = subprocess.run(
        ["node", str(Path(__file__).with_name("uxa_personal_os_client.cjs"))],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "simulation only" in result.stdout


@pytest.mark.django_db
def test_installation_separates_ordinary_and_operator_information(client, user):
    client.force_login(user)
    response = client.get("/account/installation/")
    assert response.status_code == 200
    assert b"contact your instance operator" in response.content
    assert b"docker compose exec" not in response.content
    assert b"Startup choice" not in response.content
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    response = client.get("/account/installation/")
    assert response.status_code == 200
    assert b"Installed revision" in response.content
    assert b"docker compose exec" in response.content


@pytest.mark.django_db
@pytest.mark.parametrize("included,expected_open", [(0, False), (1, True)])
def test_research_controls_are_collapsed_until_participation(user, included, expected_open):
    request = RequestFactory().get("/account/data/")
    request.user = user
    html = render_to_string(
        "growth/data_management.html",
        {
            "calibration_summary": {"assessment_run_count": included},
        },
        request=request,
    )
    tag = '<details class="panel data-management-panel"'
    assert (tag + " open>") in html if expected_open else (tag + ">") in html
    assert "Your data choices" in html
    assert "Nothing is sent automatically" in html


@pytest.mark.django_db
def test_feedback_handoff_does_not_attach_private_records(user):
    request = RequestFactory().get("/account/pilot-feedback/")
    request.user = user
    html = render_to_string("growth/pilot_feedback.html", {}, request=request)
    assert 'https://github.com/tranquilWorks/gitg-self-host/issues/new"' in html
    assert "does not send it to the project" in html
    assert "nothing from this account is attached automatically" in html


@pytest.mark.django_db
def test_saved_summary_edit_and_profile_stage_preserve_storage(client, user, seeded):
    from growth.models import PersonalOSRevision
    from tests.test_personal_os_browser import personal_os_post

    client.force_login(user)
    page = client.get(reverse("growth:personal-os"))
    assert page.status_code == 200
    assert not page.context["show_summary"]
    assert not page.context["reusable_sources"]
    run = page.context["assessment_run"]
    response = client.post(
        reverse("growth:personal-os"),
        personal_os_post(epoch=run.pk, mission="Help my family make time for each other"),
    )
    assert response.status_code == 302
    assert PersonalOSRevision.objects.filter(user=user).count() == 1
    page = client.get(reverse("growth:personal-os"))
    assert page.context["show_summary"]
    assert b"Help my family" in page.content
    assert b'name="mission_value"' not in page.content
    edit = client.get(reverse("growth:personal-os") + "?edit=1")
    assert not edit.context["show_summary"]
    assert b"Help my family" in edit.content
    assert PersonalOSRevision.objects.filter(user=user).count() == 1
    profile = client.get(reverse("growth:profile"))
    assert b"Your starting point and progress" in profile.content
    assert b"weekly-profile-heading" not in profile.content
    assert b"current-state-heading" not in profile.content
    assert "no-store" in profile["Cache-Control"]


@pytest.mark.django_db
def test_old_context_route_preserves_filters_in_local_redirect(client, user, seeded):
    client.force_login(user)
    response = client.get("/personal-os/practices/?view=deferred")
    assert response.status_code == 302
    assert response.url == "/practices/?view=deferred&review=1"
    assert client.get(response.url).status_code == 200
    assert client.post("/personal-os/practices/").status_code == 405
