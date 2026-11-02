from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


class RequireApplicationLoginMiddleware:
    """Keep records private; allow login, registration, policy, health and assets."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_paths = {settings.LOGIN_URL, "/health/", "/accounts/create/", "/data-policy/"}
        is_static = request.path_info.startswith(settings.STATIC_URL)
        if (
            not request.user.is_authenticated
            and request.path_info not in public_paths
            and not is_static
        ):
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
        downstream = (
            "/profile/",
            "/personal-os/",
            "/weekly/",
            "/practices/",
            "/history/",
            "/evidence/",
        )
        if (
            request.user.is_authenticated
            and request.method in {"GET", "HEAD"}
            and request.path_info in downstream
            and not request.user.assessment_runs.exists()
        ):
            return redirect("growth:assessment")
        return self.get_response(request)
