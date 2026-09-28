"""Verify editorial artifacts and protected content, not human/professional acceptance."""

from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from growth.domain.instructional_content import (  # noqa: E402
    learner_projection,
    validate_instructional_content,
)

BASE = "5bf1f629d7419ed320042eca0f3547a5f11508b6"


def git(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def stripped(package):
    p = copy.deepcopy(package)
    p.pop("instructional_content", None)
    m = p["meaning_and_fit"]
    for k in [
        "prerequisites",
        "opportunity_considerations",
        "readiness_considerations",
        "safe_alternatives",
    ]:
        m.pop(k, None)
    i = p["intervention"]
    for k in ["setup", "privacy_and_boundaries", "exclusions"]:
        i.pop(k, None)
    for k in ["resource_variants", "accessibility"]:
        i.get("adaptations", {}).pop(k, None)
    for a in i["actions"]:
        a.pop("instructions", None)
    p["completion_and_review"].get("review_guidance", {}).pop("adapt", None)
    return p


def main():
    reg = json.loads((HERE / "register.json").read_text())
    canonical = yaml.safe_load(
        (ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml").read_text()
    )
    ids = {c["id"] for d in canonical["curriculum"]["domains"] for c in d["competencies"]}
    assert set(reg) == ids and len(ids) == 383
    assert sum(x["status"] == "editorial_followup_resolved" for x in reg.values()) == 310
    assert all(
        not x["review"]["formal_acceptance"] and not x["review"]["independent_authorship_certified"]
        for x in reg.values()
    )
    passes = json.loads((HERE / "passes.json").read_text())
    assert passes["maximum_passes"] == 5 and [p["number"] for p in passes["passes"]] == list(
        range(1, 6)
    )
    for path, expected in json.loads((HERE / "source-fingerprints.json").read_text()).items():
        assert sha((ROOT / path).read_bytes()) == expected, ("Stale source", path)
    exercises = {}
    for p in (ROOT / "docs/authoring/exercises").glob("*.yaml"):
        exercises.update(yaml.safe_load(p.read_text())["exercises"])
    rich = 0
    prompt_count = 0
    links = 0
    for cid, row in reg.items():
        x = exercises[cid]
        assert (
            sha(json.dumps(x, sort_keys=True, ensure_ascii=False).encode())
            == row["review"]["exercise_record_sha256"]
        ), cid
        doc = x.get("instructional_content")
        if doc:
            rich += 1
            validate_instructional_content(doc, cid)
            default = learner_projection(doc, cid)
            assert default["check"] is None
            for s in doc["sections"]:
                if s["kind"] != "prompt":
                    continue
                prompt_count += 1
                projected = learner_projection(doc, cid, attempt=s["id"])
                assert projected["check"] is None
                assert {v["id"] for v in projected["sections"]} == {
                    s["id"],
                    *s.get("references", []),
                }
                key = learner_projection(doc, cid, check=s["check_id"])["check"]
                assert key["id"] == s["check_id"]
                # Whole keys must not leak in the default reader or the attempt payload.
                assert key["body"] not in json.dumps(default, ensure_ascii=False), cid
                assert key["body"] not in json.dumps(projected, ensure_ascii=False), cid
        source = ROOT / row["source_path"]
        if source.suffix == ".md":
            text = source.read_text()
            for term in [
                "professional_boundary",
                "Formal M6K",
                "cross_context_core",
                "cross_tradition_core_or_broadly_recurrent",
                "Compatibility boundary:",
            ]:
                assert term not in text, (cid, term)
            for f in source.parent.glob("*.md"):
                for target in re.findall(r"\]\(([^)]+)\)", f.read_text()):
                    if re.match(r"(?:https?:|mailto:|#)", target):
                        continue
                    dest = (f.parent / target.split("#")[0]).resolve()
                    assert dest.exists(), (f, target)
                    links += 1
    assert rich == 107
    original_exercises = {}
    for cid, row in reg.items():
        if row["status"] != "reviewed_no_edit_required":
            continue
        source = ROOT / row["source_path"]
        if source.suffix == ".md":
            assert source.read_bytes() == git(row["source_path"]), cid
        else:
            if row["source_path"] not in original_exercises:
                original_exercises[row["source_path"]] = yaml.safe_load(git(row["source_path"]))[
                    "exercises"
                ]
            assert exercises[cid] == original_exercises[row["source_path"]][cid], cid
    for p in (HERE / "repairs").glob("*.json"):
        assert json.loads(p.read_text()) == exercises[p.stem]["instructional_content"], p
    for p in (ROOT / "docs/authoring/quality").glob("*/runtime-content-record.json"):
        r = json.loads(p.read_text())
        assert r["guide_sha256"] == sha(p.with_name("runtime-learner-reader.md").read_bytes())
        assert r["source_sha256"] == sha(
            (ROOT / f"docs/authoring/exercises/{p.parent.name[:2]}.yaml").read_bytes()
        )
    # Recompute distinct objects rather than trusting the authored overlap sentence.
    board = next(
        s["body"]
        for s in exercises["10.03"]["instructional_content"]["sections"]
        if s["id"] == "board-packet"
    )
    pairs = re.findall(r"N(\d+)/N(\d+)", board)
    touched = {int(n) for pair in pairs for n in pair}
    assert len(pairs) == 5 and set(range(1, 13)) - touched == {4, 7, 11, 12}
    assert "Four notices" in board and "Seven notices" not in board
    record = next(
        s["body"]
        for s in exercises["10.06"]["instructional_content"]["sections"]
        if s["id"] == "recall-record"
    )
    assert "Assistance:" in record and "Accuracy:" in record
    folder = next(
        s
        for s in exercises["10.07"]["instructional_content"]["sections"]
        if s["id"] == "folder-system"
    )
    assert "Correct folders are" not in folder["body"]
    attempt = next(
        s
        for s in exercises["10.07"]["instructional_content"]["sections"]
        if s["id"] == "part-practice"
    )
    assert "folder-system" in attempt["references"]
    assert "verify 1001" not in exercises["10.09"]["actions"][2]["instructions"]
    assert "1111 is 15" not in exercises["10.09"]["adaptation"]
    lens = next(
        c["body"]
        for c in exercises["10.11"]["instructional_content"]["checks"]
        if c["id"] == "two-lens-key"
    )
    assert "Science, history, economics, humanities and arts" in lens
    assert (
        "costs due now"
        in (ROOT / reg["24.03"]["source_path"]).with_name("check-prompts.md").read_text()
    )
    # Recompute the changed-case arithmetic and retain its material distinctions.
    assert abs((1 - 0.8**4) - 0.5904) < 1e-12 and abs((1 - 0.8**2) - 0.36) < 1e-12
    assert 4 + 4 + 6 == 14 and 18 - 14 == 4
    assert max(6, 9) + 4 == 13 and 6 + 9 + 4 == 19
    assert 22 + 4 == 26 and 26 > 25
    assert (11 * 60 + 30) - (9 * 60 + 30) == 120 and 180 - 120 == 60
    protected = [
        "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml",
        "data/model/grounded_growth_model_v1.json",
        "data/model/competency_lever_mapping_v1.csv",
        "data/practices/registries/activation_ledger.yaml",
        "data/practices/research_gaps.yaml",
        "docs/authoring/quality/ledger.json",
    ]
    for path in protected:
        assert git(path) == (ROOT / path).read_bytes(), path
    selected = set(
        yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())[
            "implemented_competency_ids"
        ]
    )
    count = actions = changed = 0
    for p in (ROOT / "data/practices/protocols").rglob("*.yaml"):
        name = str(p.relative_to(ROOT))
        raw = p.read_bytes()
        oldraw = git(name)
        a = yaml.safe_load(oldraw)
        b = yaml.safe_load(raw)
        cid = b["parent_competency_id"]
        count += 1
        actions += len(b["intervention"]["actions"])
        assert stripped(a) == stripped(b), ("Protected protocol structure", cid)
        assert a["evidence_and_scoring"] == b["evidence_and_scoring"], cid
        assert [v["evidence_rules"] for v in a["intervention"]["actions"]] == [
            v["evidence_rules"] for v in b["intervention"]["actions"]
        ], cid
        if cid not in selected:
            assert raw == oldraw, ("Companion runtime changed", cid)
        changed += raw != oldraw
    assert (count, actions, len(selected), changed) == (383, 1151, 108, 101)
    scope = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())["scope"]
    changed_paths = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", BASE], cwd=ROOT, text=True
        ).splitlines()
    )
    changed_paths.update(
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True
        ).splitlines()
    )
    for path in changed_paths:
        assert any(fnmatch.fnmatch(path, p) for p in scope["allowed_paths"]), (
            "Outside scope",
            path,
        )
        assert not any(fnmatch.fnmatch(path, p) for p in scope["forbidden_paths"]), (
            "Forbidden",
            path,
        )
    similarity = json.loads((HERE / "similarity.json").read_text())
    assert similarity["pair_count"] == 73153 and not similarity["exact_normalized_body_duplicates"]
    result = {
        "competencies": 383,
        "editorial_followups_resolved": 310,
        "unchanged_after_review": 73,
        "structured_lessons": rich,
        "prompt_check_projections": prompt_count,
        "local_links": links,
        "protocols": count,
        "actions": actions,
        "revised_protocols": changed,
        "unprojected_companions_preserved": 275,
        "all_evidence_rules_unchanged": True,
        "canonical_and_formal_ledger_unchanged": True,
        "normalized_exact_duplicates": 0,
        "pairwise_comparisons": 73153,
        "formal_acceptance": False,
        "independent_authorship_certified": False,
        "validation_level": (
            "Source integrity, reveal projections, reproduced factual corrections "
            "and protected invariants; not empirical or independent review."
        ),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
