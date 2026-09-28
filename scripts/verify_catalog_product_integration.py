"""Verify and report every competency's repaired source-to-product integration."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from growth.domain.instructional_content import (  # noqa: E402
    content_fingerprint,
    learner_projection,
)
from growth.domain.practice_content import load_practice_content_bundle  # noqa: E402
from scripts.catalog_learning_guides import load_companion_guides  # noqa: E402
from scripts.tailored_practice_authoring import load_exercises  # noqa: E402

OUTPUT = ROOT / "docs/authoring/catalog-product-integration-20260928"
BASELINE = "4bb8a17"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    baseline = json.loads((OUTPUT / "integration-baseline.json").read_text())
    assert baseline["commit"].startswith(BASELINE)
    bundle = load_practice_content_bundle(ROOT)
    exercises = load_exercises(ROOT)
    companions = load_companion_guides(ROOT)
    feedback = json.loads(
        (ROOT / "docs/authoring/catalog-remediation-20260927/register.json").read_text()
    )
    assert len(bundle.protocols) == len(feedback) == len(baseline["protocols"]) == 383
    rows = []
    runtime = {p["parent_competency_id"]: p for p in bundle.runtime_protocols}
    retained = {"08.06", "09.12", "10.02", "13.02"}
    frozen = {"08.02", "11.10", "16.03", "17.03", "26.01"}
    action_count = 0
    for protocol in bundle.protocols:
        cid = protocol["parent_competency_id"]
        path = (
            ROOT
            / "data/practices/protocols"
            / protocol["domain_id"]
            / (protocol["stable_id"] + ".yaml")
        )
        old = baseline["protocols"][cid]
        assert str(path.relative_to(ROOT)) == old["path"]
        assert protocol["stable_id"] == old["stable_id"]
        actions = protocol["intervention"]["actions"]
        assert [a["stable_id"] for a in actions] == old["action_ids"]
        assert protocol["completion_and_review"]["completion_rules"] == old["completion_rules"]
        action_count += len(actions)
        if cid in frozen:
            assert sha(path) == old["sha256"]
            guide = bundle.instructional_guides[cid]
            implementation = "Frozen legacy behavior with repaired companion guide"
        else:
            guide = runtime[cid]["setup_copy"]["instructional_content"]
            assert guide == exercises[cid]["instructional_content"]
            for action, authored in zip(actions, exercises[cid]["actions"], strict=True):
                assert authored["instructions"] in action["instructions"]
                assert all(check in action["instructions"] for check in authored["checks"])
            implementation = "Tailored actions and repaired learning guide"
        if cid in frozen | retained:
            rules = json.dumps(
                [a["evidence_rules"] for a in actions], sort_keys=True, separators=(",", ":")
            )
            assert hashlib.sha256(rules.encode()).hexdigest() == old["evidence_rules_sha256"]
        if cid in retained:
            assert (
                protocol["intervention"]["privacy_and_boundaries"]
                == old["retained_privacy_and_boundaries"]
            )
        if cid in companions:
            assert guide == companions[cid]
        initial = learner_projection(guide, cid)
        for prompt in (s for s in guide["sections"] if s["kind"] == "prompt"):
            attempt = learner_projection(guide, cid, attempt=prompt["id"])
            checked = learner_projection(guide, cid, check=prompt["check_id"])
            assert initial["check"] is None and attempt["check"] is None
            assert checked["check"]["id"] == prompt["check_id"]
        source = ROOT / feedback[cid]["source_path"]
        assert sha(source) == feedback[cid]["review"]["primary_file_sha256"]
        files = (
            [source]
            if source.suffix == ".yaml"
            else sorted(p for p in source.parent.rglob("*") if p.is_file())
        )
        rows.append(
            {
                "competency_id": cid,
                "name": feedback[cid]["name"],
                "context_and_mechanism": feedback[cid]["review"]["context_and_mechanism"],
                "original_feedback": feedback[cid]["audit_finding"]["required_action"],
                "editorial_disposition": feedback[cid]["status"],
                "editorial_repairs": feedback[cid]["changes"],
                "implementation": implementation,
                "source_path": str(source.relative_to(ROOT)),
                "source_files_sha256": {str(p.relative_to(ROOT)): sha(p) for p in files},
                "runtime_path": str(path.relative_to(ROOT)),
                "runtime_sha256": sha(path),
                "guide_sha256": content_fingerprint(guide),
                "learner_route": f"/practices/{runtime[cid]['slug']}/guide/",
                "action_ids": [a["stable_id"] for a in actions],
                "prompts": [s["id"] for s in guide["sections"] if s["kind"] == "prompt"],
                "resources": [r["id"] for r in guide.get("resources", [])],
                "checks": [c["id"] for c in guide["checks"]],
                "verification": (
                    "Exact source/compiler/runtime parity; explicit reveal projection; "
                    "stable IDs and completion rules"
                ),
                "independent_authorship_certified": False,
                "actual_learner_acceptance": False,
                "qualified_acceptance": False,
            }
        )
    assert action_count == 1151
    return sorted(rows, key=lambda row: row["competency_id"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = verify()
    document = {
        "baseline": BASELINE,
        "competencies": 383,
        "actions": 1151,
        "tailored_protocols": 378,
        "frozen_legacy_with_guides": 5,
        "guides": 383,
        "unintegrated": 0,
        "entries": rows,
    }
    csvfile = io.StringIO()
    fields = [
        "competency_id",
        "name",
        "original_feedback",
        "editorial_disposition",
        "implementation",
        "source_path",
        "runtime_path",
        "learner_route",
        "verification",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    outputs = {
        "register.json": json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        "catalog.csv": csvfile.getvalue(),
    }
    for name, content in outputs.items():
        path = OUTPUT / name
        if args.check:
            assert path.read_text() == content.replace("\r\n", "\n"), f"Stale {path}"
        else:
            path.write_text(content)
    print(
        "Verified 383 guides, 378 tailored protocols, 5 frozen legacy companions "
        "and 1,151 stable actions."
    )


if __name__ == "__main__":
    main()
