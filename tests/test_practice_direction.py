import json

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from growth.domain.personal_os import AUDIT_PROMPT_IDS, IDENTITY_SECTION_IDS
from growth.models import (
    AssessmentRun,
    PersonalOSRevision,
    PracticeDirectionRevision,
    PracticeProtocol,
)
from growth.services.data_lifecycle import (
    build_deletion_preview,
    delete_owner_account,
    render_owner_archive,
)
from growth.services.evidence import build_privacy_safe_evidence_export
from growth.services.personal_os import record_personal_os_revision
from growth.services.practice import start_practice
from growth.services.practice_direction import (
    DIRECTION_SECTIONS,
    connection_presentation,
    record_connection,
    record_direction_review,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def scope(user, seeded):
    return (
        user,
        user.assessment_runs.first(),
        PracticeProtocol.objects.get(slug="deepen-one-existing-friendship"),
    )


def personal(user, run, priority="Time with friends"):
    identity = {key: {"state": "unknown", "value": None} for key in IDENTITY_SECTION_IDS}
    audit = {key: {"state": "unknown", "value": None} for key in AUDIT_PROMPT_IDS}
    identity["priority_stack"] = {"state": "provided", "value": [priority]}
    identity["principles"] = {"state": "provided", "value": ["Keep promises"]}
    audit["current_truth"] = {"state": "provided", "value": "Private audit text"}
    return record_personal_os_revision(
        user=user, assessment_run=run, identity_sections=identity, audit_responses=audit
    ).revision


def choose(scope, state="unknown", **extra):
    user, run, protocol = scope
    return record_connection(
        user=user,
        run=run,
        protocol=protocol,
        state=state,
        expected_revision=extra.pop("expected_revision", 0),
        expected_personal_os=extra.pop("expected_personal_os", 0),
        **extra,
    )


def connection_post(scope, **extra):
    return {
        "assessment_epoch": str(scope[1].pk),
        "expected_revision": "0",
        "expected_personal_os": "0",
        "state": "unknown",
        "priority_index": "",
        "intended_outcome": "",
        **extra,
    }


def test_choice_revisions_are_explicit_immutable_and_idempotent(scope):
    first = choose(scope)
    assert first.state == "unknown"
    assert choose(scope, expected_revision=1).pk == first.pk
    second = choose(scope, "declined", expected_revision=1)
    third = choose(scope, "outcome", expected_revision=2, intended_outcome="Meet a friend")
    assert [row.state for row in PracticeDirectionRevision.objects.all()] == [
        "unknown",
        "declined",
        "outcome",
    ]
    assert second.intended_outcome == "" and third.revision == 3
    with pytest.raises(ValidationError):
        first.save()
    with pytest.raises(ValidationError):
        PracticeDirectionRevision.objects.filter(pk=first.pk).update(state="declined")
    with pytest.raises(ValidationError):
        first.delete()
    with pytest.raises(ValidationError):
        choose(scope, "declined", expected_revision=1)


def test_priority_keeps_exact_source_and_stale_forms_cannot_retarget(scope):
    user, run, protocol = scope
    original = personal(user, run)
    row = choose(scope, "priority", expected_personal_os=1, priority_index=0)
    personal(user, run, "Health comes first")
    assert row.chosen_text == "Time with friends"
    assert row.personal_os_id == original.pk
    assert connection_presentation(user, run, protocol)["prior_direction"]
    with pytest.raises(ValidationError):
        choose(scope, "priority", expected_revision=1, expected_personal_os=1, priority_index=0)
    current = choose(
        scope, "priority", expected_revision=1, expected_personal_os=2, priority_index=0
    )
    assert current.chosen_text == "Health comes first"
    row.refresh_from_db()
    assert row.chosen_text == "Time with friends"


@pytest.mark.parametrize(
    "state,extra",
    [
        ("priority", {"priority_index": 0}),
        ("outcome", {}),
        ("unknown", {"intended_outcome": "Hidden text"}),
        ("invalid", {}),
    ],
)
def test_invalid_choice_is_rejected(scope, state, extra):
    with pytest.raises(ValidationError):
        choose(scope, state, **extra)
    assert not PracticeDirectionRevision.objects.exists()


def test_direction_review_preserves_other_sections_and_history(scope, client):
    user, run, _ = scope
    initial = personal(user, run)
    changes = {key: {"state": "unknown", "value": None} for key in DIRECTION_SECTIONS}
    changes["mission"] = {"state": "provided", "value": "Make room for friendships"}
    result = record_direction_review(user=user, run=run, expected_revision=1, changes=changes)
    assert result.revision.principles_value == ["Keep promises"]
    assert result.revision.current_truth_value == "Private audit text"
    initial.refresh_from_db()
    assert initial.priority_stack_value == ["Time with friends"]
    with pytest.raises(ValidationError):
        record_direction_review(user=user, run=run, expected_revision=1, changes=changes)
    client.force_login(user)
    response = client.get(reverse("direction-review"))
    assert response.status_code == 200
    assert b"Time with friends" in response.content
    assert b"Private audit text" not in response.content
    assert b'name="principles_value"' not in response.content


def test_review_can_start_empty_and_form_rejects_invalid_list(scope, client):
    user, run, _ = scope
    client.force_login(user)
    payload = {"assessment_epoch": str(run.pk), "expected_revision": 0}
    for key in DIRECTION_SECTIONS:
        payload[f"{key}_state"] = "unknown"
        payload[f"{key}_value"] = ""
    url = reverse("direction-review")
    assert client.post(url, payload).status_code == 302
    assert PersonalOSRevision.objects.get().principles_state == "unknown"
    payload.update(
        expected_revision=1, priority_stack_state="provided", priority_stack_value="Same\nSame"
    )
    assert client.post(url, payload).status_code == 400
    assert PersonalOSRevision.objects.count() == 1


def test_owner_auth_epoch_and_private_surfaces(scope, client):
    user, run, protocol = scope
    url = reverse("practice-direction", args=[protocol.slug])
    assert client.get(url).status_code == 302
    client.force_login(user)
    sentinel = "PRIVATE-DIRECTION-M6L03"
    assert (
        client.post(
            url, connection_post(scope, state="outcome", intended_outcome=sentinel)
        ).status_code
        == 302
    )
    assert (
        sentinel
        in client.get(reverse("growth:practice-setup", args=[protocol.slug, 1])).content.decode()
    )
    start_practice(
        user=user, protocol=protocol, person_or_context="Friend", start_date=timezone.localdate()
    )
    weekly = client.get(reverse("growth:weekly-execution"))
    assert weekly.status_code == 200 and sentinel in weekly.content.decode()
    for name in ("growth:home", "growth:practice-list"):
        assert sentinel not in client.get(reverse(name)).content.decode()
    assert sentinel not in json.dumps(build_privacy_safe_evidence_export(user))
    other = get_user_model().objects.create_user(username="direction-other")
    with pytest.raises(ValidationError):
        record_connection(
            user=other,
            run=run,
            protocol=protocol,
            expected_revision=1,
            expected_personal_os=0,
            state="unknown",
        )
    client.force_login(other)
    assert client.get(url).status_code == 302
    client.force_login(user)
    stale = connection_post(scope, assessment_epoch="wrong-epoch", expected_revision=1)
    assert client.post(url, stale).status_code == 409
    newer = AssessmentRun.objects.create(
        user=user,
        stable_id="NEW-DIRECTION-EPOCH",
        curriculum_version=run.curriculum_version,
        assessment_version=run.assessment_version,
        source=run.source,
    )
    with pytest.raises(ValidationError):
        choose(scope, "declined", expected_revision=1)
    assert not connection_presentation(user, newer, protocol)["record"]
    assert client.post(url, connection_post(scope, expected_revision=1)).status_code == 409


def test_corruption_suppresses_private_connection(scope, client):
    user, run, protocol = scope
    row = choose(scope, "outcome", intended_outcome="PRIVATE-CORRUPTED-INTENT")
    models.QuerySet.update(
        PracticeDirectionRevision.objects.filter(pk=row.pk), content_hash="0" * 64
    )
    assert connection_presentation(user, run, protocol) == {"unavailable": True}
    client.force_login(user)
    response = client.get(reverse("practice-direction", args=[protocol.slug]))
    assert response.status_code == 409
    assert b"PRIVATE-CORRUPTED-INTENT" not in response.content
    assert client.get(reverse("growth:owner-archive")).status_code == 409
    assert (
        b"PRIVATE-CORRUPTED-INTENT"
        not in client.get(reverse("growth:practice-setup", args=[protocol.slug, 1])).content
    )


def test_connection_archive_deletion_and_fixed_redirect(scope, client):
    user, run, protocol = scope
    source = personal(user, run)
    row = choose(scope, "priority", expected_personal_os=1, priority_index=0)
    archive = render_owner_archive(user)
    assert archive == render_owner_archive(user)
    assert b"Time with friends" in archive
    for key in (row.pk, source.pk, run.pk):
        assert str(key).encode() not in archive
    assert (
        json.loads(archive)["records"]["practice_direction_revisions"][0]["personal_os_revision"]
        == 1
    )
    client.force_login(user)
    url = reverse("practice-direction", args=[protocol.slug]) + "?return=https://example.test/"
    response = client.post(
        url,
        connection_post(
            scope, expected_revision=1, expected_personal_os=1, state="declined", priority_index=0
        ),
    )
    assert response.status_code == 302
    assert response.url == reverse("growth:practice-setup", args=[protocol.slug, 1])
    assert PracticeDirectionRevision.objects.order_by("-revision").first().personal_os_id is None
    preview = build_deletion_preview(user)
    assert preview.record_counts["practice_direction_revisions"] == 2
    delete_owner_account(user=user, expected_preview_hash=preview.content_hash)
    assert not PracticeDirectionRevision.objects.exists()
