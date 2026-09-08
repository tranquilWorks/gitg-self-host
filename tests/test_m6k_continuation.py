"""Synthetic acceptance cases; these fixtures confer no production review acceptance."""

import copy
import hashlib
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from docs.plans.m6k import continuation as c

ROOT = Path(__file__).resolve().parents[1]


def task(tid="M6K-00-01", deps=(), ids=(), actor="agent"):
    return {
        "id": tid,
        "title": "Synthetic action",
        "depends_on": list(deps),
        "competency_ids": list(ids),
        "actor_kind": actor,
        "contract_url": "https://github.com/tranquilWorks/gitg-self-host/issues/59",
    }


def receipt(root, selected, dependencies=None):
    (root / "executed.txt").write_text("Synthetic executed observation.\n")
    anchor = c.reviews.make_anchor(root, "executed.txt")
    return {
        "task_id": selected["id"],
        "task_hash": c.recovery.fingerprint(selected),
        "state": "pass",
        "actor_kind": "agent",
        "execution": "executed",
        "decision_reference": None,
        "reason": "Synthetic criterion evidence.",
        "dependencies": dependencies or {},
        "bindings": [anchor],
        "criteria": [
            {"id": key, "verdict": "pass", "reason": "Executed fixture", "anchors": [anchor]}
            for key in sorted(
                c.PROGRAM_CRITERIA.get(selected["id"], {"deliverables", "verification", "limits"})
            )
        ],
    }


def result(tasks, records, root, rows=None):
    return c.progress(root, tasks, {"rows": rows or {}}, records)


@pytest.fixture(scope="module")
def actual():
    # Clean-start simulation uses real source revisions and retained recovery evidence.
    # Do not freeze the live queue at today's frontier as future batches are merged.
    report = c.reviews.report(ROOT)
    for row in report["rows"].values():
        for dimension in row["reviews"]:
            row["reviews"][dimension] = {
                "state": "pending",
                "reason": "Clean-start fixture",
                "receipt": None,
            }
    records = json.loads((c.HERE / "program-receipts.json").read_text())["records"]
    initial = [r for r in records if r["task_id"] in {"M6K-00-01", "M6K-00-02"}]
    state = c.progress(ROOT, c.queue.build(ROOT), report, initial)
    return {**state, "report": report}


def test_clean_inventory_selects_first_unperformed_instructional_action(actual):
    assert actual["task"]["id"] == "M6K-01-01"
    assert set(actual["proofs"]) == {"M6K-00-01", "M6K-00-02"}
    assert len(actual["report"]["rows"]) == 383
    assert all(
        value["state"] == "pending"
        for row in actual["report"]["rows"].values()
        for value in row["reviews"].values()
    )


def test_program_receipts_use_existing_artifacts_and_dependency_proofs(tmp_path):
    first, second = task(), task("M6K-00-02", ["M6K-00-01"])
    record = receipt(tmp_path, first)
    ready = result([first, second], [record], tmp_path)
    assert ready["task"] == second
    assert ready["proofs"][first["id"]] == c.recovery.fingerprint(record)
    next_record = receipt(tmp_path, second, ready["proofs"])
    assert result([first, second], [record, next_record], tmp_path)["task"] is None


@pytest.mark.parametrize(
    "defect", ["source", "definition", "criteria", "execution", "verdict", "bindings"]
)
def test_program_completion_fails_closed(tmp_path, defect):
    selected = task()
    record = receipt(tmp_path, selected)
    if defect == "source":
        (tmp_path / "executed.txt").write_text("Changed after review")
    elif defect == "definition":
        selected["title"] = "Changed task"
    elif defect == "criteria":
        record["criteria"].pop()
    elif defect == "execution":
        record["execution"] = "collected"
    elif defect == "verdict":
        record["criteria"][0]["verdict"] = "pending"
    else:
        record["bindings"] = []
    state = result([selected], [record], tmp_path)
    assert not state["proofs"]
    assert selected["id"] in state["blocked"]


