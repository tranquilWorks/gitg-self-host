"""Owner-only, read-only review of saved practice fit and review horizons."""

from datetime import timedelta

from django.core.paginator import Paginator
from django.utils import timezone

from growth.domain.practice_content import PracticeContentError
from growth.services.context_priority import ContextPriorityServiceError
from growth.services.personal_os_browser import (
    active_projected_protocol_ids,
    verified_practice_contexts,
)


def build_context_review(*, user, assessment_run, params):
    try:
        latest = verified_practice_contexts(user, assessment_run, active_projected_protocol_ids())
    except (ContextPriorityServiceError, PracticeContentError):
        return {
            "error": (
                "Saved context could not be verified. Reload after the instance owner repairs it."
            )
        }
    selected = params.get("status", "deferred")
    if selected not in {"deferred", "not_applicable", "all"}:
        selected = "deferred"
    rows = []
    for record in latest.values():
        status = (
            "not_applicable"
            if record.applicability_state == "not_applicable"
            else record.disposition
        )
        if selected != "all" and status != selected:
            continue
        review_on = (
            timezone.localtime(record.created_at).date()
            + timedelta(days=record.review_horizon_days)
            if record.review_horizon_days
            else None
        )
        rows.append(
            {
                "record": record,
                "status": status,
                "review_on": review_on,
                "due": bool(review_on and review_on <= timezone.localdate()),
            }
        )
    rows.sort(
        key=lambda row: (
            row["review_on"] is None,
            row["review_on"] or timezone.localdate(),
            row["record"].protocol_id,
        )
    )
    page = Paginator(rows, 12).get_page(params.get("page"))
    return {"page": page, "selected": selected, "error": ""}
