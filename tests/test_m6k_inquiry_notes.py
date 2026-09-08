"""M6K inquiry, research and knowledge-note runtime checks."""

import json
from pathlib import Path

import pytest
import yaml
from django.urls import reverse

from docs.plans.m6k import recovery
from growth.domain.instructional_content import learner_projection, render_text
from growth.domain.practice_content import load_practice_content_bundle
from scripts.tailored_practice_authoring import load_exercises

ROOT = Path(__file__).resolve().parents[1]
COHORT = ("10.03", "10.04", "10.05")


def test_inquiry_cohort_reaches_runtime_with_preserved_identity_and_completion():
    selected = load_exercises(ROOT)
    bundle = load_practice_content_bundle(ROOT)
    canonical = {row["parent_competency_id"]: row for row in bundle.protocols}
    runtime = {row["parent_competency_id"]: row for row in bundle.runtime_protocols}

    assert len(selected) == 99
    assert len(runtime) == 383
    assert sum(len(row["actions"]) for row in runtime.values()) == 1151
    for competency_id in COHORT:
        before = yaml.safe_load(
            (ROOT / f"docs/authoring/quality/{competency_id}/runtime-baseline.yaml").read_text()
        )
        after = canonical[competency_id]
        assert before["stable_id"] == after["stable_id"]
        assert before["parent_competency_id"] == after["parent_competency_id"]
        assert [row["stable_id"] for row in before["intervention"]["actions"]] == [
            row["stable_id"] for row in after["intervention"]["actions"]
        ]
        assert (
            before["completion_and_review"]["completion_rules"]
            == after["completion_and_review"]["completion_rules"]
        )
        assert (
            runtime[competency_id]["setup_copy"]["instructional_content"]
            == selected[competency_id]["instructional_content"]
        )


def test_question_formation_separates_observation_question_and_evidence_limits():
    exercise = load_exercises(ROOT)["10.03"]
    text = render_text(learner_projection(exercise["instructional_content"], "10.03"))
    for phrase in (
        "observation, interpretation and uncertainty remain separate",
        "Descriptive questions",
        "causal questions",
        "evaluative questions",
        "five overlap pairs",
        "Private question backlog",
        "revisit trigger",
    ):
        assert phrase in text
    assert "cannot establish motive or causation" in exercise["actions"][1]["instructions"]


def test_research_case_is_complete_traceable_and_date_sensitive():
    exercise = load_exercises(ROOT)["10.04"]
    text = render_text(learner_projection(exercise["instructional_content"], "10.04"))
    for phrase in (
        "Standard Borrowing Policy",
        "April Limit Update",
        "River District Neighbors",
        "Source and claim matrix",
        "publication date",
        "effective date",
        "supported / qualified / rejected / unknown",
    ):
        assert phrase in text
    assert "fictional records" in text
    assert "locators must not be opened" in text


def test_note_case_requires_capture_connection_retrieval_reuse_and_revision():
    exercise = load_exercises(ROOT)["10.05"]
    text = render_text(learner_projection(exercise["instructional_content"], "10.05"))
    for phrase in (
        "Capture records",
        "Compression rewrites",
        "Connection names",
        "Retrieval uses",
        "Revision changes",
        "Three-entry retrieval index",
        "Same-session use is practice",
    ):
        assert phrase in text or phrase in " ".join(
            action["instructions"] for action in exercise["actions"]
        )
    assert "large archive is not evidence" in text


@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id,hidden_phrase",
    [
        ("10.03", "classify-questions", "classification-key", "A is descriptive"),
        ("10.03", "resolve-question", "resolution-key", "descriptive count is five"),
        ("10.04", "source-role", "source-role-key", "P1 and P2 are primary"),
        ("10.04", "conflict-resolution", "conflict-key", "Every clause"),
        ("10.05", "note-quality", "note-rubric", "B is usable"),
        ("10.05", "delayed-application", "application-key", "sum is 30"),
    ],
)
def test_inquiry_checks_are_revealed_only_after_the_prompt(
    competency_id, prompt_id, key_id, hidden_phrase
):
    guide = load_exercises(ROOT)[competency_id]["instructional_content"]
    prompt = render_text(learner_projection(guide, competency_id, attempt=prompt_id))
    checked = render_text(learner_projection(guide, competency_id, check=key_id))
    assert hidden_phrase not in prompt
    assert hidden_phrase in checked
    assert "Check your attempt:" not in prompt


@pytest.mark.django_db
@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id",
    [
        ("10.03", "classify-questions", "classification-key"),
        ("10.04", "conflict-resolution", "conflict-key"),
        ("10.05", "delayed-application", "application-key"),
    ],
)
def test_compiled_inquiry_guides_and_separate_keys_are_served(
    client, user, seeded, competency_id, prompt_id, key_id
):
    from growth.models import PracticeProtocol

    protocol = PracticeProtocol.objects.get(parent_competency_id=competency_id)
    client.force_login(user)
    url = reverse("growth:practice-guide", args=[protocol.slug])
    prompt = client.get(url, {"attempt": prompt_id})
    checked = client.get(url, {"check": key_id})
    assert prompt.status_code == checked.status_code == 200
    key = next(
        row for row in protocol.setup_copy["instructional_content"]["checks"] if row["id"] == key_id
    )
    assert key["body"][:40] not in prompt.content.decode()
    assert key["title"] in checked.content.decode()


@pytest.mark.parametrize("competency_id", COHORT)
def test_recovery_accepts_only_the_declared_exact_inquiry_projection(monkeypatch, competency_id):
    path = next(
        path
        for path in (ROOT / "data/practices/protocols/10").glob("*.yaml")
        if yaml.safe_load(path.read_text())["parent_competency_id"] == competency_id
    )
    changed = yaml.safe_load(path.read_text())
    changed["completion_and_review"]["completion_rules"]["minimum_completed"] = 1
    raw = yaml.safe_dump(changed)
    read = Path.read_text
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda item, *args, **kwargs: raw if item == path else read(item, *args, **kwargs),
    )
    baseline = json.loads((ROOT / "docs/plans/m6k/recovery/runtime-invariants.json").read_text())
    with pytest.raises(ValueError, match="Protected runtime differs"):
        recovery.verify_runtime(ROOT, baseline)


def test_external_sources_have_bounded_current_bindings():
    sources = yaml.safe_load((ROOT / "docs/authoring/sources.yaml").read_text())["sources"]
    by_id = {row["source_id"]: row for row in sources}
    assert by_id["SRC-ACRL-INFORMATION-LITERACY-FRAMEWORK"]["applicable_competency_ids"] == [
        "10.03",
        "10.04",
    ]
    assert by_id["SRC-CORNELL-NOTE-TAKING-SYSTEM"]["applicable_competency_ids"] == ["10.05"]
    assert "product validation" in by_id["SRC-ACRL-INFORMATION-LITERACY-FRAMEWORK"]["limitations"]
    assert "not a comparative validation" in by_id["SRC-CORNELL-NOTE-TAKING-SYSTEM"]["limitations"]


def test_supplied_numeric_keys_are_independently_reproducible():
    overlaps = [(1, 2), (2, 3), (5, 6), (8, 9), (9, 10)]
    values = [2, 3, 4, 5, 16]
    assert len(overlaps) == 5
    assert sum(values) / len(values) == 6
    assert sorted(values)[len(values) // 2] == 4
    assert max(values) - min(values) == 14
