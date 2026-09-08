import copy
import shutil
from datetime import date
from pathlib import Path

import pytest
import yaml
from django.urls import reverse
from jsonschema import ValidationError

from growth.domain.instructional_content import (
    learner_projection,
    render_text,
    validate_instructional_content,
)
from growth.domain.practice_content import (
    _canonical_content_hash,
    compile_runtime_protocol,
    legacy_projection_payload,
    load_practice_content_bundle,
)
from growth.models import CompletionCreditEvent, EvidenceEvent, PracticeProtocol, PracticeSprint
from growth.services.canonical_import import CanonicalDataError, _seed_protocols
from scripts.tailored_practice_authoring import apply_exercise, load_exercises

ROOT = Path(__file__).resolve().parents[1]


def sample_guide(cid="01.04"):
    return {
        "schema_version": "GG-INSTRUCTIONAL-CONTENT-1.0",
        "competency_id": cid,
        "title": "A complete synthetic guide",
        "scored": False,
        "sections": [
            {
                "id": "teaching",
                "kind": "concept",
                "title": "Prepare",
                "body": "TEACHING_ONLY describes the method.",
            },
            {
                "id": "brief",
                "kind": "material",
                "title": "Supplied brief",
                "body": "The permitted material contains <script>unsafe()</script> as quoted text.",
            },
            {
                "id": "attempt",
                "kind": "prompt",
                "title": "Your attempt",
                "body": "UNSEEN_INPUT is the supplied new question.",
                "references": ["brief"],
                "check_id": "key",
                "attempt_mode": "unaided",
            },
        ],
        "checks": [
            {
                "id": "key",
                "title": "Check the attempt",
                "body": "ANSWER_ONLY contains the checking explanation.",
                "criteria": ["Explain the result using the supplied facts."],
            }
        ],
    }


def test_prompt_and_key_are_absent_until_explicitly_requested():
    guide = sample_guide()
    initial = render_text(learner_projection(guide, "01.04"))
    attempt = render_text(learner_projection(guide, "01.04", attempt="attempt"))
    checked = render_text(learner_projection(guide, "01.04", check="key"))
    assert "TEACHING_ONLY" in initial
    assert "UNSEEN_INPUT" not in initial and "ANSWER_ONLY" not in initial
    assert "UNSEEN_INPUT" in attempt and "ANSWER_ONLY" not in attempt
    assert "TEACHING_ONLY" not in attempt
    assert "ANSWER_ONLY" in checked and "UNSEEN_INPUT" in checked
    with pytest.raises(ValueError, match="not both"):
        learner_projection(guide, "01.04", attempt="attempt", check="key")


@pytest.mark.parametrize(
    "defect", ["missing_material", "missing_key", "foreign", "duplicate", "orphan"]
)
def test_reference_and_identity_defects_fail_closed(defect):
    guide = sample_guide()
    if defect == "missing_material":
        guide["sections"][2]["references"] = ["not-supplied"]
    elif defect == "missing_key":
        guide["sections"][2]["check_id"] = "not-supplied"
    elif defect == "foreign":
        guide["competency_id"] = "21.03"
    elif defect == "duplicate":
        guide["sections"].append(copy.deepcopy(guide["sections"][0]))
    else:
        guide["checks"].append({**guide["checks"][0], "id": "unowned"})
    with pytest.raises(ValueError):
        validate_instructional_content(guide, "01.04")


@pytest.mark.parametrize("defect", ["inline_answer", "scored", "maintainer_field"])
def test_undeclared_keys_scoring_or_metadata_fields_are_rejected(defect):
    guide = sample_guide()
    if defect == "inline_answer":
        guide["sections"][2]["answer"] = "Must be separate"
    elif defect == "scored":
        guide["scored"] = True
    else:
        guide["maintainer_compatibility"] = "Must stay in governance"
    with pytest.raises(ValidationError):
        validate_instructional_content(guide, "01.04")


def test_compiler_round_trip_preserves_action_and_completion_rules():
    bundle = load_practice_content_bundle(ROOT)
    package = next(p for p in bundle.protocols if p["parent_competency_id"] == "01.04")
    exercise = copy.deepcopy(load_exercises(ROOT)["01.04"])
    exercise["instructional_content"] = sample_guide()
    projected = apply_exercise(package, exercise)
    reloaded = yaml.safe_load(yaml.safe_dump(projected))
    runtime = compile_runtime_protocol(reloaded, bundle.activation_entries)
    assert runtime["setup_copy"]["instructional_content"] == sample_guide()
    assert reloaded["intervention"]["actions"] == package["intervention"]["actions"]
    assert reloaded["completion_and_review"] == package["completion_and_review"]
    assert "instructional_content" not in package


