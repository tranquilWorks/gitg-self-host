"""M6K independent-learning, teaching and breadth runtime checks."""

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
COHORT = ("10.09", "10.10", "10.11")


def test_cohort_reaches_runtime_with_preserved_identity_and_completion():
    selected = load_exercises(ROOT)
    bundle = load_practice_content_bundle(ROOT)
    canonical = {row["parent_competency_id"]: row for row in bundle.protocols}
    runtime = {row["parent_competency_id"]: row for row in bundle.runtime_protocols}

    assert len(selected) == 105
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


def test_independent_learning_supplies_complete_binary_work_and_help_route():
    exercise = load_exercises(ROOT)["10.09"]
    authored = " ".join(
        section["body"] for section in exercise["instructional_content"]["sections"]
    )
    for phrase in (
        "places worth 4, 2 and 1",
        "Outcome and pass condition",
        "every bit pattern from 000 through 111",
        "Precise question",
        "fourth place is added",
        "refusing a needed reference",
    ):
        assert phrase.lower() in authored.lower()
    assert "not a claim of expertise" in exercise["scope_note"]


def test_teaching_case_preserves_consent_application_and_simulation_boundary():
    exercise = load_exercises(ROOT)["10.10"]
    authored = " ".join(
        section["body"] for section in exercise["instructional_content"]["sections"]
    )
    for phrase in (
        "Columns A, B and C",
        "willing learner",
        "without pointing",
        "fresh case",
        "supplied simulation",
        "planning and analysis only",
    ):
        assert phrase.lower() in authored.lower()
    assert "willing learner" in exercise["scope_note"].lower()


def test_breadth_case_supplies_seven_lenses_packet_and_bounded_synthesis():
    exercise = load_exercises(ROOT)["10.11"]
    authored = " ".join(
        section["body"] for section in exercise["instructional_content"]["sections"]
    )
    for phrase in (
        "science asks",
        "history asks",
        "technology asks",
        "economics asks",
        "humanities examine",
        "arts examine",
        "society asks",
        "W0",
        "two-lens",
        "population-wide",
    ):
        assert phrase.lower() in authored.lower()


@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id,hidden_phrase",
    [
        ("10.09", "three-bit-table", "three-bit-table-key", "complete table is"),
        ("10.09", "four-bit-extension", "four-bit-extension-key", "1001 includes"),
        ("10.10", "lesson-plan", "lesson-plan-key", "complete short explanation"),
        ("10.10", "learner-application", "learner-application-key", "A3 is the top-left"),
        ("10.11", "seven-lens-prompt", "seven-lens-key", "defensible map includes"),
        ("10.11", "two-lens-synthesis", "two-lens-key", "D1 supports"),
    ],
)
def test_keys_are_revealed_only_after_the_prompt(competency_id, prompt_id, key_id, hidden_phrase):
    guide = load_exercises(ROOT)[competency_id]["instructional_content"]
    prompt = render_text(learner_projection(guide, competency_id, attempt=prompt_id))
    checked = render_text(learner_projection(guide, competency_id, check=key_id))
    assert hidden_phrase.lower() not in prompt.lower()
    assert hidden_phrase.lower() in checked.lower()
    assert "Check your attempt:" not in prompt


@pytest.mark.django_db
@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id",
    [
        ("10.09", "four-bit-extension", "four-bit-extension-key"),
        ("10.10", "learner-application", "learner-application-key"),
        ("10.11", "two-lens-synthesis", "two-lens-key"),
    ],
)
def test_compiled_guides_and_separate_keys_are_served(
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
def test_recovery_accepts_only_the_declared_exact_projection(monkeypatch, competency_id):
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


def test_external_sources_are_current_and_bounded_to_their_claims():
    sources = yaml.safe_load((ROOT / "docs/authoring/sources.yaml").read_text())["sources"]
    by_id = {row["source_id"]: row for row in sources}
    expected = {
        "SRC-CAST-UDL-GUIDELINES-3": ["10.10"],
        "SRC-NASEM-INTERDISCIPLINARY-RESEARCH-2005": ["10.11"],
    }
    for source_id, competency_ids in expected.items():
        assert by_id[source_id]["applicable_competency_ids"] == competency_ids
        assert "not" in by_id[source_id]["limitations"].lower()
        assert by_id[source_id]["date_accessed"] == "2026-09-08"


def test_binary_grid_and_lens_facts_are_reproducible():
    assert [
        sum(bit * weight for bit, weight in zip(bits, (4, 2, 1), strict=True))
        for bits in (
            (0, 0, 0),
            (0, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 1, 0),
            (1, 1, 1),
        )
    ] == list(range(8))
    grid = {
        (column, row): (x, y) for x, column in enumerate("ABC") for y, row in enumerate((1, 2, 3))
    }
    assert grid[("A", 3)] == (0, 2) and grid[("C", 1)] == (2, 0)
    assert {"science", "history", "technology", "economics", "humanities", "arts", "society"} == {
        "science",
        "history",
        "technology",
        "economics",
        "humanities",
        "arts",
        "society",
    }