def test_stale_dependency_does_not_block_independent_work(tmp_path):
    first, second, other = task(), task("M6K-00-02", ["M6K-00-01"]), task("M6K-01-02")
    record = receipt(tmp_path, first)
    stale = receipt(tmp_path, second, {first["id"]: "0" * 64})
    state = result([first, second, other], [record, stale], tmp_path)
    assert state["task"] == other
    assert "stale prerequisite" in state["blocked"][second["id"]]


def test_duplicate_records_and_program_substitute_for_content_are_rejected(tmp_path):
    selected = task()
    record = receipt(tmp_path, selected)
    with pytest.raises(ValueError, match="Duplicate"):
        result([selected], [record, record], tmp_path)
    selected = task("M6K-A-1001", ids=["10.01"])
    with pytest.raises(ValueError, match="substitute"):
        result([selected], [receipt(tmp_path, selected)], tmp_path)


def test_schema_rejects_advisory_completion(tmp_path):
    document = {
        "schema_version": "GG-M6K-PROGRAM-RECEIPTS-1.0",
        "records": [receipt(tmp_path, task())],
    }
    validator = Draft202012Validator(
        json.loads((c.HERE / "continuation-receipts.schema.json").read_text())
    )
    validator.validate(document)
    document["reported_completed"] = ["M6K-01-01"]
    with pytest.raises(ValidationError):
        validator.validate(document)


def test_quality_progress_uses_validated_dimension_and_relevant_revision(tmp_path):
    a, b = task("M6K-A-1001", ids=["10.01"]), task("M6K-B-1001", ["M6K-A-1001"], ["10.01"])
    row = {
        "revision": dict.fromkeys(c.reviews.BOUND["integration"], "fixture"),
        "reviews": {
            "scope": {"state": "pass", "receipt": "a-real-fixture", "reason": None},
            "instructional": {"state": "pending", "receipt": None, "reason": "Missing"},
        },
    }
    state = result([a, b], [], tmp_path, {"10.01": row})
    assert state["task"] == b
    row["revision"]["instruction"] = "changed"
    assert state["proofs"] == result([a, b], [], tmp_path, {"10.01": row})["proofs"]
    row["reviews"]["scope"]["state"] = "invalid"
    state = result([a, b], [], tmp_path, {"10.01": row})
    assert not state["proofs"] and state["task"] is None


def test_human_gate_cannot_be_cleared_by_agent_or_missing_human_decisions(tmp_path):
    selected = task("M6K-07-02", actor="human_gate")
    record = receipt(tmp_path, selected)
    assert not result([selected], [record], tmp_path)["proofs"]
    record.update(actor_kind="human", decision_reference="Synthetic owner decision")
    row = {"reviews": {d: {"state": "pending"} for d in ("learner", "qualified", "owner")}}
    assert not result([selected], [record], tmp_path, {"10.01": row})["proofs"]
    for value in row["reviews"].values():
        value["state"] = "pass"
    state = result([selected], [record], tmp_path, {"10.01": row})
    assert selected["id"] in state["proofs"] and state["task"] is None


def test_generated_packet_schema_and_stable_binding(actual, monkeypatch):
    first = c.packet(ROOT, actual)
    Draft202012Validator(json.loads((c.HERE / "portfolio/batch.schema.json").read_text())).validate(
        first["batch"]
    )
    monkeypatch.setattr(c, "git", lambda *args: "a" * 40)
    second = c.packet(ROOT, actual)
    assert first["binding_hash"] == second["binding_hash"]
    assert (
        first["batch"]["sources"]["baseline_commit"]
        != second["batch"]["sources"]["baseline_commit"]
    )
    assert len(first["neighbors"]) == 383


def test_pinned_portfolio_reference_blobs_are_exact():
    provenance = json.loads((c.HERE / "portfolio/provenance.json").read_text())
    assert provenance["revision"] == c.PC_REVISION
    for record in provenance["files"]:
        data = (ROOT / record["local_path"]).read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert digest == record["git_blob"]


