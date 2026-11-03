from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from growth.domain.personal_os import (
    AUDIT_PROMPT_DEFINITIONS,
    AUDIT_PROMPT_IDS,
    IDENTITY_SECTION_DEFINITIONS,
    IDENTITY_SECTION_IDS,
)
from growth.forms import AssessmentPriorityContextForm, PersonalOSForm
from growth.models import AssessmentContext, AssessmentRun, PersonalOSRevision
from growth.personal_os_copy import PROMPTS
from growth.presentation import recovery
from growth.services.context import ContextServiceError, record_context_bundle
from growth.services.history import reuse_state
from growth.services.personal_os import (
    PersonalOSServiceError,
    PersonalOSWriteConflictError,
    record_personal_os_revision,
)
from growth.services.personal_os_browser import (
    assessment_context_initial,
    personal_os_initial,
)
from growth.services.profile import build_profile_summary


def _sections(form, definitions, section_ids):
    return tuple(
        {
            "stable_id": section_id,
            "prompt": PROMPTS[section_id][0],
            "help_text": PROMPTS[section_id][1],
            "state": form[f"{section_id}_state"],
            "value": form[f"{section_id}_value"],
        }
        for section_id in section_ids
    )


def _render(request, *, run, personal_form, context_form, status=200):
    reusable = []
    try:
        reusable = [
            source
            for source in AssessmentRun.objects.filter(user=request.user).exclude(pk=run.pk)
            if reuse_state(request.user, source)["options"]
        ]
    except (ValidationError, ValueError, TypeError):
        return recovery(
            request, "Earlier choices could not be verified. No value is displayed.", status=409
        )
    saved = bool(personal_form.initial.get("mission_state"))
    summary = []
    for key, label in (("season", "Current season"), ("capacity", "Room for practice")):
        if context_form.initial.get(f"{key}_state") == "provided":
            value = context_form.initial.get(f"{key}_value")
            choices = dict(context_form.fields[f"{key}_value"].choices)
            summary.append(
                {"label": label, "value": choices.get(str(value), choices.get(value, value))}
            )
    for key, (label, _) in PROMPTS.items():
        if personal_form.initial.get(f"{key}_state") == "provided":
            summary.append({"label": label, "value": personal_form.initial.get(f"{key}_value", "")})
    return render(
        request,
        "growth/personal_os.html",
        {
            "assessment_run": run,
            "show_summary": saved and request.method == "GET" and request.GET.get("edit") != "1",
            "saved_sections": summary,
            "reusable_sources": reusable,
            "personal_form": personal_form,
            "context_form": context_form,
            "identity_sections": _sections(
                personal_form,
                IDENTITY_SECTION_DEFINITIONS,
                IDENTITY_SECTION_IDS,
            ),
            "audit_sections": _sections(
                personal_form,
                AUDIT_PROMPT_DEFINITIONS,
                AUDIT_PROMPT_IDS,
            ),
        },
        status=status,
    )


@require_http_methods(["GET", "POST"])
def personal_os(request):
    run = build_profile_summary(request.user).assessment_run
    if run is None:
        messages.info(
            request, "Complete or import an assessment before adding Personal OS context."
        )
        return redirect("growth:assessment")

    personal_rows = tuple(
        PersonalOSRevision.objects.filter(assessment_run=run).order_by("revision")
    )
    context_rows = tuple(AssessmentContext.objects.filter(assessment_run=run).order_by("revision"))
    try:
        for record in (*personal_rows, *context_rows):
            record.full_clean()
        if [record.revision for record in personal_rows] != list(range(1, len(personal_rows) + 1)):
            raise ValidationError("Personal OS revision sequence is invalid.")
        if [record.revision for record in context_rows] != list(range(1, len(context_rows) + 1)):
            raise ValidationError("Assessment context revision sequence is invalid.")
    except (ValidationError, ValueError, TypeError):
        return recovery(
            request,
            "Saved Personal OS or context state could not be verified. No value is displayed.",
            status=409,
        )
    latest_personal = personal_rows[-1] if personal_rows else None
    latest_context = context_rows[-1] if context_rows else None
    form_type = request.POST.get("form_type") if request.method == "POST" else None
    personal_form = PersonalOSForm(
        request.POST if form_type == "personal_os" else None,
        initial=personal_os_initial(latest_personal, assessment_epoch=run.pk),
    )
    context_form = AssessmentPriorityContextForm(
        request.POST if form_type == "assessment_context" else None,
        initial=assessment_context_initial(latest_context, assessment_epoch=run.pk),
    )
    for key, (prompt, help_text) in PROMPTS.items():
        personal_form.fields[f"{key}_state"].label = "Your choice"
        personal_form.fields[f"{key}_value"].label = prompt
        personal_form.fields[f"{key}_value"].help_text = help_text
    context_form.fields["capacity_value"].choices = (
        ("", "Choose the room you have"),
        ("0", "No room for another practice"),
        ("1", "Very little room"),
        ("2", "Some room"),
        ("3", "Comfortable room"),
        ("4", "Plenty of room"),
    )
    context_form.fields[
        "capacity_value"
    ].help_text = "The room you report can help narrow practices to fit your current life."

    if request.method == "POST" and form_type not in {"personal_os", "assessment_context"}:
        return recovery(
            request, "Unsupported Personal OS action. No value was saved or displayed.", status=400
        )

    if form_type == "personal_os" and personal_form.is_valid():
        if personal_form.cleaned_data["assessment_epoch"] != run.pk:
            return recovery(
                request,
                "The assessment period changed. Reload before saving; no value is displayed.",
                status=409,
            )
        try:
            result = record_personal_os_revision(
                user=request.user,
                assessment_run=run,
                identity_sections=personal_form.contract_values(IDENTITY_SECTION_IDS),
                audit_responses=personal_form.contract_values(AUDIT_PROMPT_IDS),
            )
        except (PersonalOSWriteConflictError, OperationalError, IntegrityError):
            return recovery(
                request,
                "The saved record changed while saving. Reload and retry; no value is displayed.",
                status=409,
            )
        except (PersonalOSServiceError, ValidationError, ValueError, TypeError):
            personal_form.add_error(None, "The Personal OS response could not be validated.")
            return _render(
                request,
                run=run,
                personal_form=personal_form,
                context_form=context_form,
                status=400,
            )
        messages.success(
            request,
            "Personal OS revision saved."
            if result.created
            else "Personal OS response was unchanged.",
        )
        return redirect("growth:personal-os")

    if form_type == "assessment_context" and context_form.is_valid():
        if context_form.cleaned_data["assessment_epoch"] != run.pk:
            return recovery(
                request,
                "The assessment period changed. Reload before saving; no value is displayed.",
                status=409,
            )
        try:
            result = record_context_bundle(
                user=request.user,
                assessment_run=run,
                assessment_factors=context_form.contract_factors(),
            )
        except (OperationalError, IntegrityError):
            return recovery(
                request,
                "The application is busy. Reload and retry; no value is displayed.",
                status=409,
            )
        except (ContextServiceError, ValidationError, ValueError, TypeError):
            context_form.add_error(None, "The season and capacity response could not be validated.")
            return _render(
                request,
                run=run,
                personal_form=personal_form,
                context_form=context_form,
                status=400,
            )
        messages.success(
            request,
            (
                "Season and capacity revision saved."
                if result.assessment_created
                else "Season and capacity response was unchanged."
            ),
        )
        return redirect("growth:personal-os")

    status = 400 if request.method == "POST" else 200
    return _render(
        request,
        run=run,
        personal_form=personal_form,
        context_form=context_form,
        status=status,
    )
