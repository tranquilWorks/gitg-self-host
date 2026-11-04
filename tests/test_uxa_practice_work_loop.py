from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from growth.forms import PracticeCheckInForm
from growth.models import EvidenceEvent, PracticeProtocol, PracticeSprint
from growth.practice_presentation import (
    check_in_observations,
    present_check_in_form,
    readable_result,
)
from growth.services.evidence import build_privacy_safe_evidence_export, verify_evidence_event
from growth.services.practice import current_sprint_for, save_check_in
from growth.services.profile import build_profile_summary
from tests.test_composite_score_state import _partial_closeout
from tests.test_evidence_audit import _check_in_data
from tests.test_practice_workflow import create_sprint


@pytest.mark.django_db
def test_active_identity_is_owner_scoped_and_same_on_every_entry(client, user, seeded):
    client.force_login(user)
    sprint = create_sprint(user)
    url = reverse("growth:practice-sprint", args=[sprint.pk])
    browse = client.get("/practices/", {"browse": "1", "q": sprint.protocol.name})
    assert browse.context["current_sprint"] == sprint
    assert browse.context["explorer"]["page"].object_list[0].pk == sprint.protocol_id
    assert all(row["protocol"].pk != sprint.protocol_id for row in browse.context["suggestions"])
    assert f'data-attempt="{sprint.pk}"'.encode() in browse.content
    assert (
        client.get(reverse("growth:practice-recommendation", args=[sprint.protocol.slug])).url
        == url
    )
    for path in ("/", "/weekly/", url):
        response = client.get(path)
        assert response.status_code == 200
        assert sprint.protocol.name.encode() in response.content
    guide = client.get(reverse("growth:practice-guide", args=[sprint.protocol.slug]))
    assert guide.status_code == 200
    assert f'data-attempt="{sprint.pk}"'.encode() in guide.content
    assert url.encode() in guide.content
    other = get_user_model().objects.create_user(username="other-practice-owner")
    client.force_login(other)
    assert client.get(url).status_code == 404
    assert str(sprint.pk).encode() not in client.get("/practices/").content


@pytest.mark.django_db
def test_completion_updates_current_and_recomputes_not_reranks(client, user, seeded):
    client.force_login(user)
    sprint, _ = _partial_closeout(user)
    assert current_sprint_for(user) is None
    browser = client.get("/practices/")
    assert browser.context["last_completed"] == sprint
    assert browser.context["current_sprint"] is None
    assert tuple(browser.context["ranked_protocols"]) == tuple(
        build_profile_summary(user).recommendations
    )
    assert b"browser-current-practice" not in browser.content
    assert b"Last completed practice" in browser.content
    assert b"Choose your next practice" in client.get("/").content


@pytest.mark.django_db
def test_display_choices_and_first_week_do_not_rewrite_contracts(client, user, seeded):
    client.force_login(user)
    sprint = create_sprint(user)
    before = list(PracticeProtocol.objects.values())
    form = PracticeCheckInForm(sprint=sprint)
    choices = {
        key: [value for value, _ in form.fields[key].choices]
        for key in ("support_level", "context_comparison", "evidence_direction")
    }
    present_check_in_form(form)
    assert choices == {key: [value for value, _ in form.fields[key].choices] for key in choices}
    response = client.get(reverse("growth:practice-sprint", args=[sprint.pk]))
    assert response.context["end_date"] == sprint.start_date + timedelta(days=6)
    assert b"not an automatic deadline" in response.content
    assert list(PracticeProtocol.objects.values()) == before
    assert sprint.protocol.duration_days == 14


