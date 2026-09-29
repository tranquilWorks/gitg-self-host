from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from growth.domain.personal_os import AUDIT_PROMPT_IDS, IDENTITY_SECTION_IDS
from growth.models import (
    AssessmentContext,
    AssessmentRun,
    PersonalOSRevision,
    PracticeContext,
    WeeklyExecutionPlan,
)
from growth.services.assessment import persist_assessment_run
from growth.services.context import record_context_bundle
from growth.services.history import REUSE_MAX_AGE, confirm_reuse, preview_reuse, reuse_state
from growth.services.personal_os import record_personal_os_revision
from growth.services.practice import transition_sprint
from growth.services.weekly_followup import historical_plan, save_current_plan, save_plan_review
from tests.test_assessment_integration import golden_payload
from tests.test_weekly_execution import _nonweekly_state, _sprint, _submitted_evidence
from tests.test_weekly_followup import plan_for

pytestmark = pytest.mark.django_db


def save_intentions(
    user,
    run,
    mission="PRIVATE-OLDER-MISSION",
    capacity=2,
    principle="Keep promises",
    audit_text="PRIVATE-DATED-OBSERVATION",
):
    unknown = {"state": "unknown", "value": None}
    identity = {key: deepcopy(unknown) for key in IDENTITY_SECTION_IDS}
    identity["mission"] = {"state": "provided", "value": mission}
    identity["principles"] = {"state": "provided", "value": [principle]}
    audit = {key: deepcopy(unknown) for key in AUDIT_PROMPT_IDS}
    audit["current_truth"] = {"state": "provided", "value": audit_text}
    personal = record_personal_os_revision(
        user=user, assessment_run=run, identity_sections=identity, audit_responses=audit
    ).revision
    context = record_context_bundle(
        user=user,
        assessment_run=run,
        assessment_factors={
            "season": {"state": "provided", "value": "foundation"},
            "capacity": {"state": "provided", "value": capacity},
        },
    ).assessment_context
    return personal, context


@pytest.fixture
def periods(user, seeded):
    sprint = _sprint(user)
    source = sprint.assessment_run
    save_intentions(user, source)
    target, _ = persist_assessment_run(user, golden_payload())
    return user, source, target, sprint


def test_selected_reuse_is_previewed_atomic_and_preserves_unselected_state(client, periods):
    user, source, target, sprint = periods
    save_intentions(
        user,
        target,
        "CURRENT-MISSION",
        4,
        principle="Protect recovery",
        audit_text="CURRENT-OBSERVATION",
    )
    old_records = list(PersonalOSRevision.objects.filter(assessment_run=source).values())
    before = _nonweekly_state(user, sprint)
    client.force_login(user)
    url = reverse("history-reuse", args=[source.pk])
    page = client.get(url)
    assert page.status_code == 200
    assert not page.context["form"]["selected"].value()
    assert b"PRIVATE-OLDER-MISSION" in page.content
    assert b"PRIVATE-DATED-OBSERVATION" not in page.content
    response = client.post(url, {"intent": "preview", "selected": ["mission", "capacity"]})
    assert response.status_code == 200
    assert b"CURRENT-MISSION" in response.content
    assert PersonalOSRevision.objects.filter(assessment_run=target).count() == 1
    token = response.context["confirmation"].initial["token"]
    assert "PRIVATE-OLDER-MISSION" not in token
    assert client.post(url, {"intent": "confirm", "token": token}).status_code == 302
    latest = PersonalOSRevision.objects.filter(assessment_run=target).latest("revision")
    assert latest.mission_value == "PRIVATE-OLDER-MISSION"
    assert latest.current_truth_value == "CURRENT-OBSERVATION"
    assert latest.principles_value == ["Protect recovery"]
    assert (
        AssessmentContext.objects.filter(assessment_run=target).latest("revision").capacity_value
        == 2
    )
    assert list(PersonalOSRevision.objects.filter(assessment_run=source).values()) == old_records
    assert _nonweekly_state(user, sprint) == before
    assert not PracticeContext.objects.filter(assessment_run=target).exists()
    assert client.post(url, {"intent": "confirm", "token": token}).status_code == 409


