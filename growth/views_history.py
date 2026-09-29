from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, OperationalError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from growth.forms_history import ConfirmReuseForm, ReuseIntentionsForm
from growth.models import AssessmentRun, PracticeSprint, WeeklyExecutionPlan
from growth.services.history import (
    REUSE_MAX_AGE,
    REUSE_SALT,
    confirm_reuse,
    intention_rows,
    period_intentions,
    preview_reuse,
    reuse_state,
)
from growth.services.practice import current_sprint_for
from growth.services.weekly_followup import historical_plan

ERRORS = (
    ValidationError,
    ValueError,
    TypeError,
    signing.BadSignature,
    OperationalError,
    IntegrityError,
    AssessmentRun.DoesNotExist,
)


def _conflict():
    return HttpResponse(
        "This history or confirmation changed or could not be verified. "
        "Return to History and preview again. No private value is displayed.",
        status=409,
    )


@login_required
@never_cache
@require_GET
def history(request):
    runs = AssessmentRun.objects.filter(user=request.user).order_by("-created_at", "-pk")
    return render(
        request,
        "growth/history.html",
        {
            "periods": Paginator(runs, 10).get_page(request.GET.get("page")),
            "current": runs.first(),
            "active_sprint": current_sprint_for(request.user),
        },
    )


@login_required
@never_cache
@require_GET
def history_period(request, run_id):
    run = get_object_or_404(AssessmentRun, pk=run_id, user=request.user)
    try:
        intentions = period_intentions(request.user, run)
    except ERRORS:
        return _conflict()
    practices = (
        PracticeSprint.objects.filter(user=request.user, assessment_run=run)
        .select_related("protocol")
        .order_by("-created_at", "-pk")
    )
    plans = (
        WeeklyExecutionPlan.objects.filter(user=request.user, assessment_run=run)
        .select_related("action", "review")
        .order_by("-week_start", "-revision")
    )
    plan_page = Paginator(plans, 12).get_page(request.GET.get("plans_page"))
    try:
        for plan in plan_page:
            historical_plan(request.user, plan)
    except ERRORS:
        return _conflict()
    return render(
        request,
        "growth/history_period.html",
        {
            "period": run,
            "current": AssessmentRun.objects.filter(user=request.user).first(),
            "practices": Paginator(practices, 12).get_page(request.GET.get("practices_page")),
            "plans": plan_page,
            "intentions": intentions,
            "intention_rows": intention_rows(intentions),
        },
    )


@login_required
@never_cache
@require_GET
def history_plan(request, plan_id):
    plan = get_object_or_404(
        WeeklyExecutionPlan.objects.select_related(
            "assessment_run", "sprint__protocol", "action", "review"
        ),
        pk=plan_id,
        user=request.user,
    )
    try:
        context = historical_plan(request.user, plan)
    except ERRORS:
        return _conflict()
    return render(request, "growth/history_plan.html", context)


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def history_reuse(request, run_id=None):
    source = (
        get_object_or_404(AssessmentRun, pk=run_id, user=request.user)
        if run_id
        else AssessmentRun.objects.filter(user=request.user).order_by("-created_at")[1:2].first()
    )
    if source is None:
        messages.info(request, "There is no earlier assessment period to review yet.")
        return redirect("history")
    if request.method == "POST" and request.POST.get("intent") == "confirm":
        confirmation = ConfirmReuseForm(request.POST)
        if not confirmation.is_valid():
            return _conflict()
        try:
            # The source in the signed preview must also match this owner-scoped URL.
            payload = signing.loads(
                confirmation.cleaned_data["token"],
                salt=REUSE_SALT,
                max_age=REUSE_MAX_AGE,
            )
            if payload["source"] != source.pk:
                return _conflict()
            confirm_reuse(request.user, confirmation.cleaned_data["token"])
        except ERRORS:
            return _conflict()
        messages.success(
            request,
            "Selected intentions saved for your current assessment period. "
            "Earlier records are unchanged.",
        )
        return redirect("growth:personal-os")
    try:
        state = reuse_state(request.user, source)
    except ERRORS:
        return _conflict()
    form = ReuseIntentionsForm(
        request.POST if request.method == "POST" else None, options=state["options"]
    )
    if request.method == "POST":
        if request.POST.get("intent") != "preview":
            return _conflict()
        if form.is_valid():
            try:
                state, token = preview_reuse(request.user, source, form.cleaned_data["selected"])
            except ERRORS:
                return _conflict()
            return render(
                request,
                "growth/history_reuse.html",
                {
                    **state,
                    "preview": True,
                    "confirmation": ConfirmReuseForm(initial={"token": token}),
                    "selected_rows": [
                        row
                        for row in state["options"]
                        if row["key"] in form.cleaned_data["selected"]
                    ],
                },
            )
    return render(
        request,
        "growth/history_reuse.html",
        {**state, "form": form},
        status=400 if request.method == "POST" else 200,
    )