@pytest.mark.django_db
def test_actual_import_and_html_text_views_withhold_keys_and_leave_evidence_unchanged(
    user, seeded, client
):
    bundle = load_practice_content_bundle(ROOT)
    runtime = copy.deepcopy(bundle.runtime_protocols)
    chosen = next(p for p in runtime if p["parent_competency_id"] == "01.04")
    chosen["setup_copy"]["instructional_content"] = sample_guide()
    _seed_protocols(runtime)
    counts = (EvidenceEvent.objects.count(), CompletionCreditEvent.objects.count())
    url = reverse("growth:practice-guide", args=[chosen["slug"]])
    assert client.get(url).status_code == 302
    client.force_login(user)
    for format_value in (None, "txt", "md"):
        params = {"format": format_value} if format_value else {}
        response = client.get(url, params)
        assert response.status_code == 200
        assert response["Cache-Control"] == "private, no-store"
        assert b"UNSEEN_INPUT" not in response.content and b"ANSWER_ONLY" not in response.content
        if not format_value:
            assert b"<script>unsafe()" not in response.content
            assert b"&lt;script&gt;" in response.content
        attempt = client.get(url, {**params, "attempt": "attempt"})
        assert b"UNSEEN_INPUT" in attempt.content and b"ANSWER_ONLY" not in attempt.content
        assert b"TEACHING_ONLY" not in attempt.content
        assert b"ANSWER_ONLY" in client.get(url, {**params, "check": "key"}).content
    assert client.post(url).status_code == 405
    assert client.get(url, {"check": "unknown"}).status_code == 404
    assert client.get(url, {"format": "html"}).status_code == 404
    assert counts == (EvidenceEvent.objects.count(), CompletionCreditEvent.objects.count())
    recommendation = client.get(reverse("growth:practice-recommendation", args=[chosen["slug"]]))
    assert url.encode() in recommendation.content


@pytest.mark.django_db
def test_active_and_paused_practices_block_instructional_change_atomically(user, seeded):
    bundle = load_practice_content_bundle(ROOT)
    for status in (PracticeSprint.Status.ACTIVE, PracticeSprint.Status.PAUSED):
        runtime = copy.deepcopy(bundle.runtime_protocols)
        chosen = next(p for p in runtime if p["parent_competency_id"] == "01.04")
        sprint = PracticeSprint.objects.create(
            user=user,
            protocol_id=chosen["stable_id"],
            start_date=date(2026, 9, 8),
            person_or_context="Synthetic guide compatibility case",
            status=status,
        )
        chosen["setup_copy"]["instructional_content"] = sample_guide()
        runtime[0]["name"] = "An earlier change must also roll back"
        before = list(PracticeProtocol.objects.values_list("stable_id", "name", "setup_copy"))
        with pytest.raises(CanonicalDataError, match="active or paused practice"):
            _seed_protocols(runtime)
        assert before == list(
            PracticeProtocol.objects.values_list("stable_id", "name", "setup_copy")
        )
        sprint.delete()


def test_manifest_bound_typed_and_frozen_guides_preserve_legacy_runtime(tmp_path):
    shutil.copytree(ROOT / "data", tmp_path / "data")
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    bundle = load_practice_content_bundle(ROOT)
    root = tmp_path / "data/practices"
    package_path = next(p for p in (root / "protocols/01").glob("*.yaml") if "0104" in p.name)
    package = yaml.safe_load(package_path.read_text())
    package["instructional_content"] = sample_guide()
    package_path.write_text(yaml.safe_dump(package))
    path = root / "registries/guides/0802.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump(sample_guide("08.02")))
    manifest_path = root / "release_manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["instructional_guide_files"] = ["registries/guides/0802.yaml"]
    manifest["content_files"].append("registries/guides/0802.yaml")
    manifest["content_hash"] = _canonical_content_hash(
        [root / p for p in manifest["content_files"]], root, manifest
    )
    manifest_path.write_text(yaml.safe_dump(manifest))
    loaded = load_practice_content_bundle(tmp_path)
    assert loaded.instructional_guides["08.02"] == sample_guide("08.02")
    before = next(p for p in bundle.runtime_protocols if p["parent_competency_id"] == "08.02")
    after = next(p for p in loaded.runtime_protocols if p["parent_competency_id"] == "08.02")
    assert legacy_projection_payload(before) == legacy_projection_payload(after)
    typed = next(p for p in loaded.runtime_protocols if p["parent_competency_id"] == "01.04")
    assert typed["setup_copy"]["instructional_content"] == sample_guide()