def test_new_target_does_not_copy_audit_or_unselected_values(periods):
    user, source, target, _ = periods
    _, token = preview_reuse(user, source, ["mission"])
    confirm_reuse(user, token)
    row = PersonalOSRevision.objects.get(assessment_run=target)
    assert row.mission_state == "provided"
    assert row.principles_state == "unknown"
    assert row.current_truth_state == "unknown"
    assert not AssessmentContext.objects.filter(assessment_run=target).exists()


@pytest.mark.parametrize("changed", ["source", "target", "assessment"])
def test_reuse_rejects_changed_source_target_or_assessment(periods, changed):
    user, source, target, _ = periods
    _, token = preview_reuse(user, source, ["mission", "capacity"])
    if changed == "assessment":
        AssessmentRun.objects.create(
            user=user,
            stable_id="NEWEST-HISTORY-EPOCH",
            curriculum_version=target.curriculum_version,
            assessment_version=target.assessment_version,
            source=target.source,
        )
    else:
        save_intentions(user, source if changed == "source" else target, "CHANGED", 1)
    count = PersonalOSRevision.objects.count()
    with pytest.raises(ValidationError):
        confirm_reuse(user, token)
    assert PersonalOSRevision.objects.count() == count


def test_reuse_rejects_invalid_selection_tampering_expiry_and_other_owner(
    periods, django_user_model
):
    user, source, _, _ = periods
    for selected in ([], ["current_truth"], ["anti_goals"], ["practice_fit"]):
        with pytest.raises(ValidationError):
            preview_reuse(user, source, selected)
    _, token = preview_reuse(user, source, ["mission"])
    with pytest.raises(signing.BadSignature):
        confirm_reuse(user, token + "x")
    with (
        patch(
            "django.core.signing.time.time",
            return_value=timezone.now().timestamp() + REUSE_MAX_AGE + 2,
        ),
        pytest.raises(signing.SignatureExpired),
    ):
        confirm_reuse(user, token)
    other = django_user_model.objects.create_user(username="history-other")
    with pytest.raises(ValidationError):
        confirm_reuse(other, token)


def test_combined_reuse_rolls_back_if_context_write_fails(periods):
    user, source, target, _ = periods
    _, token = preview_reuse(user, source, ["mission", "capacity"])
    with (
        patch(
            "growth.services.history.record_context_bundle", side_effect=ValidationError("conflict")
        ),
        pytest.raises(ValidationError),
    ):
        confirm_reuse(user, token)
    assert not PersonalOSRevision.objects.filter(assessment_run=target).exists()