@pytest.mark.django_db
def test_readable_submitted_views_preserve_exact_event_and_export(client, user, seeded):
    client.force_login(user)
    sprint = create_sprint(user)
    check_in = save_check_in(
        sprint=sprint,
        cleaned_data=_check_in_data(
            sprint.protocol.actions.first(),
            action_attempted=True,
            action_completed=False,
            moved_beyond_transactional=True,
            internal_resistance=0,
            note="PRIVATE-READABLE-NOTE",
        ),
        submit=True,
    )
    event = EvidenceEvent.objects.get(check_in=check_in)
    before = build_privacy_safe_evidence_export(user)
    for path in (
        "/evidence/",
        reverse("growth:practice-check-in-detail", args=[sprint.pk, check_in.pk]),
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert b"Technical audit details" not in response.content
        assert b"Base evidence mass" not in response.content
        assert b"GG-EVIDENCE-1.0" not in response.content
        assert b"Evidence reading" not in response.content
    detail = client.get(reverse("growth:practice-check-in-detail", args=[sprint.pk, check_in.pk]))
    assert b"PRIVATE-READABLE-NOTE" in detail.content
    assert b"None" in detail.content  # Explicit zero is still a recorded response.
    assert b"Repetition" not in detail.content
    assert b"Download minimized evidence JSON" not in client.get("/evidence/").content
    assert b"Download minimized evidence JSON" in client.get("/account/data/").content
    assert build_privacy_safe_evidence_export(user) == before
    verify_evidence_event(event)
    assert EvidenceEvent.objects.count() == 1
    assert PracticeSprint.objects.count() == 1


def test_structured_result_display_keeps_false_zero_and_named_opportunities():
    assert readable_result(False) == "No"
    assert readable_result(0) == "0"
    assert readable_result({"numerator": 0, "denominator": 3}) == "0 of 3 opportunities"
    assert readable_result({"amount": 0, "unit": "minutes"}) == "0 minutes"


def test_display_uses_immutable_event_rules_not_later_action_rules():
    from types import SimpleNamespace

    check_in = SimpleNamespace(
        sprint=SimpleNamespace(protocol=SimpleNamespace(setup_copy={})),
        action=SimpleNamespace(evidence_rules={"schema_version": "later-unrelated-version"}),
        user_initiated=False,
        follow_up_question_asked=True,
        internal_resistance=None,
        expected_reciprocity=None,
        observed_reciprocity=None,
        typed_observations=[],
    )
    event = SimpleNamespace(
        input_snapshot={
            "evidence_rules": {
                "schema_version": "practice-observation-v1",
                "primary_markers": ["user_initiated"],
                "supporting_markers": ["follow_up_question_asked"],
            }
        }
    )
    assert check_in_observations(check_in, event) == [
        {"label": "Follow up question asked", "value": "Yes"},
        {"label": "User initiated", "value": "Not marked"},
    ]


@pytest.mark.django_db
def test_typed_observations_display_without_legacy_rule_parsing(client, user, seeded):
    from datetime import date

    from growth.services.practice import start_practice
    from tests.test_all_active_runtime import _typed_observations

    protocol = PracticeProtocol.objects.get(
        stable_id="PRACTICE-COMP-0101-CONCEPTIONS-OF-FLOURISHING-01"
    )
    assert protocol.actions.first().evidence_rules["schema_version"] == "typed-evidence-rules-v1"
    sprint = start_practice(
        user=user, protocol=protocol, person_or_context="Synthetic typed", start_date=date.today()
    )
    action = protocol.actions.first()
    values = _check_in_data(
        action, user_initiated=False, typed_observations=_typed_observations(action)
    )
    check_in = save_check_in(sprint=sprint, cleaned_data=values, submit=True)
    event = EvidenceEvent.objects.get(check_in=check_in)
    before = build_privacy_safe_evidence_export(user)
    client.force_login(user)
    response = client.get(reverse("growth:practice-check-in-detail", args=[sprint.pk, check_in.pk]))
    assert response.status_code == 200
    assert response.context["observations"]
    assert b"Technical audit details" not in response.content
    verify_evidence_event(event)
    assert build_privacy_safe_evidence_export(user) == before
