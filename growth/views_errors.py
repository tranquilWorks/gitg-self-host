from django.http import JsonResponse
from django.shortcuts import render

from growth.presentation import recovery


def bad_request(request, exception=None):
    return recovery(
        request,
        "This request could not be understood. Open a fresh page and try again.",
        status=400,
    )


def forbidden(request, exception=None):
    return recovery(request, "This action is not available to your account.", status=403)


def not_found(request, exception=None):
    return recovery(
        request, "This page is unavailable or does not belong to your account.", status=404
    )


def csrf_failure(request, reason=""):
    message = "Your session could not be verified. Reload the page before submitting again."
    if request.path == "/assessment/runs/":
        response = JsonResponse({"error": message}, status=403)
        response["Cache-Control"] = "no-store, private"
        return response
    return recovery(request, message, status=403)


def server_error(request):
    # No request context: a database failure must not trigger session/user queries.
    response = render(None, "500.html", status=500)
    response["Cache-Control"] = "no-store, private"
    return response
