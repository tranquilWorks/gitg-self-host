from dataclasses import replace
from urllib.parse import parse_qs

import pytest
from django.http import QueryDict
from django.urls import reverse

from growth.models import AssessmentRun, CompositeScoreSnapshot, EvidenceEvent, PracticeContext
from growth.services.assessment import persist_assessment_run
from growth.services.practice import transition_sprint
from growth.services.practice_discovery import build_practice_explorer
from growth.services.profile import build_profile_summary
from tests.test_assessment_integration import golden_payload
from tests.test_weekly_execution import _plan, _sprint


@pytest.mark.django_db
def test_new_user_has_a_real_starting_path(client, user):
    client.force_login(user)
    response = client.get(reverse("growth:home"))
    assert response.status_code == 200
    assert b"Start with where you are." in response.content
    assert b"Find your starting point" in response.content
    assert b"demonstration profile" not in response.content
    assert b"Your latest provisional map is led by" not in response.content
    assert reverse("growth:assessment").encode() in response.content


@pytest.mark.django_db
def test_demo_is_labeled_and_real_assessment_does_not_show_demo_notice(client, user, seeded):
    client.force_login(user)
    response = client.get(reverse("growth:home"))
    assert b"You are exploring a demonstration profile." in response.content
    assert b"Start my own assessment" in response.content
    assert b"The Seeker" not in response.content
    persist_assessment_run(user, golden_payload())
    response = client.get(reverse("growth:home"))
    assert b"demonstration profile" not in response.content
    assert b"Make room for what matters." in response.content


@pytest.mark.django_db
def test_discovery_is_bounded_and_does_not_rerank_or_write(client, user, seeded):
    client.force_login(user)
    expected = [item.pk for item in build_profile_summary(user).recommendations]
    models = (AssessmentRun, CompositeScoreSnapshot, EvidenceEvent, PracticeContext)
    before = [model.objects.count() for model in models]
    response = client.get(reverse("growth:practice-list"))
    assert [item.pk for item in response.context["ranked_protocols"]] == expected
    assert response.context["explorer"]["page"] is None
    assert response.content.count(b'class="practice-card"') == 3
    assert b"growth/guided_entry.css" in response.content
    guide = client.get("/practices/deepen-one-existing-friendship/guide/")
    assert guide.status_code == 200
    assert b"growth/guided_entry.css" not in guide.content
    response = client.get(reverse("growth:practice-list"), {"q": "friendship"})
    assert [item.pk for item in response.context["ranked_protocols"]] == expected
    assert 0 < len(response.context["explorer"]["page"]) <= 12
    assert b"not a personalized ranking" in response.content
    assert [model.objects.count() for model in models] == before


@pytest.mark.django_db
def test_explorer_pages_cover_the_catalog_without_duplicates(seeded):
    first = build_practice_explorer(QueryDict("browse=1"))["page"]
    assert first.paginator.count == 383
    ids = [item.pk for page in first.paginator for item in page]
    assert len(ids) == len(set(ids)) == 383
    assert all(len(page) <= 12 for page in first.paginator)
    assert build_practice_explorer(QueryDict("browse=1&page=bad"))["page"].number == 1
    assert build_practice_explorer(QueryDict("browse=1&page=9999"))["page"].number == 32


@pytest.mark.django_db
def test_filters_compose_and_survive_page_navigation(seeded):
    result = build_practice_explorer(QueryDict("browse=1&domain=10"))
    assert result["page"].paginator.count == 14
    assert all(item.parent_competency.domain_id == "10" for item in result["page"])
    assert parse_qs(result["next_query"])["domain"] == ["10"]
    assert parse_qs(result["next_query"])["page"] == ["2"]
    exact = build_practice_explorer(QueryDict("domain=10&q=10.12"))
    assert [item.parent_competency_id for item in exact["page"]] == ["10.12"]
    assert build_practice_explorer(QueryDict("domain=09&q=10.12"))["page"].paginator.count == 0


@pytest.mark.django_db
def test_empty_invalid_and_hostile_filters_are_safe_and_recoverable(client, user, seeded):
    client.force_login(user)
    response = client.get(
        reverse("growth:practice-list"), {"q": '<script>alert("x")</script>', "domain": "invalid"}
    )
    assert response.status_code == 200
    assert b"No matching practices" in response.content
    assert b"Clear filters and browse all practices" in response.content
    assert b"Unavailable area" in response.content
    assert b'<script>alert("x")</script>' not in response.content
    assert response.context["explorer"]["page"].paginator.count == 0
    long_query = build_practice_explorer(QueryDict("q=" + "x" * 1000))
    assert len(long_query["query"]) == 120


@pytest.mark.django_db
def test_home_keeps_weekly_review_visible_after_practice_stops(client, user, seeded):
    sprint = _sprint(user)
    _plan(user, sprint)
    transition_sprint(sprint, "stopped")
    client.force_login(user)
    response = client.get(reverse("growth:home"))
    assert response.context["active_sprint"] is None
    assert response.context["weekly_review_pending"] is not None
    assert b"A weekly proof review is ready." in response.content


@pytest.mark.django_db
def test_verification_problem_is_visible_without_opening_details(client, user, seeded, monkeypatch):
    summary = replace(
        build_profile_summary(user), state_verification_error="Synthetic audit error."
    )
    monkeypatch.setattr("growth.views.build_profile_summary", lambda _user: summary)
    client.force_login(user)
    response = client.get(reverse("growth:home"))
    assert b'<details class="stage-panel" open>' in response.content
    assert b"Synthetic audit error." in response.content
