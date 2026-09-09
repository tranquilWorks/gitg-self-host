"""M6K apprenticeship, transmission and accessible learning runtime checks."""

import json
from itertools import pairwise
from pathlib import Path

import pytest
import yaml
from django.urls import reverse

from docs.plans.m6k import recovery
from growth.domain.instructional_content import learner_projection, render_text
from growth.domain.practice_content import load_practice_content_bundle
from scripts.tailored_practice_authoring import load_exercises

ROOT = Path(__file__).resolve().parents[1]
COHORT = ("10.12", "10.13", "10.14")


def test_cohort_reaches_runtime_with_preserved_identity_and_completion():
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


def guide_text(competency_id):
    guide = load_exercises(ROOT)[competency_id]["instructional_content"]
    return " ".join(row["body"] for row in guide["sections"] + guide["checks"])


def test_apprenticeship_preserves_guidance_and_safe_simulation_boundary():
    text = guide_text("10.12")
    for phrase in (
        "80 cm",
        "normal and slower pace",
        "Teacher confirmation or untested",
        "live feedback",
        "not restraint, climbing, rescue",
        "simulated supported improvement",
    ):
        assert phrase in text


def test_transmission_preserves_context_and_distribution_authority():
    text = guide_text("10.13")
    for phrase in (
        "notes yes, audio no",
        "volunteer team only",
        "return-only",
        "Another shift",
        "No response means pending",
        "oldest volunteer",
        "actual holder verification",
    ):
        assert phrase in text


def test_access_preserves_construct_supports_and_comparison_limits():
    text = guide_text("10.14")
    for phrase in (
        "three positions and two moves",
        "two-component presentation package",
        "not a diagnosis",
        "Preserve required supports",
        "Practice and two changed",
        "simulated observations",
        "reaching B2 alone",
    ):
        assert phrase.lower() in text.lower()


@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id,hidden_phrase",
    [
        ("10.12", "observation-prompt", "observation-key", "The written-step example"),
        ("10.12", "corrected-attempt", "corrected-attempt-key", "disparity decreases"),
        ("10.13", "draft-prompt", "draft-key", "A complete H0 handoff"),
        ("10.13", "correction-prompt", "correction-key", "D1 violates scope"),
        ("10.14", "barrier-prompt", "barrier-key", "The essential demand"),
        ("10.14", "adapted-attempt", "adapted-attempt-key", "R1 substitutes"),
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
        ("10.12", "corrected-attempt", "corrected-attempt-key"),
        ("10.13", "correction-prompt", "correction-key"),
        ("10.14", "adapted-attempt", "adapted-attempt-key"),
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


def test_sources_are_bounded_and_prior_applicability_is_unchanged():
    sources = yaml.safe_load((ROOT / "docs/authoring/sources.yaml").read_text())["sources"]
    by_id = {row["source_id"]: row for row in sources}
    assert by_id["SRC-CAST-UDL-GUIDELINES-3"]["applicable_competency_ids"] == ["10.10"]
    for source_id, cid in (
        ("SRC-UNESCO-ICH-TRANSMISSION-2003", "10.13"),
        ("SRC-CAST-UDL-ACCESS-FAQ", "10.14"),
    ):
        source = by_id[source_id]
        assert source["applicable_competency_ids"] == [cid]
        assert source["date_accessed"] == "2026-09-09"
        assert "not" in source["limitations"].lower()


def test_supplied_correction_and_route_keys_match_the_actual_task_data():
    import re

    exercises = load_exercises(ROOT)
    bow = exercises["10.12"]["instructional_content"]
    prompt = next(s["body"] for s in bow["sections"] if s["id"] == "corrected-attempt")
    pairs = re.findall(r"loops (\d+) cm and (\d+) cm", prompt)
    differences = [abs(int(a) - int(b)) for a, b in pairs]
    key = next(k["body"] for k in bow["checks"] if k["id"] == "corrected-attempt-key")
    assert len(differences) == 2
    assert f"from {differences[0]} cm to {differences[1]} cm" in key
    guide = exercises["10.14"]["instructional_content"]
    packet = next(s["body"] for s in guide["sections"] if s["id"] == "route-packet")
    routes = re.findall(r"R[12] is ([ABC][123]), ([ABC][123]), ([ABC][123])", packet)
    assert len(routes) == 2
    for route in routes:
        coords = [("ABC".index(p[0]), int(p[1])) for p in route]
        assert len(set(coords)) == 3
        assert [abs(x2 - x1) + abs(y2 - y1) for (x1, y1), (x2, y2) in pairwise(coords)] == [
            1,
            1,
        ]
        assert coords[1][1] - coords[0][1] == 1
    prompt = next(s["body"] for s in guide["sections"] if s["id"] == "adapted-attempt")
    answers = re.findall(r"R[12] response is ([ABC][123]), ([ABC][123]), ([ABC][123])", prompt)
    assert answers[0][-1] == routes[0][-1] and answers[0][1] != routes[0][1]
    assert answers[1] == routes[1]
    key = next(k["body"] for k in guide["checks"] if k["id"] == "adapted-attempt-key")
    assert f"substitutes {answers[0][1]} for {routes[0][1]}" in key
