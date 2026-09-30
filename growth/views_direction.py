from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, OperationalError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from growth.domain.personal_os import IDENTITY_SECTION_DEFINITIONS
from growth.forms_direction import DirectionReviewForm, PracticeDirectionForm
from growth.models import AssessmentRun, PracticeProtocol
from growth.presentation import recovery
from growth.services.personal_os_browser import personal_os_initial
from growth.services.practice_direction import (
    DIRECTION_SECTIONS,
    direction_history,
    record_connection,
    record_direction_review,
    verified_personal_os,
)


def _conflict(request):
    return recovery(
        request,
        "Your saved direction or assessment changed, or could not be verified. "
        "Reload this page before saving. No private value is displayed.",
        status=409,
    )


def _sections(row):
    return [
        {
            "label": IDENTITY_SECTION_DEFINITIONS[key].prompt,
            "state": getattr(row, f"{key}_state").replace("_", " "),
            "value": getattr(row, f"{key}_value"),
            "is_list": key in ("anti_goals", "priority_stack"),
        }
        for key in DIRECTION_SECTIONS
    ]


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def direction_review(request):
    run = AssessmentRun.objects.filter(user=request.user).first()
    if run is None:
        return redirect("growth:assessment")
    try:
        rows = verified_personal_os(request.user, run)
    except (ValidationError, ValueError, TypeError):
        return _conflict(request)
    latest = rows[-1] if rows else None
    initial = personal_os_initial(latest, assessment_epoch=str(run.pk))
    initial["expected_revision"] = latest.revision if latest else 0
    form = DirectionReviewForm(request.POST if request.method == "POST" else None, initial=initial)
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["assessment_epoch"] != str(run.pk):
            return _conflict(request)
        try:
            result = record_direction_review(
                user=request.user,
                run=run,
                expected_revision=form.cleaned_data["expected_revision"],
                changes=form.contract_values(DIRECTION_SECTIONS),
            )
        except (ValidationError, ValueError, TypeError, OperationalError, IntegrityError):
            return _conflict(request)
        messages.success(
            request, "Direction review saved." if result.created else "Your direction is unchanged."
        )
        return redirect("direction-review")
    history = Paginator(list(reversed(rows[:-1])), 5).get_page(request.GET.get("page"))
    return render(
        request,
        "growth/direction_review.html",
        {
            "form": form,
            "latest": latest,
            "sections": [
                {
                    "state": form[f"{key}_state"],
                    "value": form[f"{key}_value"],
                    "title": key.replace("_", " ").capitalize(),
                }
                for key in DIRECTION_SECTIONS
            ],
            "history": history,
            "history_rows": [{"record": row, "sections": _sections(row)} for row in history],
        },
        status=400 if request.method == "POST" else 200,
    )


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def practice_direction(request, slug):
    protocol = get_object_or_404(
        PracticeProtocol, slug=slug, availability=PracticeProtocol.Availability.ACTIVE
    )
    run = AssessmentRun.objects.filter(user=request.user).first()
    if run is None:
        return redirect("growth:assessment")
    try:
        personal_rows = verified_personal_os(request.user, run)
        rows = direction_history(request.user, run, protocol)
    except (ValidationError, ValueError, TypeError, IndexError):
        return _conflict(request)
    latest = rows[-1] if rows else None
    personal_os = personal_rows[-1] if personal_rows else None
    old_priority = bool(
        latest
        and latest.personal_os_id
        and latest.personal_os_id != getattr(personal_os, "pk", None)
    )
    initial = {
        "assessment_epoch": str(run.pk),
        "expected_revision": latest.revision if latest else 0,
        "expected_personal_os": personal_os.revision if personal_os else 0,
        "state": latest.state if latest else "",
        "priority_index": latest.priority_index if latest and not old_priority else None,
        "intended_outcome": latest.intended_outcome if latest else "",
    }
    form = PracticeDirectionForm(
        request.POST if request.method == "POST" else None, personal_os=personal_os, initial=initial
    )
    destination = request.GET.get("return", "")
    # Fixed destinations: no arbitrary redirect URL or cross-owner record identifier.
    back_url = (
        reverse("growth:weekly-execution")
        if destination == "weekly"
        else reverse(
            "growth:practice-setup",
            kwargs={"slug": slug, "step": 7 if destination == "setup7" else 1},
        )
    )
    if request.method == "POST" and form.is_valid():
        values = form.cleaned_data.copy()
        if values.pop("assessment_epoch") != str(run.pk):
            return _conflict(request)
        try:
            record_connection(user=request.user, run=run, protocol=protocol, **values)
        except (ValidationError, ValueError, TypeError, OperationalError, IntegrityError):
            return _conflict(request)
        messages.success(request, "Practice connection saved. Earlier choices are preserved.")
        return redirect(back_url)
    history = Paginator(list(reversed(rows[:-1])), 5).get_page(request.GET.get("page"))
    return render(
        request,
        "growth/practice_direction.html",
        {
            "form": form,
            "protocol": protocol,
            "latest": latest,
            "old_priority": old_priority,
            "history": history,
            "back_url": back_url,
            "destination": destination if destination in ("weekly", "setup7") else "",
        },
        status=400 if request.method == "POST" else 200,
    )
