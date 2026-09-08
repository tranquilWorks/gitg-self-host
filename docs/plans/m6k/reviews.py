#!/usr/bin/env python3
"""Repository-only, revision-bound editorial evidence. Never grants runtime credit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.plans.m6k.recovery import curriculum, fingerprint  # noqa: E402
from growth.domain.instructional_content import (  # noqa: E402
    learner_projection,
    validate_instructional_content,
)

HERE = Path(__file__).resolve().parent
QUALITY = Path("docs/authoring/quality")
DIMENSIONS = (
    "scope",
    "instructional",
    "cold_start",
    "integration",
    "learner",
    "qualified",
    "owner",
)
DEPENDENCY = {
    "instructional": "scope",
    "cold_start": "instructional",
    "integration": "cold_start",
    "learner": "integration",
    "qualified": "integration",
    "owner": "integration",
}
BOUND = {
    "scope": ("canonical", "scope", "contract"),
    "instructional": ("canonical", "scope", "instruction", "materials", "contract"),
    "cold_start": ("canonical", "scope", "instruction", "materials", "renderer", "contract"),
    "integration": (
        "canonical",
        "scope",
        "instruction",
        "materials",
        "renderer",
        "evidence",
        "contract",
    ),
}
HUMAN = {"learner": "actual_learner", "qualified": "qualified_decision", "owner": "owner_decision"}
# These literal signatures identify maintainer syntax, not semantic quality.
INTERNAL = re.compile(
    r"\b(?:retained_typed|projected_legacy|GG-[A-Z][A-Z0-9-]+|M6K-\d\d-\d\d)\b"
    r"|\b(?:stable_id|schema_version|runtime_projection)\s*[:=]"
)


class ReviewError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReviewError(message)


def unique(rows, key, label):
    values = [r[key] for r in rows]
    require(len(values) == len(set(values)), f"Duplicate {label}.")


def safe_path(root, relative):
    path = (root / relative).resolve()
    require(
        not Path(relative).is_absolute() and path.is_relative_to(root.resolve()),
        f"Artifact escapes repository: {relative}",
    )
    require(path.is_file(), f"Missing artifact: {relative}")
    return path


def load_document(path):
    # Reject duplicate mappings: PyYAML's usual last-value-wins would hide an ID.
    class StrictLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            require(key not in result, f"Duplicate mapping key {key} in {path}")
            result[key] = loader.construct_object(value_node)
        return result

    StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    return yaml.load(path.read_text(), Loader=StrictLoader)


def anchor_value(root, anchor):
    path = safe_path(root, anchor["path"])
    if not anchor["pointer"]:
        return path.read_bytes()
    require(anchor["pointer"].startswith("/"), "Artifact pointer must be an RFC 6901 pointer.")
    value = load_document(path)
    try:
        for part in anchor["pointer"][1:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            value = value[int(part)] if isinstance(value, list) else value[part]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise ReviewError(f"Unresolved artifact pointer: {anchor}") from exc
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def anchor_hash(root, anchor):
    return hashlib.sha256(anchor_value(root, anchor)).hexdigest()


def verify_anchor(root, anchor):
    require(anchor_hash(root, anchor) == anchor["sha256"], f"Stale artifact: {anchor['path']}")


def make_anchor(root, path, pointer=""):
    anchor = {"path": path, "pointer": pointer, "sha256": ""}
    anchor["sha256"] = anchor_hash(root, anchor)
    return anchor


def validate_schema(value, name):
    Draft202012Validator(json.loads((HERE / f"schemas/{name}.schema.json").read_text())).validate(
        value
    )


def mechanical_errors(exercise, cid):
    errors = []
    visible = {k: v for k, v in exercise.items() if k != "instructional_content"}
    if INTERNAL.search(json.dumps(visible, ensure_ascii=False)):
        errors.append("QA-05: internal engineering metadata in learner copy")
    guide = exercise.get("instructional_content")
    if guide:
        try:
            validate_instructional_content(guide, cid)
            for section in guide["sections"]:
                if INTERNAL.search(section["title"] + "\n" + section["body"]):
                    errors.append("QA-05: internal engineering metadata in guide")
                if section["kind"] == "prompt" and section["attempt_mode"] == "unaided":
                    visible = learner_projection(guide, cid, attempt=section["id"])
                    text = "\n".join(s["body"] for s in visible["sections"])
                    key = next(c for c in guide["checks"] if c["id"] == section["check_id"])
                    if key["body"].strip() in text:
                        errors.append("QA-02: check body copied into an unaided prompt/material")
        except (ValueError, KeyError) as exc:
            errors.append(f"QA-01/02: {exc}")
        except Exception as exc:
            # Schema errors are returned as structural defects, never as a quality pass.
            from jsonschema import ValidationError

            if not isinstance(exc, ValidationError):
                raise
            errors.append(f"QA-01/02: {exc.message}")
    return sorted(set(errors))


def corpus(root):
    canonical = curriculum(root)
    exercises = {}
    for path in sorted((root / "docs/authoring/exercises").glob("*.yaml")):
        document = load_document(path)
        for cid, entry in document["exercises"].items():
            require(
                cid not in exercises and cid.startswith(document["domain_id"] + "."),
                f"Duplicate or foreign competency: {cid}",
            )
            exercises[cid] = entry
    require(
        set(exercises) == set(canonical) and len(canonical) == 383, "Expected exact 383 sources."
    )
    return canonical, exercises


def snapshot(root, cid, canonical, exercise, *, packages_by_id=None):
    plan_path = root / QUALITY / cid / "scope-plan.json"
    plan = load_document(plan_path) if plan_path.exists() else None
    contract = [
        root / "docs/plans/m6k/program.json",
        root / "docs/plans/m6k/REVIEW_RECORD.md",
        root / "docs/plans/m6k/reviews.py",
        *sorted((root / "docs/plans/m6k/schemas").glob("*.json")),
    ]
    renderer = [
        root / "growth/domain/instructional_content.py",
        root / "growth/views_instructional.py",
        root / "data/practices/schema/instructional_content_v1.schema.json",
        root / "templates/growth/practice_guide.html",
        root / "templates/growth/partials/instructional_link.html",
        root / "growth/urls.py",
        root / "growth/static/growth/app.css",
    ]
    packages = []
    for path in (
        []
        if packages_by_id is not None
        else sorted((root / "data/practices/protocols" / cid[:2]).glob("*.yaml"))
    ):
        package = load_document(path)
        if package["parent_competency_id"] == cid:
            packages.append(package)
    if packages_by_id is not None:
        packages = [packages_by_id[cid]]
    require(len(packages) == 1, f"Expected one runtime package for {cid}.")
    scope = {k: exercise.get(k) for k in ("goal", "scope_note", "adaptation")}
    return {
        "canonical": fingerprint(canonical),
        "scope": fingerprint([scope, plan]),
        "instruction": fingerprint(
            {k: v for k, v in exercise.items() if k != "instructional_content"}
        ),
        "materials": fingerprint(exercise.get("instructional_content")),
        "renderer": fingerprint(
            {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in renderer}
        ),
        "evidence": fingerprint(packages[0]),
        "source": fingerprint(exercise),
        "contract": fingerprint(
            {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in contract}
        ),
    }


def required_criteria(dimension):
    stage = {"scope": "A", "instructional": "B", "cold_start": "C"}.get(dimension)
    if stage:
        program = json.loads((HERE / "program.json").read_text())
        return {s.split(":", 1)[0] for s in program["stages"][stage]["acceptance"]}
    return {"I1", "I2", "I3"} if dimension == "integration" else {"H1", "H2"}


def check_scope(root, cid, canonical):
    path = safe_path(root, str(QUALITY / cid / "scope-plan.json"))
    plan = load_document(path)
    validate_schema(plan, "scope-plan")
    require(
        plan["competency_id"] == cid and plan["canonical_sha256"] == fingerprint(canonical),
        "Scope plan must bind the current canonical definition.",
    )
    require(
        plan["starting_ability"].strip() and plan["prerequisites"].strip(),
        "Scope requires starting ability and prerequisites.",
    )
    require(plan["facets"], "Scope requires individual facets.")
    unique(plan["facets"], "id", "scope facet")
    for facet in plan["facets"]:
        require(
            facet["relationship"] in ("required", "role_conditional", "alternative"),
            "Invalid canonical facet relationship.",
        )
        require(
            facet["disposition"] in ("exercised", "pathway", "deferred"),
            "Invalid facet disposition.",
        )
        require(facet["reason"].strip(), "Facet needs a reasoned disposition.")
        for kind in ("teaching", "practice", "evidence", "next_route"):
            require(facet[kind], f"Missing facet {kind} anchors.")
            for anchor in facet[kind]:
                verify_anchor(root, anchor)
    require(plan["default_scope"] in ("bounded", "full"), "Declare bounded or full default scope.")
    if plan["default_scope"] == "full":
        require(
            all(f["disposition"] == "exercised" for f in plan["facets"]),
            "One-facet/default pathway cannot claim full scope with deferred facets.",
        )
    # Completeness of the facet list is A1's reasoned editorial decision, not NLP inference.


def validate_receipt(root, receipt, current, accepted, all_receipts, canonical, exercise):
    cid, dimension = receipt["competency_id"], receipt["dimension"]
    fields = BOUND.get(dimension, BOUND["integration"])
    require(
        all(
            receipt["start_revision"][k] == receipt["finish_revision"][k] == current[k]
            for k in fields
        ),
        "Stale or mid-review changed revision.",
    )
    for dep in receipt["dependencies"]:
        require(dep in accepted, f"Missing, stale or invalid dependency: {dep}")
        require(
            all_receipts[dep]["competency_id"] == cid, "Cross-competency dependency is invalid."
        )
    for anchor in receipt["inputs"] + receipt["outputs"]:
        verify_anchor(root, anchor)
    for criterion in receipt["criteria"]:
        for anchor in criterion["anchors"]:
            verify_anchor(root, anchor)
    for evidence in receipt["evidence"]:
        require(
            evidence["kind"] == evidence["claim"],
            "Simulated/static evidence cannot claim live work.",
        )
        for anchor in evidence["anchors"]:
            verify_anchor(root, anchor)
    unique(receipt["criteria"], "id", "criterion")
    unique(receipt["findings"], "id", "finding")
    for finding in receipt["findings"]:
        require(
            not finding["closed"] or finding["closure"], "Closed finding requires closure evidence."
        )
        for anchor in finding["closure"]:
            verify_anchor(root, anchor)
    if receipt["state"] != "pass":
        if receipt["state"] == "justified_not_applicable":
            require(
                dimension in ("learner", "qualified"),
                "N/A cannot excuse canonical or owner review.",
            )
            require(
                receipt["actor"]["kind"] == "human"
                and receipt["decision_reference"]
                and receipt["criteria"]
                and any(e["kind"] == HUMAN[dimension] for e in receipt["evidence"]),
                "N/A requires a real decision record.",
            )
        return
    require(
        receipt["inputs"] and receipt["outputs"] and receipt["evidence"], "Missing review evidence."
    )
    require(
        any(e["execution"] in ("executed", "inspected") for e in receipt["evidence"]),
        "Collected or unavailable evidence cannot support a pass.",
    )
    if dimension == "integration":
        require(
            any(
                e["kind"] == "software" and e["execution"] == "executed"
                for e in receipt["evidence"]
            ),
            "Integration requires executed software evidence.",
        )
    require(
        {c["id"] for c in receipt["criteria"]} == required_criteria(dimension),
        "Missing criterion evidence or unsupported blanket pass.",
    )
    require(
        all(c["verdict"] == "pass" for c in receipt["criteria"]), "Pass contains unpassed criteria."
    )
    require(
        not any(f["blocking"] and not f["closed"] for f in receipt["findings"]),
        "Unresolved blocking finding prohibits pass.",
    )
    prerequisite = DEPENDENCY.get(dimension)
    if prerequisite:
        require(
            any(all_receipts[d]["dimension"] == prerequisite for d in receipt["dependencies"]),
            f"Missing {prerequisite} dependency.",
        )
    if dimension == "scope":
        check_scope(root, cid, canonical)
    if dimension in ("instructional", "cold_start", "integration"):
        errors = mechanical_errors(exercise, cid)
        require(not errors, "; ".join(errors))
    if dimension == "instructional":
        material_ids = {
            s["id"] for s in exercise.get("instructional_content", {}).get("sections", [])
        }
        plan = load_document(safe_path(root, str(QUALITY / cid / "scope-plan.json")))
        require("promised_material_ids" in plan, "Missing explicit promised-material inventory.")
        require(
            set(plan["promised_material_ids"]) <= material_ids,
            "QA-01: Missing promised material/example.",
        )
    if dimension in HUMAN:
        require(
            receipt["actor"]["kind"] == "human" and receipt["decision_reference"],
            "Human dimension requires an actual minimized decision reference.",
        )
        require(
            any(e["kind"] == HUMAN[dimension] for e in receipt["evidence"]),
            "Agent/software evidence cannot become a human decision.",
        )
    else:
        require(
            receipt["actor"]["kind"] in ("agent", "independent_agent"), "Invalid editorial actor."
        )
    if dimension == "cold_start":
        cold = receipt["cold_start"]
        require(
            receipt["actor"]["kind"] == "independent_agent" and cold,
            "Cold start requires a separate run with staged inputs.",
        )
        require(
            all(
                receipt["actor"]["run"] != all_receipts[d]["actor"]["run"]
                for d in receipt["dependencies"]
            ),
            "Author run cannot be its own cold start.",
        )
        for key in ("bundle", "attempt", "key", "scope_audit"):
            verify_anchor(root, cold[key])
        require(
            cold["initial_inputs"] == [cold["bundle"]],
            "Initial inputs must contain only learner bundle.",
        )
        bundle = json.loads(anchor_value(root, cold["bundle"]))
        guide = exercise.get("instructional_content")
        require(guide is not None, "Cold-start bundle requires explicit learner projection.")
        require(
            bundle.get("projection")
            == learner_projection(guide, cid, attempt=bundle.get("attempt_id")),
            "Cold-start bundle differs from the final learner-only projection.",
        )
        require(
            json.loads(anchor_value(root, cold["key"])) == guide["checks"],
            "Cold-start checking artifact differs from actual keys.",
        )
        plan = load_document(safe_path(root, str(QUALITY / cid / "scope-plan.json")))
        require(
            bundle.get("prerequisites") == plan["prerequisites"],
            "Cold-start prerequisites differ from the reviewed scope plan.",
        )
        require(
            set(bundle) == {"projection", "attempt_id", "prerequisites"}
            and bundle["prerequisites"],
            "Cold-start bundle contains hidden rationale or lacks prerequisites.",
        )


def load_ledger(root, ledger_path=None):
    path = ledger_path or root / QUALITY / "ledger.json"
    ledger = load_document(path)
    validate_schema(ledger, "ledger")
    unique(ledger["receipts"], "id", "receipt ID")
    unique(ledger["receipts"], "path", "receipt path")
    receipts, previous = {}, {}
    for item in ledger["receipts"]:
        raw = safe_path(root, item["path"]).read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == item["sha256"],
            "Receipt bytes changed after indexing.",
        )
        receipt = load_document(root / item["path"])
        validate_schema(receipt, "receipt")
        require(receipt["id"] == item["id"], "Receipt/index ID mismatch.")
        require(
            Path(item["path"]).parent == QUALITY / receipt["competency_id"] / "receipts",
            "Receipt must belong to its competency directory.",
        )
        unit = (receipt["competency_id"], receipt["dimension"])
        require(receipt["previous"] == previous.get(unit), "Broken append-only receipt chain.")
        previous[unit] = item["sha256"]
        receipts[item["id"]] = receipt
    return ledger, receipts


def preserve_history(root, base):
    """Compare against a pinned Git base; hashes alone cannot prevent rebaselining history."""
    prefix = str(QUALITY)
    existing = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", base, "--", f"{prefix}/ledger.json"],
        cwd=root,
        text=True,
    )
    if not existing.strip():
        old_receipts = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", base, "--", prefix], cwd=root, text=True
        )
        require(
            not any("/receipts/" in name for name in old_receipts.splitlines()),
            "Base has receipts but no ledger; reconcile history explicitly.",
        )
        return
    result = subprocess.run(
        ["git", "show", f"{base}:{prefix}/ledger.json"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    old = json.loads(result.stdout)
    current = load_document(root / QUALITY / "ledger.json")
    require(
        current["receipts"][: len(old["receipts"])] == old["receipts"],
        "Ledger history was rewritten.",
    )
    for item in old["receipts"]:
        original = subprocess.check_output(["git", "show", f"{base}:{item['path']}"], cwd=root)
        require((root / item["path"]).read_bytes() == original, "Historical receipt was rewritten.")


def report(root, ledger_path=None):
    canonical, exercises = corpus(root)
    _ledger, receipts = load_ledger(root, ledger_path)
    require(
        all(r["competency_id"] in canonical for r in receipts.values()), "Unknown competency ID."
    )
    packages = {}
    for path in sorted((root / "data/practices/protocols").rglob("*.yaml")):
        package = load_document(path)
        cid = package["parent_competency_id"]
        require(cid not in packages, "Duplicate runtime competency ID.")
        packages[cid] = package
    require(set(packages) == set(canonical), "Runtime inventory differs from canonical IDs.")
    current = {
        cid: snapshot(root, cid, row, exercises[cid], packages_by_id=packages)
        for cid, row in canonical.items()
    }
    # Only the latest disposition for a dimension may support a new dependency.
    latest = {(r["competency_id"], r["dimension"]): rid for rid, r in receipts.items()}
    accepted, status = set(), {}
    for rid, receipt in receipts.items():
        try:
            validate_receipt(
                root,
                receipt,
                current[receipt["competency_id"]],
                accepted,
                receipts,
                canonical[receipt["competency_id"]],
                exercises[receipt["competency_id"]],
            )
            state, reason = receipt["state"], None
            if state == "pass" and latest[(receipt["competency_id"], receipt["dimension"])] == rid:
                accepted.add(rid)
        except (ValueError, KeyError, TypeError) as exc:
            state, reason = "invalid", str(exc)
        status[rid] = {"state": state, "reason": reason}
    origins = json.loads((root / "docs/plans/m6k/recovery/source-inventory.json").read_text())
    selection = load_document(root / "contracts/tailored-practice-authoring.yaml")
    selected = set(selection["implemented_competency_ids"])
    require(
        len(selected) == len(selection["implemented_competency_ids"])
        and selected <= set(canonical),
        "Invalid compiler selection.",
    )
    frozen = set(json.loads((HERE / "program.json").read_text())["frozen_legacy_ids"])
    rows = {}
    for cid in canonical:
        states = {}
        for dimension in DIMENSIONS:
            rid = latest.get((cid, dimension))
            states[dimension] = (
                {**status[rid], "receipt": rid}
                if rid
                else {"state": "pending", "reason": "No review receipt.", "receipt": None}
            )
        rows[cid] = {
            "name": canonical[cid]["name"],
            "source_origin": origins[cid]["origin"],
            "revision": current[cid],
            "runtime": "frozen_companion"
            if cid in frozen
            else "tailored"
            if cid in selected
            else "rewrite_pending",
            "reviews": states,
            "mechanical_findings": mechanical_errors(exercises[cid], cid),
        }
    return {
        "schema_version": "GG-M6K-CURRENT-REVIEWS-1.0",
        "recovered_drafts": len(rows),
        "tailored_runtime": len(selected),
        "runtime_rewrites_pending": 383 - len(selected),
        "counts": {
            d: sum(r["reviews"][d]["state"] == "pass" for r in rows.values()) for d in DIMENSIONS
        },
        "invalid_current_receipts": sum(
            v["state"] == "invalid" for r in rows.values() for v in r["reviews"].values()
        ),
        "claim_limit": "Mechanical validity and recorded dispositions only; "
        "no semantic, human-identity, "
        "live-effectiveness, deployment or mastery certification.",
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["report", "check", "snapshot"])
    parser.add_argument("--competency")
    parser.add_argument("--base", help="Pinned prior Git revision for append-only history checks.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.base:
        preserve_history(ROOT, args.base)
    if args.command == "snapshot":
        canonical, exercises = corpus(ROOT)
        require(args.competency in canonical, "Supply one canonical --competency.")
        value = snapshot(
            ROOT, args.competency, canonical[args.competency], exercises[args.competency]
        )
    else:
        value = report(ROOT)
    text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        if args.command == "check":
            require(
                args.output.read_text() == text, "Current review report is stale; regenerate it."
            )
        else:
            args.output.write_text(text)
    else:
        print(text, end="")
    if args.command == "check":
        require(value["invalid_current_receipts"] == 0, "Invalid current review receipts.")
        from docs.plans.m6k.recovery import verify

        verify(ROOT, ROOT / "docs/plans/m6k/recovery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