def test_historical_weekly_proof_is_read_only_and_cannot_replan(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    _submitted_evidence(sprint, plan.action, direction="contradicts")
    save_plan_review(user=user, plan=plan, next_step="pause_reconsider", adjustment="scope")
    persist_assessment_run(user, golden_payload())
    before = _nonweekly_state(user, sprint)
    client.force_login(user)
    response = client.get(reverse("history-plan", args=[plan.pk]))
    assert response.status_code == 200
    assert b"Contradicts" in response.content
    assert b"Read-only weekly history" in response.content
    assert b"Pause and reconsider" in response.content
    assert client.post(reverse("history-plan", args=[plan.pk])).status_code == 405
    for name in ("weekly-plan-detail", "weekly-replan", "weekly-calendar"):
        assert client.get(reverse(name, args=[plan.pk])).status_code == 409
    assert _nonweekly_state(user, sprint) == before


def test_history_is_owner_scoped_and_verifies_corruption(client, user, seeded, django_user_model):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    urls = [
        reverse("history-period", args=[sprint.assessment_run_id]),
        reverse("history-plan", args=[plan.pk]),
        reverse("history-reuse", args=[sprint.assessment_run_id]),
    ]
    for url in urls:
        assert client.get(url).status_code == 302
    client.force_login(django_user_model.objects.create_user(username="history-private"))
    for url in urls:
        assert client.get(url).status_code == 404
    client.force_login(user)
    models.QuerySet.update(WeeklyExecutionPlan.objects.filter(pk=plan.pk), content_hash="0" * 64)
    for url in urls[:2]:
        assert client.get(url).status_code == 409
    with pytest.raises(ValidationError):
        historical_plan(user, WeeklyExecutionPlan.objects.get(pk=plan.pk))


@pytest.mark.parametrize("status", ["active", "paused"])
def test_old_practice_has_clear_navigation_and_current_week_refuses_mixing(client, periods, status):
    user, source, target, sprint = periods
    if status == "paused":
        transition_sprint(sprint, "paused")
    client.force_login(user)
    assessment = client.get(reverse("growth:assessment"))
    assert b"What changes when you reassess" in assessment.content
    assert sprint.protocol.name.encode() in assessment.content
    page = client.get(reverse("growth:practice-sprint", args=[sprint.pk]))
    assert page.status_code == 200
    assert b"earlier assessment period" in page.content
    assert b"Stop practice" in page.content
    assert b"Plan weekly execution" not in page.content
    if status == "paused":
        assert b"Resume practice" in page.content
    weekly = client.get(reverse("growth:weekly-execution"))
    assert weekly.status_code == 200
    assert b"New weekly plans cannot mix these periods" in weekly.content
    assert b"Save weekly plan" not in weekly.content
    with pytest.raises(ValidationError):
        save_current_plan(
            user=user,
            assessment_run=source,
            sprint=sprint,
            action=sprint.protocol.actions.first(),
            week_start=timezone.localdate() - timedelta(days=timezone.localdate().weekday()),
            intended_on=timezone.localdate(),
            expected_revision=0,
        )
    sprint.refresh_from_db()
    assert sprint.assessment_run_id == source.pk
    assert target.pk != source.pk


def test_period_pagination_empty_history_and_declined_values(client, periods):
    user, source, target, _ = periods
    for index in range(11):
        AssessmentRun.objects.create(
            user=user,
            stable_id=f"HISTORY-PAGE-{index}",
            curriculum_version=target.curriculum_version,
            assessment_version=target.assessment_version,
            source=target.source,
        )
    client.force_login(user)
    first = client.get(reverse("history"))
    assert len(first.context["periods"]) == 10
    assert first.context["periods"].has_next()
    second = client.get(reverse("history"), {"page": 2})
    assert len(second.context["periods"]) == 3
    assert source.pk in [row.pk for row in second.context["periods"]]
    assert reuse_state(user, target)["options"] == []


def test_corrupt_intentions_suppress_history_and_reuse(client, periods):
    user, source, _, _ = periods
    row = PersonalOSRevision.objects.get(assessment_run=source)
    models.QuerySet.update(PersonalOSRevision.objects.filter(pk=row.pk), content_hash="0" * 64)
    client.force_login(user)
    for name in ("history-period", "history-reuse"):
        response = client.get(reverse(name, args=[source.pk]))
        assert response.status_code == 409
        assert b"PRIVATE-OLDER-MISSION" not in response.content


def test_paused_older_practice_can_close_without_transferring_credit(client, periods):
    from growth.models import CompletionCreditEvent, CompositeScoreState
    from tests.test_practice_workflow import check_in_post

    user, source, target, sprint = periods
    client.force_login(user)
    actions = list(sprint.protocol.actions.order_by("sequence"))
    rows = [
        check_in_post(
            actions[0],
            action_completed="on",
            user_initiated="on",
            moved_beyond_transactional="on",
            meaningful_information_shared="on",
        ),
        check_in_post(
            actions[1],
            action_completed="on",
            future_interaction_scheduled="on",
            context_comparison="same_context",
        ),
        check_in_post(
            actions[2],
            follow_up_question_asked="on",
            follow_up_within_seven_days="on",
            context_comparison="same_context",
        ),
    ]
    before = list(CompositeScoreState.objects.filter(assessment_run=target).values())
    for row in rows:
        row["intent"] = "submit"
        assert (
            client.post(reverse("growth:practice-check-in-new", args=[sprint.pk]), row).status_code
            == 302
        )
    transition_sprint(sprint, "paused")
    assert (
        b"Review and close paused practice"
        in client.get(reverse("growth:practice-sprint", args=[sprint.pk])).content
    )
    response = client.post(
        reverse("growth:practice-review", args=[sprint.pk]),
        {"reflection": "A concrete earlier-period observation.", "contradictory_evidence": ""},
    )
    assert response.status_code == 302
    sprint.refresh_from_db()
    assert sprint.status == "completed"
    assert sprint.assessment_run_id == source.pk
    assert CompletionCreditEvent.objects.get(sprint=sprint).assessment_run_id == source.pk
    assert not CompletionCreditEvent.objects.filter(assessment_run=target).exists()
    assert list(CompositeScoreState.objects.filter(assessment_run=target).values()) == before
