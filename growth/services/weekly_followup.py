"""Explicit weekly follow-up over unchanged immutable plan/review contracts."""

import hashlib
from datetime import UTC, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from growth.domain.weekly_execution import build_weekly_review_snapshot
from growth.models import AssessmentRun, PracticeSprint, WeeklyExecutionPlan
from growth.services.practice import current_sprint_for, transition_sprint
from growth.services.weekly_execution import (
    current_window,
    proof_events_for_plan,
    record_weekly_plan,
    record_weekly_review,
)

ADJUSTMENTS = {
    "none": "Keep the approach if it still fits your current capacity.",
    "timing": "Choose a more workable day for the action.",
    "scope": "Review the action's bounded scope and allowed adaptations before planning it again.",
    "support": "Review the practice guide and choose the support the action allows.",
    "context": "Review whether this practice still fits your situation before planning again.",
    "recovery": "Review your season and capacity before committing to another action.",
}


def _current_run(user, run_id, *, lock=False):
    if not getattr(user, "is_authenticated", False):
        raise ValidationError("Sign in to review this plan.")
    rows = AssessmentRun.objects.filter(user=user)
    if lock:
        rows = rows.select_for_update()
    run = rows.first()
    if run is None or run.pk != run_id:
        raise ValidationError("The assessment period changed. Reload this week.")
    return run


def verified_plan(user, plan, *, require_latest=True):
    _current_run(user, plan.assessment_run_id)
    return historical_plan(user, plan, require_latest=require_latest)


def historical_plan(user, plan, *, require_latest=False):
    """Read-only proof presentation; never authorizes current-period writes."""
    if not user.is_authenticated or plan.assessment_run.user_id != user.pk:
        raise ValidationError("Plan ownership could not be verified.")
    if plan.user_id != user.pk:
        raise ValidationError("Plan ownership could not be verified.")
    rows = list(
        WeeklyExecutionPlan.objects.filter(
            assessment_run_id=plan.assessment_run_id, week_start=plan.week_start
        )
        .select_related("sprint__protocol", "action", "assessment_run")
        .order_by("revision")
    )
    for revision, row in enumerate(rows, 1):
        row.full_clean()
        if row.revision != revision or row.user_id != user.pk:
            raise ValidationError("The weekly revision history could not be verified.")
    if not rows or not any(row.pk == plan.pk for row in rows):
        raise ValidationError("The plan could not be verified.")
    if require_latest and rows[-1].pk != plan.pk:
        raise ValidationError("This plan has a newer revision. Reload this week.")
    review = getattr(plan, "review", None)
    if review:
        review.full_clean()
    proof = proof_events_for_plan(plan, through=review.submitted_at if review else None)
    if review:
        rebuilt = build_weekly_review_snapshot(
            plan_stable_id=str(plan.pk),
            plan_content_hash=plan.content_hash,
            proof_events=proof,
            reviewed_at=review.submitted_at,
            next_step=review.next_step,
            adjustment=review.adjustment,
        )
        if (
            rebuilt.payload != review.canonical_snapshot
            or rebuilt.content_hash != review.content_hash
        ):
            raise ValidationError("The saved review proof could not be verified.")
    return {
        "plan": plan,
        "is_latest": rows[-1].pk == plan.pk,
        "revisions": rows,
        "review": review,
        "proof_rows": [
            {
                **event,
                "direction_label": event["direction"].replace("_", " ").capitalize(),
                "withholding_labels": [
                    item.replace("_", " ").capitalize() for item in event["withholding_reasons"]
                ],
            }
            for event in proof
        ],
        "adjustment_help": ADJUSTMENTS.get(review.adjustment, "") if review else "",
        "window_end": plan.week_start + timedelta(days=6),
    }


def previous_week_context(user, run, week_start):
    plan = (
        WeeklyExecutionPlan.objects.filter(user=user, assessment_run=run, week_start__lt=week_start)
        .select_related("sprint__protocol", "action", "assessment_run", "review")
        .order_by("-week_start", "-revision")
        .first()
    )
    if plan is None:
        return None
    context = verified_plan(user, plan)
    context["weeks_ago"] = (week_start - plan.week_start).days // 7
    return context


