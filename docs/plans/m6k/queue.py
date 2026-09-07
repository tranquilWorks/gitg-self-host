#!/usr/bin/env python3
"""Read-only M6K task navigator; never runs tasks or approves content."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent


def build(root: Path, plan_dir: Path = HERE) -> list[dict[str, Any]]:
    program = json.loads((plan_dir / "program.json").read_text())
    if program["target_competencies"] != 383 or program["target_actions_preserved"] != 1151:
        raise ValueError("The declared canonical and preserved-action targets changed.")
    source = root / program["canonical_path"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != program["canonical_sha256"]:
        raise ValueError(
            "Canonical source changed: reconcile the plan explicitly; do not guess IDs."
        )
    curriculum = yaml.safe_load(source.read_text())["curriculum"]
    domains = curriculum["domains"]
    actual = {d["id"]: len(d["competencies"]) for d in domains}
    if actual != program["domain_counts"]:
        raise ValueError("Canonical domain inventory does not match the plan.")
    rows = [row for d in domains for row in d["competencies"]]
    if len(rows) != 383 or len({r["id"] for r in rows}) != 383:
        raise ValueError("Expected exactly 383 unique canonical competency IDs.")
    tasks = [dict(t) for t in program["pre_tasks"]]
    fixes = {cid: t["id"] for t in tasks for cid in t["competency_ids"]}
    for domain in domains:
        for row in domain["competencies"]:
            cid = row["id"]
            stem = cid.replace(".", "")
            for stage, rule in program["stages"].items():
                deps = (
                    ["M6K-01-02"]
                    if stage == "A"
                    else [f"M6K-{'A' if stage == 'B' else 'B'}-{stem}"]
                )
                if stage == "A" and cid in fixes:
                    deps.append(fixes[cid])
                tasks.append(
                    {
                        "id": f"M6K-{stage}-{stem}",
                        "title": f"{cid} {row['name']} / {rule['title']}",
                        "depends_on": deps,
                        "actor_kind": "independent_agent" if stage == "C" else "agent",
                        "competency_ids": [cid],
                        "domain_id": domain["id"],
                        "milestone": rule["milestone"],
                        "issue": rule["issue"],
                        "acceptance": rule["acceptance"],
                        "canonical_scope": row["scope"],
                        "evidence_of_progress": row["evidence_of_progress"],
                        "applicability": row.get("classification", {}),
                        "professional_boundary": row.get("professional_boundary")
                        or domain.get("professional_boundary"),
                        "authoring_path": f"docs/authoring/exercises/{domain['id']}.yaml",
                        "source_status": (
                            "Must resolve the recovered baseline; existence here is not assumed."
                        ),
                        "runtime_disposition": "frozen_companion"
                        if cid in program["frozen_legacy_ids"]
                        else "retained_typed"
                        if cid in program["retained_typed_ids"]
                        else "runtime_targeted",
                        "review_input_warning": (
                            "For C, withhold canonical_scope and author rationale "
                            "from the reviewer until after the learner-only attempt. "
                            "This task card is for the coordinator."
                        ),
                    }
                )
        tasks.append(
            {
                "id": f"M6K-06-D{domain['id']}",
                "title": f"Integrate and verify domain {domain['id']}: {domain['name']}",
                "depends_on": [f"M6K-C-{r['id'].replace('.', '')}" for r in domain["competencies"]],
                "actor_kind": "agent",
                "issue": 64,
                "competency_ids": [r["id"] for r in domain["competencies"]],
            }
        )
    groups = {
        "@all-C": [t["id"] for t in tasks if t["id"].startswith("M6K-C-")],
        "@all-domain-integration": [t["id"] for t in tasks if t["id"].startswith("M6K-06-D")],
    }
    for raw in program["post_tasks"]:
        item = dict(raw)
        item["depends_on"] = [x for d in raw["depends_on"] for x in groups.get(d, [d])]
        tasks.append(item)
    ids = {t["id"] for t in tasks}
    if len(tasks) != 1194 or len(ids) != len(tasks):
        raise ValueError("Expected 1194 distinct task IDs (1149 reviews + 45 supporting actions).")
    for t in tasks:
        if set(t["depends_on"]) - ids or t["id"] in t["depends_on"]:
            raise ValueError(f"Invalid dependencies: {t['id']}")
        if "issue" not in t:
            t["issue"] = next(
                m["issue"] for m in program["milestones"] if t["id"].startswith(m["id"] + "-")
            )
        t["contract_url"] = f"https://github.com/{program['repository']}/issues/{t['issue']}"
    visited: set[str] = set()
    while len(visited) < len(ids):
        ready = {t["id"] for t in tasks if set(t["depends_on"]) <= visited} - visited
        if not ready:
            raise ValueError("Dependency cycle detected.")
        visited |= ready
    return tasks


def declared_state(path: Path | None, tasks: list[dict[str, Any]]) -> tuple[set[str], set[str]]:
    """Advisory operator state, not evidence validation or an acceptance record."""
    data = json.loads(path.read_text()) if path else {}
    if set(data) - {"reported_completed", "reported_blocked"}:
        raise ValueError("Use only reported_completed and reported_blocked in advisory state.")
    done = data.get("reported_completed", [])
    blocked = data.get("reported_blocked", [])
    ids = {t["id"] for t in tasks}
    if not isinstance(done, list) or not isinstance(blocked, list):
        raise ValueError("Advisory state fields must be lists of task IDs.")
    if any(not isinstance(x, str) for x in done + blocked):
        raise ValueError("Task IDs must be strings.")
    if len(set(done)) != len(done) or len(set(blocked)) != len(blocked):
        raise ValueError("Duplicate state task ID.")
    if (set(done) | set(blocked)) - ids or set(done) & set(blocked):
        raise ValueError("Unknown or conflicting state task ID.")
    if "M6K-07-02" in done:
        raise ValueError(
            "This planning navigator cannot clear the human gate. "
            "Use the reviewed evidence workflow."
        )
    for t in tasks:
        if t["id"] in done and not set(t["depends_on"]) <= set(done):
            raise ValueError(f"Reported completion lacks prerequisite: {t['id']}")
    return set(done), set(blocked)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "list", "show", "next", "export"])
    parser.add_argument("task_id", nargs="?")
    parser.add_argument("--root", type=Path, default=HERE.parents[2])
    parser.add_argument("--state", type=Path, help="Advisory state only; cannot approve work.")
    args = parser.parse_args()
    try:
        tasks = build(args.root.resolve())
        done, blocked = declared_state(args.state, tasks)
        if args.command == "validate":
            print(
                "PLAN VALID: 383 competencies, 1149 review actions, "
                "27 domain integrations, 18 program actions; acyclic dependencies."
            )
            print("No content, runtime, human or specialist acceptance established.")
        elif args.command == "list":
            for t in tasks:
                print(f"{t['id']}\t{t['actor_kind']}\t{t['title']}")
        elif args.command == "export":
            print(json.dumps(tasks, indent=2, ensure_ascii=False))
        else:
            if args.command == "show":
                chosen = next((t for t in tasks if t["id"] == args.task_id), None)
                if chosen is None:
                    raise ValueError("Unknown task ID; use list.")
            else:
                chosen = next(
                    (
                        t
                        for t in tasks
                        if t["id"] not in done | blocked and set(t["depends_on"]) <= done
                    ),
                    None,
                )
            print(
                json.dumps(
                    {
                        "planner_only": True,
                        "advisory_state_is_not_acceptance": True,
                        "task": chosen,
                        "reported_blocked": sorted(blocked),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        parser.exit(2, f"M6K plan error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
