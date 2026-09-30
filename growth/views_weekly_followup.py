from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from growth.forms import WeeklyExecutionReviewForm
from growth.forms_weekly_followup import RecurringWeeklyPlanForm, WeeklyTransitionForm
from growth.models import WeeklyExecutionPlan
from growth.presentation import recovery
from growth.services.practice import current_sprint_for
from growth.services.weekly_execution import current_window
from growth.services.weekly_followup import (
    calendar_file,
    can_replan,
    confirm_review_transition,
    save_current_plan,
    save_plan_review,
    transition_available,
    verified_plan,
)

ERRORS = (ValidationError, ValueError, TypeError, OperationalError, IntegrityError)


def _conflict(request):
    return recovery(
        request,
        "This plan, practice or assessment changed, or could not be verified. "
        "Return to Weekly and reload before acting. No private value is displayed.",
        status=409,
    )


def _plan(request, plan_id):
    return get_object_or_404(
        WeeklyExecutionPlan.objects.select_related(
            "assessment_run", "sprint__protocol", "action", "review"
        ),
        pk=plan_id,
        user=request.user,
    )


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def weekly_plan_detail(request, plan_id):
    plan = _plan(request, plan_id)
    try:
        context = verified_plan(request.user, plan, require_latest=False)
    except ERRORS:
        return _conflict(request)
    form = WeeklyExecutionReviewForm(
        request.POST if request.method == "POST" else None,
        initial={"plan_id": plan.pk, "next_step": "continue_current", "adjustment": "none"},
    )
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data["plan_id"] != plan.pk:
            return _conflict(request)
        try:
            save_plan_review(
                user=request.user,
                plan=plan,
                next_step=form.cleaned_data["next_step"],
                adjustment=form.cleaned_data["adjustment"],
            )
        except ERRORS:
            return _conflict(request)
        messages.success(request, "Weekly review saved. Choose the next step when you are ready.")
        return redirect("weekly-plan-detail", plan_id=plan.pk)
    context.update(
        {
            "form": form,
            "can_replan": context["is_latest"] and can_replan(request.user, plan),
            "can_pause": transition_available(request.user, plan, context["review"], "pause"),
            "can_stop": transition_available(request.user, plan, context["review"], "stop"),
            "active_sprint": current_sprint_for(request.user),
        }
    )
    return render(
        request,
        "growth/weekly_plan_detail.html",
        context,
        status=400 if request.method == "POST" else 200,
    )


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def weekly_replan(request, plan_id):
    plan = _plan(request, plan_id)
    try:
        context = verified_plan(request.user, plan)
    except ERRORS:
        return _conflict(request)
    if not can_replan(request.user, plan):
        messages.info(
            request, "Replanning needs this practice to be active in the current assessment period."
        )
        return redirect("growth:practice-sprint", sprint_id=plan.sprint_id)
    start, end = current_window()
    target = (
        WeeklyExecutionPlan.objects.filter(
            user=request.user, assessment_run=plan.assessment_run, week_start=start
        )
        .order_by("-revision")
        .first()
    )
    action = plan.action
    if request.GET.get("mode") == "next":
        action = (
            plan.sprint.protocol.actions.filter(sequence__gt=plan.action.sequence)
            .order_by("sequence")
            .first()
        )
    form = RecurringWeeklyPlanForm(
        request.POST if request.method == "POST" else None,
        sprint=plan.sprint,
        initial={
            "assessment_epoch": plan.assessment_run_id,
            "sprint_id": plan.sprint_id,
            "week_start": start,
            "expected_revision": target.revision if target else 0,
            "action": action.pk if action else None,
            "intended_on": timezone.localdate(),
        },
    )
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        if data["assessment_epoch"] != plan.assessment_run_id:
            return _conflict(request)
        try:
            save_current_plan(
                user=request.user,
                assessment_run=plan.assessment_run,
                sprint=plan.sprint,
                action=data["action"],
                week_start=data["week_start"],
                intended_on=data["intended_on"],
                expected_revision=data["expected_revision"],
                source=plan,
            )
        except ERRORS:
            return _conflict(request)
        messages.success(
            request, "This week's plan is saved. The original plan and proof are preserved."
        )
        return redirect("growth:weekly-execution")
    context.update({"form": form, "week_start": start, "week_end": end, "target": target})
    return render(
        request,
        "growth/weekly_replan.html",
        context,
        status=400 if request.method == "POST" else 200,
    )


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def weekly_transition(request, plan_id, decision):
    if decision not in {"pause", "stop"}:
        return recovery(request, "Unknown next step.", status=404)
    plan = _plan(request, plan_id)
    try:
        context = verified_plan(request.user, plan)
    except ERRORS:
        return _conflict(request)
    if not transition_available(request.user, plan, context["review"], decision):
        return _conflict(request)
    form = WeeklyTransitionForm(
        request.POST if request.method == "POST" else None,
        initial={"expected_status": plan.sprint.status, "expected_week": current_window()[0]},
    )
    if request.method == "POST" and form.is_valid():
        try:
            confirm_review_transition(
                user=request.user, plan=plan, decision=decision, **form.cleaned_data
            )
        except ERRORS:
            return _conflict(request)
        messages.success(
            request,
            "Practice paused."
            if decision == "pause"
            else "Practice stopped. You can now explore another choice.",
        )
        return redirect("growth:weekly-execution" if decision == "pause" else "context-review")
    context.update({"form": form, "decision": decision})
    return render(
        request,
        "growth/weekly_transition.html",
        context,
        status=400 if request.method == "POST" else 200,
    )


@login_required
@never_cache
@require_GET
def weekly_calendar(request, plan_id):
    plan = _plan(request, plan_id)
    try:
        content = calendar_file(request.user, plan)
    except ERRORS:
        return _conflict(request)
    response = HttpResponse(content, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="grounded-growth-{plan.intended_on.isoformat()}.ics"'
    )
    response["X-Content-Type-Options"] = "nosniff"
    return response
