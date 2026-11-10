"""Cross-route stage contract. These request tests are not browser validation."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from growth.models import AssessmentRun, CompletionCreditEvent, EvidenceEvent, PracticeSprint
from growth.services.evidence import build_privacy_safe_evidence_export, verify_evidence_event
from growth.services.profile import build_profile_summary
from tests.test_composite_score_state import _partial_closeout
from tests.test_practice_workflow import create_sprint

pytestmark = pytest.mark.django_db


def test_fresh_account_has_one_substantive_path_and_no_seed(client, user):
    client.force_login(user)
    home = client.get("/")
    assert b"Start assessment" in home.content
    assert b"current-practice-heading" not in home.content
    for path in (
        "/profile/",
        "/personal-os/",
        "/weekly/",
        "/practices/",
        "/history/",
        "/evidence/",
    ):
        response = client.get(path)
        assert response.status_code == 302
        assert response.url.startswith("/assessment/")
    assert not AssessmentRun.objects.filter(user=user).exists()
    assert not PracticeSprint.objects.filter(user=user).exists()
    user.refresh_from_db()
    assert not user.is_staff and not user.is_superuser


def test_assessed_without_practice_has_no_empty_review_or_closeout(client, user, seeded):
    client.force_login(user)
    run = AssessmentRun.objects.get(user=user)
    before = AssessmentRun.objects.values().get(pk=run.pk)
    weekly = client.get("/weekly/")
    assert b"Choose your next practice" in weekly.content
    assert b"Look back at your action" not in weekly.content
    assert b"Save proof-based weekly review" not in weekly.content
    assert b"No submitted proof" not in weekly.content
    for path in ("/", "/profile/", "/practices/", "/weekly/"):
        response = client.get(path)
        assert response.status_code == 200
        assert b"Open final review" not in response.content
        assert b"Technical audit details" not in response.content
    assert AssessmentRun.objects.values().get(pk=run.pk) == before
    assert not CompletionCreditEvent.objects.filter(assessment_run__user=user).exists()


def test_active_stage_has_same_attempt_and_cannot_close_early(client, user, seeded):
    sprint = create_sprint(user)
    client.force_login(user)
    path = reverse("growth:practice-sprint", args=[sprint.pk])
    assert client.get("/").context["active_sprint"].pk == sprint.pk
    assert client.get("/weekly/").context["active_sprint"].pk == sprint.pk
    assert client.get("/practices/").context["current_sprint"].pk == sprint.pk
    assert (
        client.get(reverse("growth:practice-recommendation", args=[sprint.protocol.slug])).url
        == path
    )
    guide = client.get(reverse("growth:practice-guide", args=[sprint.protocol.slug]))
    assert f'data-attempt="{sprint.pk}"'.encode() in guide.content
    assert b"Look back at your action" in client.get("/weekly/").content
    response = client.post(
        reverse("growth:practice-review", args=[sprint.pk]), {"reflection": "Not enough evidence."}
    )
    assert response.status_code == 200
    sprint.refresh_from_db()
    assert sprint.status == "active"
    assert not CompletionCreditEvent.objects.filter(sprint=sprint).exists()
    assert not EvidenceEvent.objects.filter(check_in__sprint__user=user).exists()


def test_completed_stage_read_surfaces_preserve_records_and_owner_boundary(client, user, seeded):
    sprint, _ = _partial_closeout(user)
    client.force_login(user)
    before = build_privacy_safe_evidence_export(user)
    credit = list(CompletionCreditEvent.objects.filter(sprint=sprint).values())
    summary = build_profile_summary(user)
    browser = client.get("/practices/")
    assert tuple(browser.context["ranked_protocols"]) == tuple(summary.recommendations)
    assert browser.context["current_sprint"] is None
    for path in ("/", "/weekly/", "/profile/", "/practices/", "/history/", "/evidence/"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.context.get("active_sprint") is None
        assert b"Find a starting point" not in response.content
        assert b"Technical audit details" not in response.content
    assert b"Choose your next practice" in client.get("/").content
    for event in EvidenceEvent.objects.filter(check_in__sprint__user=user):
        verify_evidence_event(event)
    assert build_privacy_safe_evidence_export(user) == before
    assert list(CompletionCreditEvent.objects.filter(sprint=sprint).values()) == credit
    other = get_user_model().objects.create_user(username="integrated-other-owner")
    client.force_login(other)
    assert client.get(reverse("growth:practice-sprint", args=[sprint.pk])).status_code == 404
