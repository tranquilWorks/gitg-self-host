from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from growth.models import AssessmentRun, WeeklyExecutionPlan, WeeklyExecutionReview
from growth.services.practice import save_check_in, transition_sprint
from growth.services.weekly_execution import current_window, record_weekly_plan
from growth.services.weekly_followup import (
    calendar_file,
    confirm_review_transition,
    previous_week_context,
    save_current_plan,
    save_plan_review,
    verified_plan,
)
from tests.test_weekly_execution import _nonweekly_state, _sprint, _submitted_evidence

pytestmark = pytest.mark.django_db


def plan_for(user, sprint, *, weeks_ago=0):
    day = timezone.localdate() - timedelta(weeks=weeks_ago)
    return record_weekly_plan(
        user=user,
        assessment_run=sprint.assessment_run,
        sprint=sprint,
        action=sprint.protocol.actions.order_by("sequence").first(),
        week_start=current_window(today=day)[0],
        intended_on=day,
        today=day,
    ).plan


def payload(plan, **changes):
    values = {
        "assessment_epoch": plan.assessment_run_id,
        "sprint_id": plan.sprint_id,
        "week_start": current_window()[0],
        "expected_revision": 0,
        "action": plan.action_id,
        "intended_on": timezone.localdate(),
    }
    return values | changes


def test_previous_week_and_explicit_replan_preserve_original(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint, weeks_ago=2)
    save_plan_review(user=user, plan=plan, next_step="continue_current", adjustment="timing")
    original = WeeklyExecutionPlan.objects.values().get(pk=plan.pk)
    review = WeeklyExecutionReview.objects.values().get(plan=plan)
    before = _nonweekly_state(user, sprint)
    client.force_login(user)
    weekly = client.get(reverse("growth:weekly-execution"))
    assert b"2 weeks ago" in weekly.content
    assert b"no-evidence state" in weekly.content
    assert b"Continue the current action" in weekly.content
    url = reverse("weekly-replan", args=[plan.pk])
    assert client.get(url).status_code == 200
    assert WeeklyExecutionPlan.objects.count() == 1
    response = client.post(url, payload(plan))
    assert response.status_code == 302
    assert WeeklyExecutionPlan.objects.count() == 2
    assert WeeklyExecutionPlan.objects.values().get(pk=plan.pk) == original
    assert WeeklyExecutionReview.objects.values().get(plan=plan) == review
    assert _nonweekly_state(user, sprint) == before
    assert client.post(url, payload(plan)).status_code == 409
    assert WeeklyExecutionPlan.objects.count() == 2


