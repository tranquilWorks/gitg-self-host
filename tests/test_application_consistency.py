from unittest.mock import patch

import pytest
from django import forms
from django.core.exceptions import ValidationError
from django.template import Context
from django.test import Client, RequestFactory

from growth.models import AssessmentRun
from growth.templatetags.presentation import application_navigation, form_error_summary
from growth.views_errors import server_error


@pytest.mark.parametrize(
    ("path", "label"),
    [
        ("/", "Home"),
        ("/personal-os/practices/example/context/", "Personal OS"),
        ("/practices/example/direction/", "Practices"),
        ("/practice-sprints/example/", "Practices"),
        ("/weekly/plans/example/", "Weekly"),
        ("/history/periods/example/", "History"),
        ("/profile/", "Profile"),
        ("/assessment/", "Assessment"),
        ("/evidence/", "Evidence"),
        ("/accounts/password-change/", "Account"),
        ("/account/pilot-feedback/", "Feedback"),
    ],
)
def test_navigation_has_one_correct_current_section(path, label):
    context = application_navigation({"request": RequestFactory().get(path)})
    current = [
        link["label"] for link in context["primary"] + context["secondary"] if link["current"]
    ]
    assert current == [label]
    assert len(context["primary"]) == 6
    assert context["more_current"] == (
        label if label in {"Assessment", "Evidence", "Account", "Feedback"} else ""
    )


def test_error_summary_identifies_controls_without_repeating_bound_forms():
    class ExampleForm(forms.Form):
        mission = forms.CharField(label="Mission")
        token = forms.CharField(widget=forms.HiddenInput)

    form = ExampleForm({})
    form.add_error(None, "Review your choices.")
    rows = form_error_summary(Context({"form": form, "same_form": form, "unbound": ExampleForm()}))[
        "form_errors"
    ]
    assert len(rows) == 3
    assert rows[0] == {
        "target": "id_mission",
        "label": "Mission",
        "message": "This field is required.",
    }
    assert all(not row["target"] for row in rows[1:])


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,target",
    [
        ("/personal-os/", "/personal-os/"),
        ("/weekly/", "/weekly/"),
        ("/history/reuse/", "/history/"),
    ],
)
def test_invalid_html_actions_recover_without_echoing_values_or_writing(
    client, user, seeded, url, target
):
    client.force_login(user)
    before = list(AssessmentRun.objects.values())
    response = client.post(
        url,
        {"form_type": "invalid", "intent": "invalid", "mission_value": "PRIVATE-UNTRUSTED-VALUE"},
    )
    # No earlier period is a normal, safe redirect from the reuse shortcut.
    assert response.status_code in {302, 400}
    if response.status_code == 400:
        assert f'href="{target}"' in response.content.decode()
        assert b"PRIVATE-UNTRUSTED-VALUE" not in response.content
        assert "no-store" in response["Cache-Control"]
    assert list(AssessmentRun.objects.values()) == before


@pytest.mark.django_db
def test_conflict_and_missing_pages_have_safe_navigation(client, user, seeded, settings):
    settings.DEBUG = False
    client.force_login(user)
    with patch(
        "growth.views_personal_os.PersonalOSRevision.objects.filter", side_effect=None
    ) as query:
        row = type(
            "Corrupt",
            (),
            {
                "full_clean": lambda self: (_ for _ in ()).throw(
                    ValidationError("PRIVATE-CORRUPT-VALUE")
                )
            },
        )()
        query.return_value.order_by.return_value = [row]
        response = client.get("/personal-os/")
    assert response.status_code == 409
    assert b"PRIVATE-CORRUPT-VALUE" not in response.content
    assert b'href="/personal-os/"' in response.content
    missing = client.get("/history/periods/not-owned-or-missing/")
    assert missing.status_code == 404
    assert b"This page is unavailable." in missing.content
    assert b"not-owned-or-missing" not in missing.content
    assert "no-store" in missing["Cache-Control"]


@pytest.mark.django_db
def test_csrf_recovery_preserves_assessment_json_and_never_echoes_inputs(user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    html = client.post("/personal-os/", {"mission_value": "PRIVATE-CSRF-VALUE"})
    assert html.status_code == 403
    assert b"PRIVATE-CSRF-VALUE" not in html.content
    assert b'href="/personal-os/"' in html.content
    api = client.post("/assessment/runs/", "{}", content_type="application/json")
    assert api.status_code == 403
    assert "session could not be verified" in api.json()["error"]


@pytest.mark.django_db
def test_server_error_has_no_database_dependency_or_exception_details(django_assert_num_queries):
    with django_assert_num_queries(0):
        response = server_error(RequestFactory().get("/PRIVATE-PATH/"))
    assert response.status_code == 500
    assert b"Temporarily unavailable." in response.content
    assert b"PRIVATE-PATH" not in response.content
    assert "no-store" in response["Cache-Control"]
