"""M6K physical-capacity repair and runtime projection checks."""

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
COHORT = ("12.05", "12.08")


def test_physical_capacity_cohort_reaches_runtime_with_preserved_identity():
    selected = load_exercises(ROOT)
    bundle = load_practice_content_bundle(ROOT)
    canonical = {row["parent_competency_id"]: row for row in bundle.protocols}
    runtime = {row["parent_competency_id"]: row for row in bundle.runtime_protocols}

    assert len(selected) == 108
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


def test_strength_route_is_complete_for_entry_established_and_instruction_first():
    exercise = load_exercises(ROOT)["12.05"]
    text = render_text(learner_projection(exercise["instructional_content"], "12.05"))
    for phrase in (
        "squat or rise",
        "hinge",
        "push",
        "pull",
        "carry",
        "Entry or adapted route",
        "Established-plan route",
        "Instruction-first route",
        "Which one variable could later change",
        "This screen does not provide medical clearance",
    ):
        assert phrase in text
    assert "maximum effort" in exercise["setup"]
    assert "retained the dose" in exercise["examples"]["supportive"]
    assert "strength improvement" not in exercise["examples"]["supportive"]


def test_power_speed_coordination_and_agility_are_separate_and_bounded():
    exercise = load_exercises(ROOT)["12.08"]
    guide = exercise["instructional_content"]
    text = render_text(learner_projection(guide, "12.08"))
    for phrase in (
        "Coordination organizes",
        "Reaction is initiating",
        "Speed is completing",
        "Power is producing force rapidly",
        "Agility is rapid whole-body movement",
        "Existing-plan speed",
        "Existing-plan power",
        "Existing-plan agility",
        "Instruction-first",
    ):
        assert phrase in text
    assert "supplies no load or jump" in text
    assert "reactive agility" in text


@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id,hidden_phrase",
    [
        ("12.05", "progression-case", "progression-key", "Progress is not supported"),
        ("12.08", "classify-cases", "classification-key", "A primarily observes"),
        ("12.08", "compare-case", "comparison-key", "Progression is not supported"),
    ],
)
def test_physical_capacity_checks_are_separately_revealed(
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
        ("12.05", "route-selection", "route-key"),
        ("12.08", "select-route", "route-check"),
    ],
)
def test_compiled_physical_capacity_guides_are_served(
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
def test_recovery_allows_only_exact_declared_physical_capacity_projection(
    monkeypatch, competency_id
):
    path = next(
        path
        for path in (ROOT / "data/practices/protocols/12").glob("*.yaml")
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


def test_current_sources_bind_current_professional_support_to_both_competencies():
    sources = yaml.safe_load((ROOT / "docs/authoring/sources.yaml").read_text())["sources"]
    by_id = {row["source_id"]: row for row in sources}
    assert by_id["SRC-ACSM-2026-RESISTANCE-TRAINING"]["applicable_competency_ids"] == [
        "12.05",
        "12.08",
    ]
    assert by_id["SRC-ACSM-EP-COMPONENT-PROGRESSION"]["applicable_competency_ids"] == [
        "12.05",
        "12.08",
    ]
    assert by_id["SRC-NSCA-STRENGTH-CONDITIONING-BASICS"]["applicable_competency_ids"] == ["12.08"]
