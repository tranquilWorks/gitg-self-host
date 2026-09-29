from unittest.mock import patch

import pytest
from django.urls import reverse

from growth.models import PracticeContext
from growth.services.personal_os_browser import build_browser_priority_presentation
from growth.services.profile import build_profile_summary
from tests.test_personal_os_browser import practice_context_post


@pytest.mark.django_db
@pytest.mark.parametrize("mode", ["not_applicable", "defer"])
def test_excluded_top_choices_never_return_in_fallback(client, user, seeded, mode):
    client.force_login(user)
    summary = build_profile_summary(user)
    originals = tuple(summary.recommendations)
    for protocol in originals:
        extra = (
            {"deferred_factor": "readiness", "defer_reason": "timing"} if mode == "defer" else {}
        )
        response = client.post(
            reverse("growth:practice-context", args=[protocol.slug]),
            practice_context_post(epoch=summary.assessment_run.pk, mode=mode, **extra),
        )
        assert response.status_code == 302
    priority = build_browser_priority_presentation(user=user, summary=summary)
    assert priority.recommendations == ()
    assert not priority.context_aware
    assert tuple(build_profile_summary(user).recommendations) == originals
    # Even absence of assessment context must not bypass explicit exclusions.
    with patch(
        "growth.services.personal_os_browser._verified_assessment_context", return_value=None
    ):
        assert build_browser_priority_presentation(user=user, summary=summary).recommendations == ()


@pytest.mark.django_db
def test_partial_input_preserves_unknown_and_zero_across_revisions(client, user, seeded):
    client.force_login(user)
    summary = build_profile_summary(user)
    protocol = summary.recommendations[0]
    url = reverse("growth:practice-context", args=[protocol.slug])
    payload = practice_context_post(
        epoch=summary.assessment_run.pk, mode="partial", applicability="0"
    )
    assert client.post(url, payload).status_code == 302
    first = PracticeContext.objects.get(protocol=protocol)
    assert first.applicability_value == 0
    assert first.importance_state == "unknown"
    assert first.importance_value is None
    page = client.get(url)
    assert page.context["form"]["applicability"].value() == 0
    assert page.context["form"]["mode"].value() == "partial"
    payload["importance"] = "3"
    assert client.post(url, payload).status_code == 302
    first.refresh_from_db()
    assert first.importance_state == "unknown"
    assert PracticeContext.objects.filter(protocol=protocol).count() == 2


@pytest.mark.django_db
def test_missing_capacity_and_partial_review_keep_exclusions(client, user, seeded):
    from tests.test_personal_os_browser import assessment_context_post

    client.force_login(user)
    summary = build_profile_summary(user)
    first, second, third = summary.recommendations
    run = summary.assessment_run
    first_url = reverse("growth:practice-context", args=[first.slug])
    client.post(first_url, practice_context_post(epoch=run.pk, mode="not_applicable"))
    client.post(
        reverse("growth:practice-context", args=[second.slug]),
        practice_context_post(epoch=run.pk, mode="partial", importance="3"),
    )
    for capacity in ("unknown", "provided"):
        data = assessment_context_post(epoch=run.pk)
        if capacity == "unknown":
            data.update(capacity_state="unknown", capacity_value="")
        client.post(reverse("growth:personal-os"), data)
        result = client.get(reverse("growth:practice-list")).context["priority"]
        assert first not in result.recommendations
        assert result.recommendations == (second, third)
        assert not result.context_aware
    alternative = client.post(first_url, {"intent": "request_alternative"})
    assert alternative.context["priority"].alternative_protocol is None
    assert b"Explore another practice" in alternative.content
    assert b"not make it a personalized recommendation" in alternative.content


@pytest.mark.django_db
def test_unverified_context_suppresses_suggestions(client, user, seeded):
    from growth.services.context_priority import ContextPriorityServiceError

    summary = build_profile_summary(user)
    with patch(
        "growth.services.personal_os_browser.verified_practice_contexts",
        side_effect=ContextPriorityServiceError("synthetic"),
    ):
        result = build_browser_priority_presentation(user=user, summary=summary)
        client.force_login(user)
        home = client.get(reverse("growth:home"))
        assert b"Suggestions are paused." in home.content
        assert b"Saved context could not be verified." in home.content
    assert result.status == "unavailable"
    assert result.recommendations == ()
    assert result.recommended_ids == frozenset()
    assert result.policy_version == "GG-BROWSER-CONTEXT-SELECTION-2.0"


