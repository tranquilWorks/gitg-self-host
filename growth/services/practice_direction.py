from django.core.exceptions import ValidationError
from django.db import transaction

from growth.domain.personal_os import AUDIT_PROMPT_IDS, IDENTITY_SECTION_IDS
from growth.domain.practice_direction import direction_snapshot
from growth.models import AssessmentRun, PersonalOSRevision, PracticeDirectionRevision
from growth.services.personal_os import record_personal_os_revision

DIRECTION_SECTIONS = ("mission", "anti_goals", "priority_stack", "twelve_month_direction")


def verified_personal_os(user, run):
    if run.user_id != user.pk:
        raise ValidationError("Invalid owner.")
    rows = list(PersonalOSRevision.objects.filter(assessment_run=run).order_by("revision"))
    for index, row in enumerate(rows, 1):
        row.full_clean()
        if row.revision != index:
            raise ValidationError("Invalid Personal OS history.")
    return rows


def direction_history(user, run, protocol):
    if run.user_id != user.pk:
        raise ValidationError("Invalid owner.")
    rows = list(
        PracticeDirectionRevision.objects.filter(assessment_run=run, protocol=protocol)
        .select_related("personal_os", "assessment_run")
        .order_by("revision")
    )
    for index, row in enumerate(rows, 1):
        row.full_clean()
        if row.revision != index or row.user_id != user.pk:
            raise ValidationError("Invalid connection history.")
    return rows


def connection_presentation(user, run, protocol):
    if run is None:
        return {"unavailable": True}
    try:
        rows = direction_history(user, run, protocol)
        personal_rows = verified_personal_os(user, run)
        latest_os = personal_rows[-1] if personal_rows else None
        latest = rows[-1] if rows else None
        return {
            "record": latest,
            "protocol": protocol,
            "prior_direction": bool(
                latest
                and latest.personal_os_id
                and latest.personal_os_id != getattr(latest_os, "pk", None)
            ),
        }
    except (ValidationError, ValueError, TypeError, IndexError):
        return {"unavailable": True}


def _lock_current(user, run):
    if not getattr(user, "is_authenticated", False) or run.user_id != user.pk:
        raise ValidationError("Invalid owner.")
    locked = AssessmentRun.objects.select_for_update().get(pk=run.pk, user=user)
    latest = AssessmentRun.objects.filter(user=user).first()
    if latest.pk != locked.pk:
        raise ValidationError("The assessment period changed. Reload before saving.")
    return locked


@transaction.atomic
def record_connection(
    *,
    user,
    run,
    protocol,
    expected_revision,
    expected_personal_os,
    state,
    priority_index=None,
    intended_outcome="",
):
    run = _lock_current(user, run)
    history = direction_history(user, run, protocol)
    personal_rows = verified_personal_os(user, run)
    personal_os = personal_rows[-1] if personal_rows else None
    if expected_revision != (history[-1].revision if history else 0) or expected_personal_os != (
        personal_os.revision if personal_os else 0
    ):
        raise ValidationError("Your direction or connection changed. Reload before saving.")
    row = PracticeDirectionRevision(
        user=user,
        assessment_run=run,
        protocol=protocol,
        revision=expected_revision + 1,
        state=state,
        personal_os=personal_os if state == "priority" else None,
        priority_index=priority_index,
        intended_outcome=intended_outcome,
    )
    row.canonical_snapshot, row.content_hash = direction_snapshot(row)
    if history and history[-1].content_hash == row.content_hash:
        return history[-1]
    row.save(force_insert=True)
    return row


@transaction.atomic
def record_direction_review(*, user, run, expected_revision, changes):
    run = _lock_current(user, run)
    rows = verified_personal_os(user, run)
    latest = rows[-1] if rows else None
    if expected_revision != (latest.revision if latest else 0):
        raise ValidationError("Your direction changed. Reload before saving.")
    if set(changes) != set(DIRECTION_SECTIONS):
        raise ValidationError("Invalid direction sections.")
    identity = (
        latest._snapshot_values(IDENTITY_SECTION_IDS)
        if latest
        else {key: {"state": "unknown", "value": None} for key in IDENTITY_SECTION_IDS}
    )
    audit = (
        latest._snapshot_values(AUDIT_PROMPT_IDS)
        if latest
        else {key: {"state": "unknown", "value": None} for key in AUDIT_PROMPT_IDS}
    )
    identity.update(changes)
    return record_personal_os_revision(
        user=user, assessment_run=run, identity_sections=identity, audit_responses=audit
    )