def can_replan(user, plan):
    sprint = current_sprint_for(user)
    return bool(
        sprint
        and sprint.pk == plan.sprint_id
        and sprint.status == "active"
        and sprint.assessment_run_id == plan.assessment_run_id
    )


@transaction.atomic
def save_current_plan(
    *, user, assessment_run, sprint, action, week_start, intended_on, expected_revision, source=None
):
    run = _current_run(user, assessment_run.pk, lock=True)
    actual_start, _ = current_window()
    if week_start != actual_start:
        raise ValidationError("The week changed. Reload before saving.")
    latest = (
        WeeklyExecutionPlan.objects.filter(user=user, assessment_run=run, week_start=week_start)
        .order_by("-revision")
        .first()
    )
    if expected_revision != (latest.revision if latest else 0):
        raise ValidationError("The weekly plan changed. Reload before saving.")
    if latest:
        verified_plan(user, latest)
    if source:
        verified_plan(user, source)
        if source.sprint_id != sprint.pk or source.week_start > week_start:
            raise ValidationError("Choose an action for the current practice and week.")
    if intended_on < timezone.localdate():
        raise ValidationError("Choose today or a later day this week.")
    return record_weekly_plan(
        user=user,
        assessment_run=run,
        sprint=sprint,
        action=action,
        week_start=week_start,
        intended_on=intended_on,
    )


@transaction.atomic
def save_plan_review(*, user, plan, next_step, adjustment):
    _current_run(user, plan.assessment_run_id, lock=True)
    verified_plan(user, plan)
    return record_weekly_review(user=user, plan=plan, next_step=next_step, adjustment=adjustment)


def transition_available(user, plan, review, decision):
    latest = (
        WeeklyExecutionPlan.objects.filter(user=user, assessment_run_id=plan.assessment_run_id)
        .order_by("-week_start", "-revision")
        .first()
    )
    sprint = current_sprint_for(user)
    choice = {"pause": "pause_reconsider", "stop": "choose_different_practice"}.get(decision)
    return bool(
        review
        and choice
        and review.next_step == choice
        and latest
        and latest.pk == plan.pk
        and sprint
        and sprint.pk == plan.sprint_id
        and (sprint.status == "active" or decision == "stop")
    )


@transaction.atomic
def confirm_review_transition(*, user, plan, expected_status, expected_week, decision):
    _current_run(user, plan.assessment_run_id, lock=True)
    context = verified_plan(user, plan)
    sprint = PracticeSprint.objects.select_for_update().get(pk=plan.sprint_id, user=user)
    if (
        expected_week != current_window()[0]
        or sprint.status != expected_status
        or not transition_available(user, plan, context["review"], decision)
    ):
        raise ValidationError("The review, week or current practice changed. Reload before acting.")
    return transition_sprint(sprint, "paused" if decision == "pause" else "stopped")


def calendar_file(user, plan):
    verified_plan(user, plan)
    start, _ = current_window()
    if (
        plan.week_start != start
        or plan.intended_on < timezone.localdate()
        or not can_replan(user, plan)
    ):
        raise ValidationError("Replan an upcoming action before downloading a calendar entry.")
    uid = hashlib.sha256(str(plan.pk).encode()).hexdigest()[:32]
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Grounded Growth//Weekly Plan//EN",
        "BEGIN:VEVENT",
        f"UID:{uid}@grounded-growth.local",
        f"DTSTAMP:{plan.created_at.astimezone(UTC):%Y%m%dT%H%M%SZ}",
        f"DTSTART;VALUE=DATE:{plan.intended_on:%Y%m%d}",
        f"DTEND;VALUE=DATE:{plan.intended_on + timedelta(days=1):%Y%m%d}",
        "SUMMARY:Grounded Growth practice",
        "CLASS:PRIVATE",
        "TRANSP:TRANSPARENT",
        "DESCRIPTION:Open Grounded Growth to review your weekly plan.",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")
