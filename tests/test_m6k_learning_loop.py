"""M6K memory, skill-path and feedback-loop runtime checks."""

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
COHORT = ("10.06", "10.07", "10.08")


def test_learning_loop_reaches_runtime_with_preserved_identity_and_completion():
    selected = load_exercises(ROOT)
    bundle = load_practice_content_bundle(ROOT)
    canonical = {row["parent_competency_id"]: row for row in bundle.protocols}
    runtime = {row["parent_competency_id"]: row for row in bundle.runtime_protocols}

    assert len(selected) == 102
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


def test_memory_case_distinguishes_retrieval_routes_delay_and_versions():
    exercise = load_exercises(ROOT)["10.06"]
    text = render_text(learner_projection(exercise["instructional_content"], "10.06"))
    authored = " ".join(
        section["body"] for section in exercise["instructional_content"]["sections"]
    )
    for phrase in (
        "Recognition is noticing",
        "U [unaided]",
        "Actual delay",
        "Target V1",
        "only step 4 changes",
        "prepared future check",
    ):
        assert (
            phrase in text
            or phrase in authored
            or phrase in " ".join(action["instructions"] for action in exercise["actions"])
        )
    assert "general working-memory capacity" in exercise["goal"]


def test_skill_path_supplies_rule_dependencies_milestones_and_fresh_case():
    exercise = load_exercises(ROOT)["10.07"]
    text = render_text(learner_projection(exercise["instructional_content"], "10.07"))
    authored = " ".join(
        section["body"] for section in exercise["instructional_content"]["sections"]
    )
    for phrase in (
        "Five folders are labeled",
        "Apply the first matching rule",
        "R read the slip fields",
        "Milestone 1",
        "Hold back this slip",
        "waiting for Lee",
    ):
        assert phrase.lower() in authored.lower() or phrase.lower() in text.lower()
    assert "integration attempt" in exercise["actions"][2]["title"].lower()


def test_feedback_case_preserves_first_output_and_retests_one_semantic_repair():
    exercise = load_exercises(ROOT)["10.08"]
    text = render_text(learner_projection(exercise["instructional_content"], "10.08"))
    authored = " ".join(
        section["body"] for section in exercise["instructional_content"]["sections"]
    )
    for phrase in (
        "difference between an intended result and an observed result",
        "Version A instruction",
        "original row below the folders",
        "Error-correction record",
        "fixed before the retest",
        "Self-review is valid",
    ):
        assert phrase in text or phrase in authored
    assert "not the learner" in exercise["scope_note"]
    assert "character" in exercise["scope_note"]


@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id,hidden_phrase",
    [
        ("10.06", "first-recall", "first-recall-key", "V1 in exact order"),
        ("10.06", "version-check", "version-check-key", "V1 remains"),
        ("10.07", "dependency-map", "dependency-map-key", "minimal valid chain"),
        ("10.07", "integration-test", "integration-test-key", "G belongs in WAITING"),
        ("10.08", "literal-test", "literal-test-key", "Version A does not name TODAY"),
        ("10.08", "fresh-retest", "fresh-retest-key", "complete Version B is"),
    ],
)
def test_learning_loop_keys_are_revealed_only_after_the_prompt(
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
        ("10.06", "version-check", "version-check-key"),
        ("10.07", "integration-test", "integration-test-key"),
        ("10.08", "fresh-retest", "fresh-retest-key"),
    ],
)
def test_compiled_learning_loop_guides_and_separate_keys_are_served(
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
def test_recovery_accepts_only_the_declared_exact_learning_loop_projection(
    monkeypatch, competency_id
):
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


def test_learning_loop_sources_are_bounded_to_their_claims():
    sources = yaml.safe_load((ROOT / "docs/authoring/sources.yaml").read_text())["sources"]
    by_id = {row["source_id"]: row for row in sources}
    expected = {
        "SRC-KARPICKE-ROEDIGER-RETRIEVAL-2008": ["10.06"],
        "SRC-VAN-MERRIENBOER-4CID-2002": ["10.07"],
        "SRC-KLUGER-DENISI-FEEDBACK-1996": ["10.08"],
    }
    for source_id, competency_ids in expected.items():
        assert by_id[source_id]["applicable_competency_ids"] == competency_ids
        assert "not" in by_id[source_id]["limitations"].lower()
        assert by_id[source_id]["date_accessed"] == "2026-09-08"


def test_supplied_sequence_precedence_and_retest_facts_are_reproducible():
    v1 = ["west door", "desk", "purple pass", "room four", "blue box", "west door"]
    v2 = ["west door", "desk", "purple pass", "room six", "blue box", "west door"]
    assert [
        index for index, pair in enumerate(zip(v1, v2, strict=True), 1) if pair[0] != pair[1]
    ] == [4]
    rules = ["completed", "waiting", "today", "this week", "reference"]
    slip_b = {"completed": False, "waiting": True, "due": "today"}
    assert next(rule for rule in rules if slip_b.get(rule, False)) == "waiting"
    expected_retest = {"green": "TODAY", "white_1": "original row", "white_2": "original row"}
    assert len(expected_retest) == 3 and set(expected_retest.values()) == {"TODAY", "original row"}
