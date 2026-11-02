import json
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client
from django.urls import reverse

from growth.assessment_copy import PROMPTS, SCALES, assessment_display_copy
from growth.models import (
    AssessmentRun,
    CompositeScoreSnapshot,
    EvidenceEvent,
    LeverBaseline,
    PracticeContext,
)
from growth.services.assessment import load_assessment_assets, persist_assessment_run
from growth.services.entry import skip_suggestion
from growth.services.practice_direction import record_direction_review
from growth.services.profile import build_profile_summary
from tests.test_assessment_integration import golden_payload
from tests.test_practice_workflow import check_in_post, create_sprint


def complete_loop(client, user, sprint=None):
    """Use actual submitted evidence and closeout, not a fabricated completed flag."""
    sprint = sprint or create_sprint(user)
    actions = list(sprint.protocol.actions.order_by("sequence"))
    client.force_login(user)
    rows = (
        check_in_post(
            actions[0],
            action_completed="on",
            user_initiated="on",
            moved_beyond_transactional="on",
            meaningful_information_shared="on",
        ),
        check_in_post(
            actions[1],
            action_completed="on",
            future_interaction_scheduled="on",
            context_comparison="same_context",
        ),
        check_in_post(
            actions[2],
            follow_up_question_asked="on",
            follow_up_within_seven_days="on",
            context_comparison="same_context",
        ),
    )
    for data in rows:
        response = client.post(
            reverse("growth:practice-check-in-new", args=[sprint.pk]), {**data, "intent": "submit"}
        )
        assert response.status_code == 302
    response = client.post(
        reverse("growth:practice-review", args=[sprint.pk]),
        {"reflection": "Synthetic completed-loop receipt."},
    )
    assert response.status_code == 302
    sprint.refresh_from_db()
    assert sprint.status == "completed"
    return sprint


def test_display_copy_is_complete_and_separate_from_the_frozen_scoring_spec():
    spec = load_assessment_assets().spec
    before = deepcopy(spec)
    assessment = spec["assessment"]
    items = (
        assessment["core_items"]
        + assessment["adaptive_capability_clarifiers"]
        + assessment["adaptive_orientation_clarifiers"]
    )
    assert set(PROMPTS) == {item["id"] for item in items}
    assert len(PROMPTS) == 93
    assert all(isinstance(text, str) and text.strip() for text in PROMPTS.values())
    assert set(SCALES) == set(assessment["response_scales"])
    assert all(set(scale) == {"1", "2", "3", "4", "5"} for scale in SCALES.values())
    assert assessment_display_copy() == {"prompts": PROMPTS, "scales": SCALES}
    assert spec == before


