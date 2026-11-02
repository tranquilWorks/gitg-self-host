from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from growth.presentation import recovery
from growth.services.entry import skip_suggestion


@require_GET
def quick_start(request):
    return render(request, "growth/quick_start.html")


@require_POST
def skip_home_suggestion(request):
    try:
        skip_suggestion(
            user=request.user,
            assessment_epoch=request.POST.get("assessment_epoch", ""),
            protocol_id=request.POST.get("protocol_id", ""),
            expected_revision=int(request.POST.get("expected_revision", "")),
        )
    except (ValidationError, ValueError, TypeError, IntegrityError, OperationalError):
        return recovery(
            request,
            "This choice could not be saved. Reload Home and try again; no value is displayed.",
            status=409,
        )
    messages.success(request, "Skipped for now. Choose another suggestion below.")
    return redirect("growth:home")
