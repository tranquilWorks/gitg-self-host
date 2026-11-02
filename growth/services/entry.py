"""Stage presentation and an explicit shortcut to the existing defer contract."""

from django.core.exceptions import ValidationError
from django.db import transaction

from growth.domain.context import PRACTICE_FACTOR_IDS
from growth.models import AssessmentContext, AssessmentRun, PracticeContext, PracticeSprint
from growth.services.context import PracticeContextInput, record_context_bundle
from growth.services.personal_os_browser import (
    assessment_factors_from_record,
    build_browser_priority_presentation,
)
from growth.services.practice import current_sprint_for
from growth.services.practice_direction import verified_personal_os
from growth.services.profile import build_profile_summary

CAPACITY_COPY = {
    0: "No room for an extra practice right now",
    1: "Very little room for an extra practice",
    2: "Some room for an extra practice",
    3: "Enough room for a regular practice",
    4: "Plenty of room for an extra practice",
}


def verified_assessment_context(user, run):
    rows = list(
        AssessmentContext.objects.filter(user=user, assessment_run=run).order_by("revision")
    )
    for index, row in enumerate(rows, 1):
        row.full_clean()
        if row.revision != index:
            raise ValidationError("Invalid context history.")
    return rows[-1] if rows else None


def build_entry_presentation(*, user, summary, priority, active_sprint):
    run = summary.assessment_run
    completed = (
        PracticeSprint.objects.filter(user=user, status="completed", review__isnull=False)
        .select_related("protocol")
        .order_by("-completed_at", "-created_at")
        .first()
    )
    result = {
        "stage": "new" if run is None else "assessed",
        "completed": completed,
        "has_completed_loop": completed is not None,
        "direction": "",
        "season": "",
        "capacity": "",
        "context_error": False,
        "suggestions": (),
    }
    if run is None:
        return result
    result["stage"] = "active" if active_sprint else "completed" if completed else "assessed"
    try:
        personal_rows = verified_personal_os(user, run)
        personal = personal_rows[-1] if personal_rows else None
        context = verified_assessment_context(user, run)
        if personal and personal.twelve_month_direction_state == "provided":
            result["direction"] = personal.twelve_month_direction_value
        if context and context.season_state == "provided":
            result["season"] = context.get_season_value_display()
        if context and context.capacity_state == "provided":
            result["capacity"] = CAPACITY_COPY[context.capacity_value]
    except (ValidationError, ValueError, TypeError, KeyError):
        result["context_error"] = True
    result["steps"] = (
        {"label": "Take the assessment", "done": run.source != "pilot_seed"},
        {"label": "Choose a direction (optional)", "done": bool(result["direction"])},
        {"label": "Start a practice", "done": user.practice_sprints.exists()},
        {"label": "Finish a practice and review it", "done": completed is not None},
    )
    if priority.status == "unavailable" or summary.state_verification_error:
        return result
    # This is a display filter, not a new ranking: an active practice already
    # has its own primary card. The underlying ordered recommendations remain exact.
    suggestions = []
    for protocol in priority.recommendations:
        if active_sprint and protocol.pk == active_sprint.protocol_id:
            continue
        latest = (
            PracticeContext.objects.filter(user=user, assessment_run=run, protocol=protocol)
            .order_by("-revision")
            .first()
        )
        suggestions.append({"protocol": protocol, "revision": latest.revision if latest else 0})
    result["suggestions"] = tuple(suggestions)
    return result


@transaction.atomic
def skip_suggestion(*, user, assessment_epoch, protocol_id, expected_revision):
    """Explicit user-choice deferral, never inferred N/A or scoring evidence."""
    run = AssessmentRun.objects.filter(user=user).first()
    if run is None or str(run.pk) != assessment_epoch:
        raise ValidationError("Your assessment changed. Reload Home before choosing again.")
    AssessmentRun.objects.select_for_update().get(pk=run.pk, user=user)
    summary = build_profile_summary(user)
    priority = build_browser_priority_presentation(user=user, summary=summary)
    current = current_sprint_for(user)
    protocol = next((p for p in priority.recommendations if p.pk == protocol_id), None)
    if (
        protocol is None
        or priority.status == "unavailable"
        or summary.state_verification_error
        or (current and current.protocol_id == protocol.pk)
    ):
        raise ValidationError("This suggestion changed. Reload Home before choosing again.")
    rows = list(
        PracticeContext.objects.filter(user=user, assessment_run=run, protocol=protocol).order_by(
            "revision"
        )
    )
    for index, row in enumerate(rows, 1):
        row.full_clean()
        if row.revision != index:
            raise ValidationError("Saved choices could not be verified.")
    latest = rows[-1] if rows else None
    if expected_revision != (latest.revision if latest else 0):
        raise ValidationError("Your saved choice changed. Reload Home before choosing again.")
    context = verified_assessment_context(user, run)
    factors = {
        factor: {
            "state": getattr(latest, f"{factor}_state") if latest else "unknown",
            "value": getattr(latest, f"{factor}_value") if latest else None,
        }
        for factor in PRACTICE_FACTOR_IDS
    }
    factors["readiness"] = {"state": "deferred", "value": None}
    return record_context_bundle(
        user=user,
        assessment_run=run,
        assessment_factors=assessment_factors_from_record(context),
        practice_inputs=(
            PracticeContextInput(
                protocol=protocol,
                factors=factors,
                disposition="deferred",
                defer_reason="user_choice",
            ),
        ),
    )