@pytest.mark.django_db
def test_review_horizon_does_not_expire_or_mutate_and_reconsider_requires_save(
    client, user, seeded
):
    from datetime import timedelta

    from django.utils import timezone

    from growth.models import CompositeScoreSnapshot, EvidenceEvent

    client.force_login(user)
    summary = build_profile_summary(user)
    protocol = summary.recommendations[0]
    url = reverse("growth:practice-context", args=[protocol.slug])
    client.post(
        url,
        practice_context_post(
            epoch=summary.assessment_run.pk,
            mode="defer",
            deferred_factor="readiness",
            defer_reason="timing",
            review_horizon_days="1",
        ),
    )
    original = PracticeContext.objects.get(protocol=protocol)
    before = (
        original.content_hash,
        EvidenceEvent.objects.count(),
        CompositeScoreSnapshot.objects.count(),
    )
    with patch(
        "growth.services.context_review.timezone.localdate",
        return_value=timezone.localdate() + timedelta(days=3),
    ):
        page = client.get(reverse("context-review"))
    row = page.context["review"]["page"][0]
    assert row["record"] == original
    assert row["due"]
    assert b"Ready to revisit" in page.content
    assert protocol not in page.context["priority"].recommendations
    client.get(url)
    assert PracticeContext.objects.filter(protocol=protocol).count() == 1
    assert (
        client.post(
            url,
            practice_context_post(
                epoch=summary.assessment_run.pk, mode="partial", applicability="2"
            ),
        ).status_code
        == 302
    )
    assert PracticeContext.objects.filter(protocol=protocol).count() == 2
    assert len(client.get(reverse("context-review")).context["review"]["page"]) == 0
    original.refresh_from_db()
    assert before == (
        original.content_hash,
        EvidenceEvent.objects.count(),
        CompositeScoreSnapshot.objects.count(),
    )
    assert original.disposition == "deferred"


@pytest.mark.django_db
def test_review_is_owner_and_assessment_scoped_and_requires_auth(client, user, seeded):
    from django.contrib.auth import get_user_model

    from growth.services.assessment import persist_assessment_run
    from tests.test_assessment_integration import golden_payload

    url = reverse("context-review")
    assert client.get(url).status_code == 302
    client.force_login(user)
    summary = build_profile_summary(user)
    protocol = summary.recommendations[0]
    context_url = reverse("growth:practice-context", args=[protocol.slug])
    client.post(
        context_url, practice_context_post(epoch=summary.assessment_run.pk, mode="not_applicable")
    )
    assert len(client.get(url, {"status": "not_applicable"}).context["review"]["page"]) == 1
    another = get_user_model().objects.create_user(username="other-context-owner")
    persist_assessment_run(another, golden_payload())
    client.force_login(another)
    assert len(client.get(url, {"status": "all"}).context["review"]["page"]) == 0
    client.force_login(user)
    persist_assessment_run(user, golden_payload())
    assert len(client.get(url, {"status": "all"}).context["review"]["page"]) == 0
    assert PracticeContext.objects.filter(assessment_run=summary.assessment_run).count() == 1


@pytest.mark.django_db
def test_review_pages_are_bounded_and_bad_filters_recover(client, user, seeded):
    from growth.domain.context import PRACTICE_FACTOR_IDS
    from growth.models import PracticeProtocol
    from growth.services.context import PracticeContextInput, record_context_bundle

    run = user.assessment_runs.first()
    protocols = list(
        PracticeProtocol.objects.filter(availability="active").order_by("stable_id")[:13]
    )
    record_context_bundle(
        user=user,
        assessment_run=run,
        assessment_factors={
            key: {"state": "unknown", "value": None} for key in ("season", "capacity")
        },
        practice_inputs=tuple(
            PracticeContextInput(
                protocol=p,
                factors={
                    key: {"state": "deferred" if key == "readiness" else "unknown", "value": None}
                    for key in PRACTICE_FACTOR_IDS
                },
                disposition="deferred",
                defer_reason="timing",
            )
            for p in protocols
        ),
    )
    client.force_login(user)
    url = reverse("context-review")
    first = client.get(url).context["review"]["page"]
    second = client.get(url, {"page": "2"}).context["review"]["page"]
    assert len(first) == 12 and len(second) == 1
    assert {r["record"].protocol_id for r in (*first, *second)} == {p.pk for p in protocols}
    recovery = client.get(url, {"page": "bad", "status": "<script>bad</script>"})
    assert recovery.status_code == 200
    assert recovery.context["review"]["selected"] == "deferred"
    assert b"<script>bad</script>" not in recovery.content
