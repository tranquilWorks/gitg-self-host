from django.contrib.auth import views as auth_views
from django.urls import include, path

from growth.views import health
from growth.views_direction import direction_review, practice_direction
from growth.views_practice import context_review
from growth.views_weekly_followup import (
    weekly_calendar,
    weekly_plan_detail,
    weekly_replan,
    weekly_transition,
)

urlpatterns = [
    path("weekly/plans/<uuid:plan_id>/", weekly_plan_detail, name="weekly-plan-detail"),
    path("weekly/plans/<uuid:plan_id>/replan/", weekly_replan, name="weekly-replan"),
    path(
        "weekly/plans/<uuid:plan_id>/decision/<str:decision>/",
        weekly_transition,
        name="weekly-transition",
    ),
    path("weekly/plans/<uuid:plan_id>/calendar/", weekly_calendar, name="weekly-calendar"),
    path("health/", health, name="health"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "accounts/password-change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url="/accounts/password-change/done/",
        ),
        name="password_change",
    ),
    path(
        "accounts/password-change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("personal-os/direction/", direction_review, name="direction-review"),
    path("practices/<slug:slug>/direction/", practice_direction, name="practice-direction"),
    path("personal-os/practices/", context_review, name="context-review"),
    path("", include("growth.urls")),
]
