"""Actual three-competency runtime content and prospective compatibility checks."""

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
COHORT = ("10.01", "10.02", "21.03")


def test_three_real_projections_preserve_identity_completion_and_retained_rules():
    bundle = load_practice_content_bundle(ROOT)
    selected = load_exercises(ROOT)
    runtime = {p["parent_competency_id"]: p for p in bundle.runtime_protocols}
    canonical = {p["parent_competency_id"]: p for p in bundle.protocols}
    assert len(selected) == 99 and len(runtime) == 383
    assert sum(len(p["actions"]) for p in runtime.values()) == 1151
    for cid in COHORT:
        before = yaml.safe_load(
            (ROOT / f"docs/authoring/quality/{cid}/runtime-baseline.yaml").read_text()
        )
        after = canonical[cid]
        assert before["stable_id"] == after["stable_id"]
        assert before["parent_competency_id"] == after["parent_competency_id"]
        assert (
            before["completion_and_review"]["completion_rules"]
            == after["completion_and_review"]["completion_rules"]
        )
        assert (
            runtime[cid]["setup_copy"]["instructional_content"]
            == selected[cid]["instructional_content"]
        )
        for old, new in zip(
            before["intervention"]["actions"], after["intervention"]["actions"], strict=True
        ):
            assert old["stable_id"] == new["stable_id"]
            assert old["typed_evidence_identity"] == new["typed_evidence_identity"]
            assert (
                old["evidence_rules"]["measurements"][1:]
                == new["evidence_rules"]["measurements"][1:]
            )
            if cid == "10.02":
                assert old["evidence_rules"] == new["evidence_rules"]


@pytest.mark.parametrize("defect", ["completion", "retained_rule", "uncompiled_instruction"])
def test_projection_declaration_does_not_authorize_arbitrary_runtime_edits(monkeypatch, defect):
    path = ROOT / "data/practices/protocols/10/PRACTICE-DELIBERATE-PRACTICE-01.yaml"
    changed = yaml.safe_load(path.read_text())
    if defect == "completion":
        changed["completion_and_review"]["completion_rules"]["minimum_completed"] = 1
    elif defect == "retained_rule":
        changed["intervention"]["actions"][1]["evidence_rules"]["measurements"][0]["target"] = "0.9"
    else:
        changed["intervention"]["actions"][0]["instructions"] = "A different intervention"
    raw = yaml.safe_dump(changed)
    read = Path.read_text
    monkeypatch.setattr(
        Path, "read_text", lambda p, *a, **kw: raw if p == path else read(p, *a, **kw)
    )
    baseline = json.loads((ROOT / "docs/plans/m6k/recovery/runtime-invariants.json").read_text())
    with pytest.raises(ValueError, match="Protected runtime differs"):
        recovery.verify_runtime(ROOT, baseline)


def test_deliberate_practice_answers_are_separate_and_recomputed():
    guide = load_exercises(ROOT)["10.02"]["instructional_content"]
    for prompt_id, key_id, values in (
        ("baseline", "baseline-key", [3, 5, 7, 9]),
        ("retry", "retry-key", [4, 6, 8, 10]),
    ):
        prompt = render_text(learner_projection(guide, "10.02", attempt=prompt_id))
        checked = render_text(learner_projection(guide, "10.02", check=key_id))
        assert "Original total:" not in prompt
        assert f"Original total: {sum(values)}." in checked
        assert f": {sum(values) + 1}." in checked
        assert "C1" in prompt and "C4" in prompt and "Actual duration" in prompt
        assert "Check your attempt:" not in prompt
    baseline = render_text(learner_projection(guide, "10.02", check="baseline-key"))
    assert sum([5, 7, 9]) == 21 and sum([5, 7, 10]) == 22
    assert "21 and then 22" in baseline and "giving 1/4" in baseline
    retry = render_text(learner_projection(guide, "10.02", check="retry-key"))
    assert sum([4, 6, 8, 10, 100]) == 128
    assert "128 and then 129" in retry
    # A known total cannot demonstrate selecting live inputs or updating them.
    assert "typed 28" in retry and "maintenance" in retry


@pytest.mark.django_db
@pytest.mark.parametrize(
    "cid,prompt_id,key_id",
    [
        ("10.01", "delayed-transfer", "delayed-key"),
        ("10.02", "baseline", "baseline-key"),
        ("21.03", "spot-the-defect", "defect-key"),
    ],
)
def test_compiled_guides_are_served_with_explicit_answer_reveal(
    client, user, seeded, cid, prompt_id, key_id
):
    from growth.models import PracticeProtocol

    protocol = PracticeProtocol.objects.get(parent_competency_id=cid)
    client.force_login(user)
    url = reverse("growth:practice-guide", args=[protocol.slug])
    prompt = client.get(url, {"attempt": prompt_id})
    checked = client.get(url, {"check": key_id})
    assert prompt.status_code == checked.status_code == 200
    key = next(
        c for c in protocol.setup_copy["instructional_content"]["checks"] if c["id"] == key_id
    )
    assert key["body"][:40] not in prompt.content.decode()
    assert key["title"] in checked.content.decode()