@pytest.mark.parametrize(
    "tid,cid,runtime_edit",
    [("M6K-B-1001", "10.01", True), ("M6K-C-1001", "10.01", False), ("M6K-B-0802", "08.02", False)],
)
def test_exact_content_and_frozen_scope(actual, tid, cid, runtime_edit):
    limits = c.scope(task(tid, ids=[cid]), actual["report"], ROOT)
    packages = [p for p in limits["allowed_paths"] if p.startswith("data/practices/protocols/")]
    assert bool(packages) is runtime_edit
    assert all(c.reviews.load_document(ROOT / p)["parent_competency_id"] == cid for p in packages)
    assert (f"docs/authoring/exercises/{cid[:2]}.yaml" in limits["allowed_paths"]) is (
        "-C-" not in tid
    )
    assert "growth/models.py" in limits["forbidden_paths"]


def candidate(value="one", base="base"):
    binding = {"task": value}
    return {"binding": binding, "binding_hash": c.recovery.fingerprint(binding), "base": base}


def test_lease_checkpoint_survives_restart_and_reuses_original_identity(tmp_path):
    path = tmp_path / "state.sqlite3"
    store = c.Store(path)
    token = store.reserve(os.getpid())
    original = store.prepare(token, candidate())
    store.release(token, original["binding_hash"], "awaiting_contract_review")
    resumed = c.Store(path)
    token = resumed.reserve(os.getpid())
    assert resumed.prepare(token, candidate(base="unrelated-new-main")) == original
    assert resumed.status()["checkpoints"][0]["phase"] == "awaiting_contract_review"
    resumed.release(token, original["binding_hash"], "awaiting_target_review")
    assert resumed.status()["checkpoint_is_not_acceptance"] is True


def test_other_process_cannot_take_live_lease(tmp_path):
    path = tmp_path / "state.sqlite3"
    store = c.Store(path)
    token = store.reserve(os.getpid())
    command = (
        "from docs.plans.m6k.continuation import Store; import os,sys; "
        "Store(sys.argv[1]).reserve(os.getpid())"
    )
    process = subprocess.run(
        [sys.executable, "-c", command, str(path)], cwd=ROOT, capture_output=True, text=True
    )
    assert process.returncode != 0 and "Workspace already leased" in process.stderr
    assert store.status()["lease"]["token"] == token


def test_abandoned_lease_requires_token_and_dead_local_owner(tmp_path, monkeypatch):
    store = c.Store(tmp_path / "state.sqlite3")
    token = store.reserve(os.getpid())
    with pytest.raises(ValueError, match="already leased"):
        store.reserve(os.getpid(), token)
    with store.connect() as db:
        db.execute("UPDATE lease SET pid=?", (99999999,))
    monkeypatch.setattr(c, "owner_alive", lambda pid: pid == os.getpid())
    with pytest.raises(ValueError, match="already leased"):
        store.reserve(os.getpid())
    with store.connect() as db:
        db.execute("UPDATE lease SET host='different-host'")
    with pytest.raises(ValueError, match="already leased"):
        store.reserve(os.getpid(), token)
    with store.connect() as db:
        db.execute("UPDATE lease SET host=?", (socket.gethostname(),))
    assert store.reserve(os.getpid(), token) != token


def test_wrong_token_second_action_corruption_and_fake_completion_fail_closed(tmp_path):
    store = c.Store(tmp_path / "state.sqlite3")
    token = store.reserve(os.getpid())
    with pytest.raises(ValueError, match="token"):
        store.prepare("wrong", candidate())
    first = store.prepare(token, candidate())
    with pytest.raises(ValueError, match="one action"):
        store.prepare(token, candidate("two"))
    with pytest.raises(ValueError, match="completion"):
        store.release(token, first["binding_hash"], "complete")
    with pytest.raises(ValueError, match="match"):
        store.release(token, candidate("two")["binding_hash"])
    corrupt = candidate()
    corrupt["binding"] = {"task": "altered"}
    with pytest.raises(ValueError, match="binding hash"):
        store.prepare(token, corrupt)
    with store.connect() as db:
        db.execute("UPDATE checkpoint SET packet=?", (json.dumps(corrupt),))
    with pytest.raises(ValueError, match="Corrupt"):
        store.stored_packet(first["binding_hash"])
    assert store.status()["lease"]["binding"] == first["binding_hash"]


