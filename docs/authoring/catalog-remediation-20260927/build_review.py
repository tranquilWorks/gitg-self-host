"""Assemble the editorial follow-up record; never grant formal or human acceptance."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    register = json.loads((HERE / "register.json").read_text())
    canonical = yaml.safe_load(
        (ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml").read_text()
    )
    entries = {c["id"]: c for d in canonical["curriculum"]["domains"] for c in d["competencies"]}
    exercises = {}
    fingerprints = {}
    for p in (ROOT / "docs/authoring/exercises").glob("*.yaml"):
        exercises.update(yaml.safe_load(p.read_text())["exercises"])
    for cid, row in register.items():
        p = ROOT / row["source_path"]
        x = exercises[cid]
        companion = p.suffix == ".md"
        files = sorted(p.parent.glob("*.md")) if companion else [p]
        for f in files:
            fingerprints[str(f.relative_to(ROOT))] = sha(f)
        if companion:
            attempt = str((p.parent / "check-prompts.md").relative_to(ROOT))
            key = str((p.parent / "check-answers.md").relative_to(ROOT))
            scope = (
                str((p.parent / "SCOPE-MAP.md").relative_to(ROOT))
                if (p.parent / "SCOPE-MAP.md").exists()
                else row["source_path"]
            )
        else:
            attempt = row["source_path"] + "#exercises/" + cid + "/instructional_content/sections"
            key = row["source_path"] + "#exercises/" + cid + "/instructional_content/checks"
            scope = row["source_path"] + "#exercises/" + cid + "/scope_note"
            if cid == "13.16":
                attempt = row["source_path"] + "#exercises/" + cid + "/actions"
                key = row["source_path"] + "#exercises/" + cid + "/examples"
        row["status"] = (
            "editorial_followup_resolved" if row["changes"] else "reviewed_no_edit_required"
        )
        row["review"] = {
            "level": (
                "Continuing-author, nonblinded editorial desk review; "
                "not formal C1 or qualified acceptance."
            ),
            "canonical_scope": entries[cid]["scope"],
            "canonical_progress": entries[cid]["evidence_of_progress"],
            "context_and_mechanism": row["audit_finding"]["distinctive_design"],
            "scope_and_route_anchor": scope,
            "attempt_anchor": attempt,
            "corrective_key_anchor": key,
            "closure_scope": (
                "Source-level editorial defects repaired or no new defect found; "
                "original independent, actual learner and qualified "
                "review requirements remain open."
            ),
            "formal_acceptance": False,
            "independent_authorship_certified": False,
            "actual_learner_evidence": False,
            "qualified_acceptance": False,
            "primary_file_sha256": sha(p),
            "exercise_record_sha256": hashlib.sha256(
                json.dumps(x, sort_keys=True, ensure_ascii=False).encode()
            ).hexdigest(),
        }
    (HERE / "register.json").write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n")
    (HERE / "source-fingerprints.json").write_text(json.dumps(fingerprints, indent=2) + "\n")
    with (HERE / "catalog.csv").open("w", newline="") as f:
        fields = [
            "id",
            "name",
            "editorial_status",
            "distinct_context",
            "source",
            "repairs",
            "remaining_evidence",
        ]
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for cid, row in register.items():
            writer.writerow(
                {
                    "id": cid,
                    "name": row["name"],
                    "editorial_status": row["status"],
                    "distinct_context": row["review"]["context_and_mechanism"],
                    "source": row["source_path"],
                    "repairs": " | ".join(c["description"] for c in row["changes"])
                    or "Baseline material retained; no new editorial defect identified.",
                    "remaining_evidence": (
                        "Independent learner-only run; actual learner/live evidence "
                        "where claimed; qualified and owner acceptance. None fabricated."
                    ),
                }
            )
    print(
        f"Recorded {len(register)} source dispositions; "
        f"{sum(bool(x['changes']) for x in register.values())} repaired; "
        "formal acceptance remains false."
    )


if __name__ == "__main__":
    main()