def test_real_assessment_client_in_deterministic_dom_simulation():
    node = shutil.which("node")
    assert node, "Node.js is required, as for the frozen assessment golden test"
    result = subprocess.run(
        [node, str(Path(__file__).with_name("uxa_assessment_client.cjs"))],
        input=json.dumps(assessment_display_copy()),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["simulation"] == "passed"


@pytest.mark.django_db
def test_fresh_entry_is_narrow_and_direct_routes_do_not_show_partial_machinery(client, user):
    client.force_login(user)
    response = client.get("/")
    body = response.content.decode()
    assert response.context["entry"]["stage"] == "new"
    assert "Start assessment" in body and "How it works" in body
    for term in (
        "Recommended next",
        "demo",
        'href="/weekly/"',
        'href="/profile/"',
        'href="/practices/"',
        'href="/personal-os/"',
    ):
        assert term not in body
    for path in (
        "/profile/",
        "/weekly/",
        "/practices/",
        "/personal-os/",
        "/history/",
        "/evidence/",
    ):
        assert client.get(path).url == "/assessment/"
    assert client.get("/quick-start/").status_code == 200


@pytest.mark.django_db
def test_assessed_home_has_real_progress_and_moves_explanations_off_profile(client, user, seeded):
    persist_assessment_run(user, golden_payload())
    client.force_login(user)
    response = client.get("/")
    assert response.context["entry"]["stage"] == "assessed"
    assert b"<s>Take the assessment</s>" in response.content
    assert b"Choose your next practice" in response.content
    assert b"How it works" not in response.content
    assert b'class="definition-grid"' not in client.get("/profile/").content
    quick = client.get("/quick-start/")
    for label in ("Starting estimate", "Completion credit", "Coverage", "Remaining priority"):
        assert label.encode() in quick.content


@pytest.mark.django_db
def test_active_and_completed_home_follow_real_practice_state(client, user, seeded):
    sprint = create_sprint(user)
    client.force_login(user)
    active = client.get("/")
    assert active.context["entry"]["stage"] == "active"
    assert active.context["active_sprint"].pk == sprint.pk
    assert sprint.protocol_id not in [
        x["protocol"].pk for x in active.context["entry"]["suggestions"]
    ]
    sprint = complete_loop(client, user, sprint)
    response = client.get("/")
    assert response.context["entry"]["stage"] == "completed"
    assert response.context["active_sprint"] is None
    assert response.context["entry"]["completed"].pk == sprint.pk
    assert b"Last completed practice" in response.content
    assert b"Find your starting point" not in response.content
    assert b"Your progress" not in response.content
    assert (
        client.get(reverse("growth:practice-review-complete", args=[sprint.pk])).status_code == 200
    )


@pytest.mark.django_db
def test_home_shows_only_owner_current_epoch_direction_without_interpreting_it(
    client, user, seeded
):
    run = user.assessment_runs.first()
    record_direction_review(
        user=user,
        run=run,
        expected_revision=0,
        changes={
            key: {"state": "provided", "value": "Make time for friends <script>"}
            if key == "twelve_month_direction"
            else {"state": "unknown", "value": None}
            for key in ("mission", "anti_goals", "priority_stack", "twelve_month_direction")
        },
    )
    client.force_login(user)
    before = [p.pk for p in build_profile_summary(user).recommendations]
    response = client.get("/")
    assert b"Make time for friends &lt;script&gt;" in response.content
    assert b"not text the app scores or analyzes" in response.content
    assert [p.pk for p in build_profile_summary(user).recommendations] == before
    persist_assessment_run(user, golden_payload())
    assert b"Make time for friends" not in client.get("/").content


@pytest.mark.django_db
def test_skip_is_explicit_deferral_and_leaves_assessment_evidence_and_scores_exact(
    client, user, seeded
):
    client.force_login(user)
    response = client.get("/")
    suggestion = response.context["entry"]["suggestions"][0]
    protocol = suggestion["protocol"]
    run = response.context["summary"].assessment_run
    models = (AssessmentRun, EvidenceEvent, CompositeScoreSnapshot, LeverBaseline)
    before = [list(model.objects.values()) for model in models]
    payload = {"assessment_epoch": str(run.pk), "protocol_id": protocol.pk, "expected_revision": 0}
    assert client.post("/home/skip/", payload).status_code == 302
    context = PracticeContext.objects.get(user=user, protocol=protocol)
    assert context.disposition == "deferred" and context.defer_reason == "user_choice"
    assert context.readiness_state == "deferred"
    assert context.applicability_state == "unknown"
    assert [list(model.objects.values()) for model in models] == before
    refreshed = client.get("/")
    assert protocol.pk not in [x["protocol"].pk for x in refreshed.context["entry"]["suggestions"]]
    assert client.post("/home/skip/", payload).status_code == 409
    assert PracticeContext.objects.count() == 1


@pytest.mark.django_db
def test_skip_rejects_stale_epoch_other_owner_active_practice_and_csrf(client, user, seeded):
    run = user.assessment_runs.first()
    protocol = build_profile_summary(user).recommendations[0]
    payload = {"assessment_epoch": str(run.pk), "protocol_id": protocol.pk, "expected_revision": 0}
    guarded = Client(enforce_csrf_checks=True)
    guarded.force_login(user)
    assert guarded.post("/home/skip/", payload).status_code == 403
    other = get_user_model().objects.create_user(username="someone-else")
    client.force_login(other)
    assert client.post("/home/skip/", payload).status_code == 409
    client.force_login(user)
    assert client.get("/home/skip/").status_code == 405
    create_sprint(user)
    with pytest.raises(ValidationError, match="suggestion changed"):
        skip_suggestion(
            user=user,
            assessment_epoch=str(run.pk),
            protocol_id="PRACTICE-FRIENDSHIP-01",
            expected_revision=0,
        )
    persist_assessment_run(user, golden_payload())
    assert client.post("/home/skip/", payload).status_code == 409
    assert PracticeContext.objects.count() == 0


@pytest.mark.django_db
def test_completed_assessment_is_concise_and_mechanics_are_not_controls(client, user, seeded):
    persist_assessment_run(user, golden_payload())
    client.force_login(user)
    response = client.get("/assessment/")
    assert response.context["has_completed_assessment"]
    assert b"Assessment complete" in response.content
    assert b'<dialog id="assessment-retake-dialog"' in response.content
    assert b'<details class="panel assessment-import">' in response.content
    assert b'id="assessment-clarify"' not in response.content
    assert b'id="assessment-quality"' not in response.content