def test_linked_worktrees_share_the_same_lease_database(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    c.git(repo, "init", "-q")
    c.git(
        repo,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "--allow-empty",
        "-m",
        "fixture",
    )
    linked = tmp_path / "linked"
    c.git(repo, "worktree", "add", "-b", "test", str(linked))
    assert c.state_path(repo) == c.state_path(linked)


@pytest.fixture
def verification(tmp_path, monkeypatch):
    prepared = {
        "task_id": "M6K-B-1001",
        "competency_ids": ["10.01"],
        "binding": {"dependencies": {"M6K-A-1001": "proof"}},
        "neighbors": {"10.02": c.recovery.fingerprint({"material": "original"})},
        "invariants": {
            "protected_files": {"immutable": "same"},
            "protocols": {
                "10.01": {
                    "protocol_id": "id",
                    "action_ids": ["one"],
                    "completion_sha256": "same",
                    "evidence_sha256": "same",
                    "runtime_disposition": "same",
                }
            },
        },
        "batch": {
            "sources": {"baseline_commit": "base"},
            "scope": {
                "allowed_paths": ["docs/authoring/exercises/10.yaml"],
                "forbidden_paths": ["growth/models.py"],
            },
        },
    }
    state = {"proofs": {"M6K-A-1001": "proof", "M6K-B-1001": "new-proof"}}
    current = copy.deepcopy(prepared["invariants"])
    exercises = {"10.02": {"material": "original"}}
    for path, doc in [
        ("docs/plans/m6k/program-receipts.json", {"records": []}),
        ("docs/authoring/quality/ledger.json", {"receipts": []}),
    ]:
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(doc))
    paths = ["docs/authoring/exercises/10.yaml"]

    def git(_root, *args):
        if args[0] == "show":
            return (tmp_path / args[1].split(":", 1)[1]).read_text()
        return "\n".join(paths) if args[0] == "diff" else ""

    monkeypatch.setattr(c, "git", git)
    monkeypatch.setattr(c, "context", lambda root: state)
    monkeypatch.setattr(c.reviews, "preserve_history", lambda *args: None)
    monkeypatch.setattr(c.reviews, "corpus", lambda root: ({}, exercises))
    monkeypatch.setattr(c.recovery, "invariant_snapshot", lambda *a, **kw: current)
    return tmp_path, prepared, state, current, exercises, paths


@pytest.mark.parametrize(
    "defect,match",
    [
        ("none", ""),
        ("missing", "completion evidence"),
        ("prerequisite", "Prerequisite"),
        ("neighbor", "Neighboring"),
        ("evidence", "Immutable"),
        ("protected", "Protected"),
        ("scope", "Out-of-scope"),
    ],
)
def test_post_action_verification_enforces_progress_and_boundaries(verification, defect, match):
    root, prepared, state, current, exercises, paths = verification
    if defect == "missing":
        state["proofs"].pop("M6K-B-1001")
    elif defect == "prerequisite":
        state["proofs"]["M6K-A-1001"] = "stale"
    elif defect == "neighbor":
        exercises["10.02"]["material"] = "altered"
    elif defect == "evidence":
        current["protocols"]["10.01"]["evidence_sha256"] = "altered"
    elif defect == "protected":
        current["protected_files"]["immutable"] = "altered"
    elif defect == "scope":
        paths.append("growth/models.py")
    if defect == "none":
        assert c.verify_changes(root, prepared) == {
            "verified": True,
            "task_id": "M6K-B-1001",
            "completion": False,
        }
    else:
        with pytest.raises(ValueError, match=match):
            c.verify_changes(root, prepared)
