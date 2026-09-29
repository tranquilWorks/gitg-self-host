"""Safe HTML recovery without echoing submitted values or exception details."""

from django.shortcuts import render
from django.urls import reverse


def recovery(request, message, *, status=409, destination=None, label=None):
    if destination is None:
        path = request.path
        destination, label = next(
            (
                (name, title)
                for prefix, name, title in (
                    ("/history/", "history", "Open history"),
                    ("/weekly/", "growth:weekly-execution", "Open this week"),
                    ("/personal-os/", "growth:personal-os", "Open Personal OS"),
                    ("/practice", "growth:practice-list", "Open practices"),
                    ("/evidence/", "growth:evidence-ledger", "Open evidence"),
                    ("/account", "growth:data-management", "Open account"),
                )
                if path.startswith(prefix)
            ),
            ("growth:home", "Return home"),
        )
    response = render(
        request,
        "growth/recovery.html",
        {
            "recovery_status": status,
            "recovery_message": message,
            "recovery_url": reverse(destination),
            "recovery_label": label or "Return home",
        },
        status=status,
    )
    response["Cache-Control"] = "no-store, private"
    return response