def test_same_week_revisions_are_readable_but_stale_actions_fail(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    save_plan_review(user=user, plan=plan, next_step="continue_current", adjustment="scope")
    action = sprint.protocol.actions.order_by("sequence").last()
    replacement = save_current_plan(
        user=user,
        assessment_run=sprint.assessment_run,
        sprint=sprint,
        action=action,
        week_start=current_window()[0],
        intended_on=timezone.localdate(),
        expected_revision=1,
        source=plan,
    ).plan
    assert replacement.revision == 2
    client.force_login(user)
    page = client.get(reverse("weekly-plan-detail", args=[plan.pk]))
    assert page.status_code == 200
    assert b"Plan revisions for this week" in page.content
    assert b"Plan this action again" not in page.content
    for name in ("weekly-replan", "weekly-calendar"):
        assert client.get(reverse(name, args=[plan.pk])).status_code == 409
    assert (
        client.post(
            reverse("weekly-plan-detail", args=[plan.pk]),
            {
                "plan_id": plan.pk,
                "next_step": "continue_current",
                "adjustment": "scope",
            },
        ).status_code
        == 409
    )


@pytest.mark.parametrize(
    "choice,decision,target",
    [
        ("pause_reconsider", "pause", "paused"),
        ("choose_different_practice", "stop", "stopped"),
    ],
)
def test_review_transition_requires_explicit_confirmation(
    client, user, seeded, choice, decision, target
):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    before = _nonweekly_state(user, sprint)
    client.force_login(user)
    detail = reverse("weekly-plan-detail", args=[plan.pk])
    response = client.post(
        detail, {"plan_id": plan.pk, "next_step": choice, "adjustment": "recovery"}
    )
    assert response.status_code == 302
    sprint.refresh_from_db()
    assert sprint.status == "active"
    url = reverse("weekly-transition", args=[plan.pk, decision])
    assert client.get(url).status_code == 200
    sprint.refresh_from_db()
    assert sprint.status == "active"
    assert (
        client.post(
            url, {"expected_status": "active", "expected_week": current_window()[0]}
        ).status_code
        == 302
    )
    sprint.refresh_from_db()
    assert sprint.status == target
    before["sprint_status"] = target
    assert _nonweekly_state(user, sprint) == before
    assert (
        client.post(
            url, {"expected_status": "active", "expected_week": current_window()[0]}
        ).status_code
        == 409
    )


def test_stale_review_cannot_change_practice_and_paused_cannot_plan(client, user, seeded):
    sprint = _sprint(user)
    old = plan_for(user, sprint, weeks_ago=1)
    save_plan_review(user=user, plan=old, next_step="pause_reconsider", adjustment="none")
    current = plan_for(user, sprint)
    with pytest.raises(ValidationError):
        confirm_review_transition(
            user=user,
            plan=old,
            expected_status="active",
            expected_week=current_window()[0],
            decision="pause",
        )
    transition_sprint(sprint, "paused")
    client.force_login(user)
    page = client.get(reverse("growth:weekly-execution"))
    assert page.status_code == 200
    assert b"Save weekly plan" not in page.content
    assert client.get(reverse("weekly-replan", args=[current.pk])).status_code == 302
    assert client.get(reverse("weekly-calendar", args=[current.pk])).status_code == 409


def test_calendar_is_private_stable_all_day_and_read_only(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    url = reverse("weekly-calendar", args=[plan.pk])
    assert client.get(url).status_code == 302
    client.force_login(user)
    before = _nonweekly_state(user, sprint)
    response = client.get(url)
    assert response.status_code == 200
    assert "no-store" in response["Cache-Control"]
    assert response["Content-Type"] == "text/calendar; charset=utf-8"
    content = response.content
    assert content == calendar_file(user, plan)
    assert f"DTSTART;VALUE=DATE:{plan.intended_on:%Y%m%d}\r\n".encode() in content
    assert f"DTEND;VALUE=DATE:{plan.intended_on + timedelta(days=1):%Y%m%d}\r\n".encode() in content
    assert all(len(line) <= 75 for line in content.split(b"\r\n"))
    assert b"\n" not in content.replace(b"\r\n", b"")
    for private in (
        user.username,
        sprint.person_or_context,
        plan.action.title,
        str(plan.pk),
        "VALARM",
        "ATTENDEE",
        "URL:",
    ):
        assert private.encode() not in content
    assert client.post(url).status_code == 405
    assert _nonweekly_state(user, sprint) == before
    assert WeeklyExecutionReview.objects.count() == 0


def test_expired_calendar_and_backdated_replan_fail(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint, weeks_ago=1)
    client.force_login(user)
    assert client.get(reverse("weekly-calendar", args=[plan.pk])).status_code == 409
    response = client.post(
        reverse("weekly-replan", args=[plan.pk]),
        payload(plan, intended_on=timezone.localdate() - timedelta(days=1)),
    )
    assert response.status_code == 400
    assert WeeklyExecutionPlan.objects.count() == 1
    with pytest.raises(ValidationError):
        save_current_plan(
            user=user,
            assessment_run=sprint.assessment_run,
            sprint=sprint,
            action=plan.action,
            week_start=plan.week_start,
            intended_on=timezone.localdate(),
            expected_revision=0,
        )


def test_owner_scope_and_current_epoch_fail_closed(client, user, seeded, django_user_model):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    other = django_user_model.objects.create_user(username="other-followup")
    client.force_login(other)
    for name in ("weekly-plan-detail", "weekly-replan", "weekly-calendar"):
        assert client.get(reverse(name, args=[plan.pk])).status_code == 404
    with pytest.raises(ValidationError):
        verified_plan(other, plan)


def test_contradictory_proof_and_review_cutoff(user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    event = _submitted_evidence(sprint, plan.action, direction="contradicts")
    context = verified_plan(user, plan)
    assert context["proof_rows"][0]["direction"] == "contradicts"
    save_plan_review(user=user, plan=plan, next_step="plan_next_action", adjustment="support")
    save_check_in(
        sprint=sprint,
        cleaned_data={
            "action": plan.action,
            "action_attempted": True,
            "action_completed": True,
            "support_level": "independent",
            "context_comparison": "same_context",
            "evidence_direction": "supports",
        },
        submit=True,
    )
    plan.refresh_from_db()
    assert len(verified_plan(user, plan)["proof_rows"]) == 1
    assert str(event.evidence_event.pk) in str(plan.review.canonical_snapshot)
    assert previous_week_context(user, sprint.assessment_run, current_window()[0]) is None


@pytest.mark.parametrize(
    "choice,label",
    [
        ("continue_current", "Plan this action again"),
        ("plan_next_action", "Choose the next action"),
        ("pause_reconsider", "Review pause"),
        ("choose_different_practice", "Review stopping and choosing another practice"),
    ],
)
def test_each_review_choice_has_actionable_next_step(client, user, seeded, choice, label):
    plan = plan_for(user, _sprint(user))
    save_plan_review(user=user, plan=plan, next_step=choice, adjustment="timing")
    client.force_login(user)
    page = client.get(reverse("weekly-plan-detail", args=[plan.pk]))
    assert page.status_code == 200
    assert label.encode() in page.content
    assert b"Choose a more workable day" in page.content


def test_old_assessment_cannot_display_or_act(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    run = sprint.assessment_run
    AssessmentRun.objects.create(
        user=user,
        stable_id="NEW-WEEKLY-EPOCH",
        curriculum_version=run.curriculum_version,
        assessment_version=run.assessment_version,
        source=run.source,
    )
    client.force_login(user)
    for name in ("weekly-plan-detail", "weekly-replan", "weekly-calendar"):
        assert client.get(reverse(name, args=[plan.pk])).status_code == 409
    with pytest.raises(ValidationError):
        save_plan_review(user=user, plan=plan, next_step="continue_current", adjustment="none")
    assert WeeklyExecutionReview.objects.count() == 0


def test_corrupt_history_fails_closed(client, user, seeded):
    from django.db import models

    plan = plan_for(user, _sprint(user))
    models.QuerySet.update(WeeklyExecutionPlan.objects.filter(pk=plan.pk), content_hash="0" * 64)
    client.force_login(user)
    for name in ("weekly-plan-detail", "weekly-replan", "weekly-calendar"):
        response = client.get(reverse(name, args=[plan.pk]))
        assert response.status_code == 409
        assert plan.sprint.person_or_context.encode() not in response.content
    assert client.get(reverse("growth:weekly-execution")).status_code == 409
