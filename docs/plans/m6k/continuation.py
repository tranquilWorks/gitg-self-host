#!/usr/bin/env python3
"""One-action M6K handoff with evidence-derived progress and persistent work leases."""

from __future__ import annotations

import argparse
import contextlib
import fnmatch
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import uuid
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docs.plans.m6k import queue, recovery, reviews  # noqa: E402

HERE = Path(__file__).resolve().parent
VERSION = "GG-M6K-CONTINUATION-1.0"
PC_REVISION = "38a7c91d8c3fe7a663a57d0353a3e60773ded20d"
PROGRAM_CRITERIA = {
    "M6K-00-01": {"sources", "provenance"},
    "M6K-00-02": {"invariants", "pending_dimensions"},
    "M6K-01-01": {"schema", "roundtrip", "retention", "exports", "browser"},
    "M6K-01-02": {"mechanical", "receipts", "negative_fixtures", "invariants"},
    "M6K-01-03": {"selection", "schema", "leases", "resume", "runner"},
}
FORBIDDEN = [
    "data/assessment/**",
    "data/model/**",
    "data/curriculum/**",
    "data/practices/registries/activation_ledger.yaml",
    "growth/models.py",
    "growth/migrations/**",
    "growth/services/canonical_import.py",
    "growth/domain/composite_scoring.py",
    "growth/services/composite_score_state.py",
    "growth/domain/context_priority.py",
    "growth/domain/typed_evidence.py",
    "growth/domain/evidence.py",
    "requirements*.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    ".github/workflows/**",
]
STAGE = {"A": "scope", "B": "instructional", "C": "cold_start"}
PHASES = {"prepared", "awaiting_contract_review", "awaiting_target_review", "interrupted"}


def require(condition, message):
    if not condition:
        raise reviews.ReviewError(message)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def check_program_record(root, record, task):
    require(record["task_hash"] == recovery.fingerprint(task), "Program task definition changed.")
    for anchor in record["bindings"]:
        reviews.verify_anchor(root, anchor)
    reviews.unique(record["criteria"], "id", "program criterion")
    for criterion in record["criteria"]:
        for anchor in criterion["anchors"]:
            reviews.verify_anchor(root, anchor)
    if record["state"] == "pass":
        expected = PROGRAM_CRITERIA.get(task["id"], {"deliverables", "verification", "limits"})
        require(
            {c["id"] for c in record["criteria"]} == expected,
            "Program completion lacks required criterion evidence.",
        )
        require(
            all(c["verdict"] == "pass" for c in record["criteria"]), "Unpassed program criterion."
        )
        require(
            record["execution"] == "executed", "Collected work cannot complete a program action."
        )
        require(record["bindings"], "Missing program artifact bindings.")
        if task["actor_kind"] == "human_gate":
            require(
                record["actor_kind"] == "human" and record["decision_reference"],
                "Human gate requires an actual authorized decision.",
            )
        else:
            require(record["actor_kind"] == "agent", "Software record actor must remain explicit.")


def progress(root, tasks, report, records):
    """Never reads the advisory navigator state, checkpoint phase or Git commit subjects."""
    definitions = {t["id"]: t for t in tasks}
    reviews.unique(records, "task_id", "program disposition")
    candidates, blocked = {}, {}
    for record in records:
        tid = record["task_id"]
        require(tid in definitions, f"Unknown program task: {tid}")
        require(
            not any(tid.startswith(f"M6K-{s}-") for s in STAGE) and not tid.startswith("M6K-06-D"),
            "Program records cannot substitute for competency review receipts.",
        )
        try:
            check_program_record(root, record, definitions[tid])
        except (ValueError, KeyError, TypeError) as exc:
            blocked[tid] = str(exc)
            continue
        if record["state"] == "blocked":
            blocked[tid] = record["reason"]
        elif record["state"] == "pass":
            candidates[tid] = record
    proofs = {}
    for task in tasks:  # queue.build supplies its deterministic dependency order.
        tid = task["id"]
        if not set(task["depends_on"]) <= proofs.keys():
            continue
        stage = next((s for s in STAGE if tid.startswith(f"M6K-{s}-")), None)
        if stage:
            cid = task["competency_ids"][0]
            row = report["rows"][cid]["reviews"][STAGE[stage]]
            if row["state"] == "pass":
                proofs[tid] = recovery.fingerprint(
                    {
                        "receipt": row["receipt"],
                        "revision": {
                            k: report["rows"][cid]["revision"][k]
                            for k in reviews.BOUND[STAGE[stage]]
                        },
                    }
                )
            elif row["state"] in ("invalid", "blocked", "revise"):
                blocked[tid] = row["reason"] or row["state"]
        elif tid.startswith("M6K-06-D"):
            rows = [report["rows"][cid]["reviews"]["integration"] for cid in task["competency_ids"]]
            if all(r["state"] == "pass" for r in rows):
                proofs[tid] = recovery.fingerprint(rows)
        elif tid in candidates:
            record = candidates[tid]
            expected = {dep: proofs[dep] for dep in task["depends_on"]}
            if record["dependencies"] != expected:
                blocked[tid] = "Missing or stale prerequisite proof."
                continue
            if task["actor_kind"] == "human_gate":
                if not all(
                    row["reviews"][d]["state"] in ("pass", "justified_not_applicable")
                    for row in report["rows"].values()
                    for d in ("learner", "qualified")
                ):
                    blocked[tid] = "Per-competency learner/qualified decisions remain open."
                    continue
                if not all(
                    row["reviews"]["owner"]["state"] == "pass" for row in report["rows"].values()
                ):
                    blocked[tid] = "Per-competency owner decisions remain open."
                    continue
            proofs[tid] = recovery.fingerprint(record)
    chosen = next(
        (
            t
            for t in tasks
            if t["id"] not in proofs
            and t["id"] not in blocked
            and set(t["depends_on"]) <= proofs.keys()
            and t["actor_kind"] != "human_gate"
        ),
        None,
    )
    for t in tasks:
        if t["actor_kind"] == "human_gate" and t["id"] not in proofs:
            blocked[t["id"]] = "Actual human gate; never dispatched to an implementation agent."
    return {"task": chosen, "proofs": proofs, "blocked": blocked}


def context(root):
    tasks = queue.build(root)
    path = root / "docs/plans/m6k/program-receipts.json"
    document = reviews.load_document(path)
    schema = json.loads((HERE / "continuation-receipts.schema.json").read_text())
    Draft202012Validator(schema).validate(document)
    report = reviews.report(root)
    result = progress(root, tasks, report, document["records"])
    result["report"] = report
    return result


def scope(task, report, root):
    ids = task["competency_ids"]
    allowed = [
        "MANIFEST.tsv",
        "contracts/active-batch.yaml",
        "contracts/repo-profile.yaml",
        "docs/authoring/quality/ledger.json",
        "docs/authoring/quality/current-report.json",
        "docs/plans/m6k/program-receipts.json",
        f"docs/evidence/{task['id']}*.md",
    ]
    for cid in ids:
        if not task["id"].startswith("M6K-C-"):
            allowed.append(f"docs/authoring/exercises/{cid[:2]}.yaml")
        allowed += [f"docs/authoring/quality/{cid}/**", f"tests/test_m6k_{cid.replace('.', '')}.py"]
        if report["rows"][cid]["runtime"] != "frozen_companion" and not task["id"].startswith(
            "M6K-C-"
        ):
            for path in sorted((root / "data/practices/protocols" / cid[:2]).glob("*.yaml")):
                if reviews.load_document(path)["parent_competency_id"] == cid:
                    allowed.append(str(path.relative_to(root)))
    if ids:
        allowed += [
            "data/practices/release_manifest.yaml",
            "reports/practice-content/**",
            "contracts/tailored-practice-authoring.yaml",
            "docs/authoring/sources.yaml",
        ]
    elif task["id"].startswith("M6K-01-"):
        allowed += [
            "docs/plans/m6k/**",
            "docs/authoring/quality/**",
            "tests/test_instructional_content.py",
            "tests/test_m6k_*.py",
            "tests/e2e/test_instructional_content.py",
            "growth/domain/instructional_content.py",
            "growth/domain/practice_content.py",
            "growth/views_instructional.py",
            "growth/urls.py",
            "growth/templatetags/**",
            "templates/growth/practice_guide.html",
            "templates/growth/partials/instructional_link.html",
            "data/practices/schema/**",
            "scripts/tailored_practice_authoring.py",
        ]
    else:
        allowed += ["docs/plans/m6k/**", "docs/authoring/quality/**", "tests/test_m6k_*.py"]
    forbidden = list(FORBIDDEN)
    for cid, row in report["rows"].items():
        if (cid not in ids or row["runtime"] == "frozen_companion") and (
            not ids or cid[:2] not in {i[:2] for i in ids}
        ):
            forbidden.append(f"data/practices/protocols/{cid[:2]}/*")
    return {"allowed_paths": sorted(set(allowed)), "forbidden_paths": sorted(set(forbidden))}


def packet(root, state):
    task = state["task"]
    if task is None:
        return None
    stage = next((s for s in STAGE if task["id"].startswith(f"M6K-{s}-")), None)
    keys = reviews.BOUND[STAGE[stage]] if stage else reviews.BOUND["integration"]
    identities = {
        cid: {k: state["report"]["rows"][cid]["revision"][k] for k in keys}
        for cid in task["competency_ids"]
    }
    program_inputs = {}
    if not task["competency_ids"]:
        for relative in (
            "growth/domain/instructional_content.py",
            "growth/views_instructional.py",
            "templates/growth/practice_guide.html",
            "templates/growth/partials/instructional_link.html",
            "docs/plans/m6k/reviews.py",
            "docs/plans/m6k/recovery/source-inventory.json",
            "docs/plans/m6k/continuation-receipts.schema.json",
        ):
            program_inputs[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    # Global tools are bound even for program tasks with no competency ID.
    binding = {
        "task": task,
        "sources": identities,
        "dependencies": {d: state["proofs"][d] for d in task["depends_on"]},
        "provider": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "program_inputs": program_inputs,
        "batch_schema": hashlib.sha256(
            (HERE / "portfolio/batch.schema.json").read_bytes()
        ).hexdigest(),
    }
    digest = recovery.fingerprint(binding)
    batch_id = task["id"] + ".R" + digest[:12]
    generated = {
        "schema_version": 1,
        "batch": {
            "id": batch_id,
            "title": task["title"],
            "goal": f"Execute only {task['id']}; retain current-revision evidence "
            "and explicit unperformed work.",
        },
        "sources": {
            "product": "products/gitg-self-host/product.yaml",
            "requirements": [
                "docs/plans/m6k/README.md",
                "docs/plans/m6k/REVIEW_RECORD.md",
                task["contract_url"],
            ],
            "milestone": task.get("milestone", task["id"][:6]),
            "baseline_commit": git(root, "rev-parse", "HEAD"),
            "control_plane_repository": "tranquilWorks/portfolio-control",
            "control_plane_path": f"products/gitg-self-host/batches/{batch_id}.yaml",
            "control_plane_revision": PC_REVISION,
        },
        "dependencies": task["depends_on"],
        "scope": scope(task, state["report"], root),
        "acceptance": task.get("acceptance")
        or [
            task["title"],
            "Retain exact artifacts and executed verification; "
            "no fabricated human or content acceptance.",
        ],
        "validation": {
            "local": ["./scripts/agent-verify.sh full", "git diff --check"],
            "focused_tests_to_add": [
                "Exercise the selected action and its negative cases; "
                "preserve neighboring entries and immutable evidence."
            ],
            "required_ci": [
                "Pilot readiness gate",
                "Playwright core journeys",
                "Docker Compose deployment drill",
            ],
        },
        "risk": {
            "class": "high",
            "hazards": ["Stale reviews or unrelated source edits are accepted."],
            "stop_conditions": [
                "Current prerequisite evidence is missing or stale.",
                "Forbidden path or neighboring competency changes.",
                "Required verification fails.",
            ],
        },
        "rollback": {
            "strategy": "Revert this isolated source batch; preserve historical evidence "
            "and restore the verified backup before any runtime import."
        },
        "evidence": {
            "output": [f"docs/evidence/{batch_id}.md"],
            "claim_boundary": "One action; software/editorial evidence only. "
            "No participant, specialist, owner, deployment or mastery acceptance is implied.",
        },
    }
    schema = json.loads((HERE / "portfolio/batch.schema.json").read_text())
    Draft202012Validator(schema).validate(generated)
    baseline = json.loads((root / "docs/plans/m6k/recovery/runtime-invariants.json").read_text())
    return {
        "version": VERSION,
        "task_id": task["id"],
        "binding": binding,
        "binding_hash": digest,
        "batch": generated,
        "actor_kind": task["actor_kind"],
        "competency_ids": task["competency_ids"],
        "blocked": state["blocked"],
        "neighbors": {
            cid: r["revision"]["source"]
            for cid, r in state["report"]["rows"].items()
            if cid not in task["competency_ids"]
        },
        "invariants": recovery.invariant_snapshot(
            root, protected_paths=list(baseline["protected_files"])
        ),
    }


def owner_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


class Store:
    """Operational SQLite state outside the application DB, shared by linked worktrees."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(
                "CREATE TABLE IF NOT EXISTS lease (id INTEGER PRIMARY KEY CHECK(id=1), "
                "token TEXT, host TEXT, pid INTEGER, binding TEXT);"
                "CREATE TABLE IF NOT EXISTS checkpoint (binding TEXT PRIMARY KEY, "
                "packet TEXT NOT NULL, phase TEXT NOT NULL, detail TEXT NOT NULL);"
            )
        os.chmod(self.path, 0o600)

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def reserve(self, pid, recover_token=None):
        require(
            type(pid) is int and pid > 0 and owner_alive(pid), "Lease requires a live owner PID."
        )
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT token,host,pid,binding FROM lease WHERE id=1").fetchone()
            if old:
                require(
                    recover_token == old[0]
                    and old[1] == socket.gethostname()
                    and not owner_alive(old[2]),
                    "Workspace already leased; recovery requires its token "
                    "and a proven dead local owner.",
                )
                db.execute("DELETE FROM lease")
            else:
                require(recover_token is None, "No abandoned lease matches this recovery request.")
            token = uuid.uuid4().hex
            db.execute(
                "INSERT INTO lease VALUES (1,?,?,?,NULL)", (token, socket.gethostname(), pid)
            )
        return token

    def require_owner(self, db, token):
        row = db.execute("SELECT token,host,pid,binding FROM lease WHERE id=1").fetchone()
        require(
            row is not None
            and row[0] == token
            and row[1] == socket.gethostname()
            and owner_alive(row[2]),
            "Missing, foreign or abandoned lease token.",
        )
        return row[3]

    def prepare(self, token, candidate):
        require(
            candidate["binding_hash"] == recovery.fingerprint(candidate["binding"]),
            "Invalid candidate binding hash.",
        )
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            bound = self.require_owner(db, token)
            require(
                bound in (None, candidate["binding_hash"]), "One lease may prepare only one action."
            )
            db.execute("UPDATE lease SET binding=? WHERE id=1", (candidate["binding_hash"],))
            previous = db.execute(
                "SELECT packet FROM checkpoint WHERE binding=?", (candidate["binding_hash"],)
            ).fetchone()
            if previous:
                # Preserve branch/PR identity and original base through unrelated commits.
                result = json.loads(previous[0])
                require(result["binding"] == candidate["binding"], "Checkpoint binding collision.")
                return result
            db.execute(
                "INSERT INTO checkpoint VALUES (?,?,?,?)",
                (candidate["binding_hash"], json.dumps(candidate), "prepared", "{}"),
            )
            return candidate

    def stored_packet(self, binding):
        with self.connect() as db:
            row = db.execute("SELECT packet FROM checkpoint WHERE binding=?", (binding,)).fetchone()
        require(row is not None, "Missing prepared checkpoint.")
        result = json.loads(row[0])
        require(
            result["binding_hash"] == binding == recovery.fingerprint(result["binding"]),
            "Corrupt checkpoint binding.",
        )
        return result

    def release(self, token, binding=None, phase="interrupted", detail=None):
        require(phase in PHASES, "A checkpoint phase cannot confer completion or approval.")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            bound = self.require_owner(db, token)
            require(binding == bound, "Release must match the reserved action.")
            if binding:
                require(
                    db.execute("SELECT 1 FROM checkpoint WHERE binding=?", (binding,)).fetchone(),
                    "Unknown checkpoint.",
                )
                db.execute(
                    "UPDATE checkpoint SET phase=?,detail=? WHERE binding=?",
                    (phase, json.dumps(detail or {}), binding),
                )
            db.execute("DELETE FROM lease")

    def status(self):
        with self.connect() as db:
            lease = db.execute("SELECT token,host,pid,binding FROM lease WHERE id=1").fetchone()
            rows = db.execute(
                "SELECT binding,phase,detail FROM checkpoint ORDER BY binding"
            ).fetchall()
        return {
            "lease": dict(zip(("token", "host", "pid", "binding"), lease, strict=True))
            if lease
            else None,
            "checkpoints": [
                {"binding": b, "phase": p, "detail": json.loads(d)} for b, p, d in rows
            ],
            "checkpoint_is_not_acceptance": True,
        }


def state_path(root):
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    return (
        common if common.is_absolute() else root / common
    ).resolve() / "m6k-continuation/state.sqlite3"


def verify_changes(root, prepared):
    state = context(root)
    require(
        all(
            state["proofs"].get(dep) == proof
            for dep, proof in prepared["binding"]["dependencies"].items()
        ),
        "Prerequisite evidence became stale during the action.",
    )
    require(
        prepared["task_id"] in state["proofs"],
        "Selected action has no valid current-revision completion evidence.",
    )
    base = prepared["batch"]["sources"]["baseline_commit"]
    reviews.preserve_history(root, base)
    record_path = "docs/plans/m6k/program-receipts.json"
    old_records = json.loads(git(root, "show", f"{base}:{record_path}"))["records"]
    new_records = reviews.load_document(root / record_path)["records"]
    require(
        [r for r in old_records if r["task_id"] != prepared["task_id"]]
        == [r for r in new_records if r["task_id"] != prepared["task_id"]],
        "Unrelated program dispositions changed.",
    )
    ledger_path = "docs/authoring/quality/ledger.json"
    old_ledger = json.loads(git(root, "show", f"{base}:{ledger_path}"))["receipts"]
    new_ledger = reviews.load_document(root / ledger_path)["receipts"]
    dimension = next(
        (STAGE[s] for s in STAGE if prepared["task_id"].startswith(f"M6K-{s}-")),
        "integration" if prepared["task_id"].startswith("M6K-06-D") else None,
    )
    for entry in new_ledger[len(old_ledger) :]:
        receipt = reviews.load_document(reviews.safe_path(root, entry["path"]))
        require(
            receipt["competency_id"] in prepared["competency_ids"]
            and receipt["dimension"] == dimension,
            "Unrelated quality review was added.",
        )
    _, exercises = reviews.corpus(root)
    for cid, expected in prepared["neighbors"].items():
        require(
            recovery.fingerprint(exercises[cid]) == expected,
            f"Neighboring competency changed: {cid}",
        )
    before = prepared["invariants"]
    after = recovery.invariant_snapshot(root, protected_paths=list(before["protected_files"]))
    require(set(before["protocols"]) == set(after["protocols"]), "Runtime inventory changed.")
    editable = {
        p
        for p in prepared["batch"]["scope"]["allowed_paths"]
        if p.startswith("data/practices/protocols/")
    }
    for path, expected in before["protected_files"].items():
        if path not in editable:
            require(after["protected_files"][path] == expected, f"Protected file changed: {path}")
    for cid, row in before["protocols"].items():
        for key in (
            "protocol_id",
            "action_ids",
            "completion_sha256",
            "evidence_sha256",
            "runtime_disposition",
        ):
            require(
                after["protocols"][cid][key] == row[key],
                f"Immutable protocol semantics changed: {cid}/{key}",
            )
    paths = git(root, "diff", "--name-only", base).splitlines()
    paths += git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    limits = prepared["batch"]["scope"]
    for path in paths:
        require(
            any(fnmatch.fnmatch(path, p) for p in limits["allowed_paths"]),
            f"Out-of-scope change: {path}",
        )
        require(
            not any(fnmatch.fnmatch(path, p) for p in limits["forbidden_paths"]),
            f"Forbidden change: {path}",
        )
    return {"verified": True, "task_id": prepared["task_id"], "completion": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["preview", "reserve", "prepare", "release", "status", "verify"]
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--owner-pid", type=int)
    parser.add_argument("--recover-token")
    parser.add_argument("--token")
    parser.add_argument("--binding")
    parser.add_argument("--phase", default="interrupted", choices=sorted(PHASES))
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "preview":
        value = context(root)
        result = {
            "version": VERSION,
            "task": value["task"],
            "blocked": value["blocked"],
            "completed_tasks": sorted(value["proofs"]),
            "dispatch_started": False,
        }
    elif args.command == "status" and not state_path(root).exists():
        result = {"lease": None, "checkpoints": [], "checkpoint_is_not_acceptance": True}
    else:
        store = Store(state_path(root))
        if args.command == "reserve":
            result = {"token": store.reserve(args.owner_pid, args.recover_token)}
        elif args.command == "prepare":
            with store.connect() as db:
                store.require_owner(db, args.token)
            state = context(root)
            candidate = packet(root, state)
            result = {
                "packet": store.prepare(args.token, candidate) if candidate else None,
                "blocked": state["blocked"],
            }
        elif args.command == "release":
            store.release(args.token, args.binding, args.phase)
            result = {"released": True, "completion": False}
        elif args.command == "verify":
            with store.connect() as db:
                require(
                    store.require_owner(db, args.token) == args.binding,
                    "Wrong action for this lease.",
                )
            result = verify_changes(root, store.stored_packet(args.binding))
        else:
            result = store.status()
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    with contextlib.suppress(BrokenPipeError):
        raise SystemExit(main())
