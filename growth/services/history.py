"""Owner-scoped historical presentation and explicit, selected intention reuse."""

from copy import deepcopy

from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction

from growth.domain.personal_os import AUDIT_PROMPT_IDS, IDENTITY_SECTION_IDS
from growth.models import AssessmentContext, AssessmentRun, PersonalOSRevision
from growth.services.context import record_context_bundle
from growth.services.personal_os import record_personal_os_revision
from growth.services.personal_os_browser import assessment_factors_from_record

REUSE_SALT = "grounded-growth-selected-intention-reuse-v1"
REUSE_MAX_AGE = 1200
LABELS = {
    "mission": "Mission",
    "principles": "Principles",
    "anti_goals": "Anti-goals",
    "twelve_month_direction": "Twelve-month direction",
    "priority_stack": "Priority stack",
    "season": "Season",
    "capacity": "Capacity",
}


def _owner(user, run):
    if not user.is_authenticated or run.user_id != user.pk:
        raise ValidationError("This assessment period is not available.")


def _chain(model, user, run):
    rows = list(model.objects.filter(assessment_run=run).order_by("revision"))
    for number, row in enumerate(rows, 1):
        row.full_clean()
        if row.user_id != user.pk or row.revision != number:
            raise ValidationError("The saved revision history could not be verified.")
    return rows[-1] if rows else None


def period_intentions(user, run):
    _owner(user, run)
    return {
        "personal": _chain(PersonalOSRevision, user, run),
        "context": _chain(AssessmentContext, user, run),
    }


def _value_rows(state):
    rows = {}
    for key, label in LABELS.items():
        record = state["personal" if key in IDENTITY_SECTION_IDS else "context"]
        value_state = getattr(record, f"{key}_state") if record else "unknown"
        value = getattr(record, f"{key}_value") if record and value_state == "provided" else None
        rows[key] = {
            "key": key,
            "label": label,
            "state": value_state,
            "state_label": value_state.replace("_", " ").capitalize(),
            "value": value,
            "display": " · ".join(value) if isinstance(value, list) else value,
        }
    return rows


def intention_rows(state):
    return list(_value_rows(state).values())


def _stamp(state):
    return {key: [row.revision, row.content_hash] if row else None for key, row in state.items()}


def reuse_state(user, source):
    _owner(user, source)
    target = AssessmentRun.objects.filter(user=user).first()
    if target is None or source.pk == target.pk or source.created_at >= target.created_at:
        raise ValidationError("Choose an earlier assessment period.")
    old = period_intentions(user, source)
    new = period_intentions(user, target)
    current_rows = _value_rows(new)
    options = [
        {**row, "current": current_rows[key]}
        for key, row in _value_rows(old).items()
        if row["state"] == "provided"
    ]
    return {"source": source, "target": target, "old": old, "new": new, "options": options}


def preview_reuse(user, source, selected):
    state = reuse_state(user, source)
    selected = sorted(set(selected))
    allowed = {row["key"] for row in state["options"]}
    if not selected or not set(selected) <= allowed:
        raise ValidationError("Select at least one provided intention to review.")
    payload = {
        "user": user.pk,
        "source": source.pk,
        "target": state["target"].pk,
        "old": _stamp(state["old"]),
        "new": _stamp(state["new"]),
        "selected": selected,
    }
    return state, signing.dumps(payload, salt=REUSE_SALT, compress=True)


def _personal_payload(record):
    if record:
        return deepcopy(record.canonical_snapshot)
    return {
        group: {key: {"state": "unknown", "value": None} for key in keys}
        for group, keys in (
            ("identity_sections", IDENTITY_SECTION_IDS),
            ("audit_responses", AUDIT_PROMPT_IDS),
        )
    }


@transaction.atomic
def confirm_reuse(user, token):
    payload = signing.loads(token, salt=REUSE_SALT, max_age=REUSE_MAX_AGE)
    if payload.get("user") != user.pk:
        raise ValidationError("The confirmation belongs to another owner.")
    # Serialize with all existing writers, which lock the assessment row.
    list(AssessmentRun.objects.select_for_update().filter(user=user).order_by("pk"))
    source = AssessmentRun.objects.get(pk=payload["source"], user=user)
    state = reuse_state(user, source)
    if (
        state["target"].pk != payload["target"]
        or _stamp(state["old"]) != payload["old"]
        or _stamp(state["new"]) != payload["new"]
    ):
        raise ValidationError(
            "The source, current intentions or assessment changed. Preview again."
        )
    selected = payload["selected"]
    allowed = {row["key"] for row in state["options"]}
    if not selected or not set(selected) <= allowed:
        raise ValidationError("The selected intentions are no longer available.")
    identity = set(selected) & set(IDENTITY_SECTION_IDS)
    if identity:
        values = _personal_payload(state["new"]["personal"])
        old = _personal_payload(state["old"]["personal"])
        for key in identity:
            values["identity_sections"][key] = old["identity_sections"][key]
        record_personal_os_revision(
            user=user,
            assessment_run=state["target"],
            identity_sections=values["identity_sections"],
            audit_responses=values["audit_responses"],
        )
    factors = set(selected) & {"season", "capacity"}
    if factors:
        values = assessment_factors_from_record(state["new"]["context"])
        old = assessment_factors_from_record(state["old"]["context"])
        for key in factors:
            values[key] = old[key]
        record_context_bundle(user=user, assessment_run=state["target"], assessment_factors=values)
    return state["target"]
