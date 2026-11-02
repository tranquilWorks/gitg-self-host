"""Public account entry points; account records use Django's normal protections."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods


@never_cache
@require_http_methods(["GET", "POST"])
def create_account(request):
    if request.user.is_authenticated:
        return redirect("growth:home")
    if not settings.ALLOW_REGISTRATION:
        return render(request, "registration/create_account.html", {"registration_closed": True})
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created. Sign in to get started.")
        return redirect("login")
    return render(request, "registration/create_account.html", {"form": form})


@never_cache
def data_policy(request):
    return render(request, "growth/data_policy.html")
