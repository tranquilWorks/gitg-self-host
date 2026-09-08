"""Synthetic receipts test enforcement only; none are production quality acceptances."""

import copy
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from jsonschema import ValidationError

from docs.plans.m6k import reviews

ROOT = Path(__file__).resolve().parents[1]
CID = "10.01"


@pytest.fixture
def case(tmp_path):
    for rel in (
        "docs/plans/m6k",
        "growth/domain/instructional_content.py",
        "growth/views_instructional.py",
        "growth/urls.py",
        "growth/static/growth/app.css",
        "templates/growth/practice_guide.html",
        "templates/growth/partials/instructional_link.html",
        "data/practices/schema/instructional_content_v1.schema.json",
        "data/practices/protocols/10",
        "docs/authoring/exercises/10.yaml",
    ):
        source, dest = ROOT / rel, tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copyfile(source, dest)
    canonical = {"id": CID, "name": "Synthetic learning review", "scope": "Learning and transfer"}
    exercise = reviews.load_document(tmp_path / "docs/authoring/exercises/10.yaml")["exercises"][
        CID
    ]
    folder = tmp_path / reviews.QUALITY / CID
    folder.mkdir(parents=True)
    artifact = folder / "synthetic-evidence.txt"
    artifact.write_text(
        "Synthetic desk observation: the delayed prompt is separated from its key.\n"
    )
    anchor = reviews.make_anchor(tmp_path, str(artifact.relative_to(tmp_path)))
    plan = {
        "competency_id": CID,
        "canonical_sha256": reviews.fingerprint(canonical),
        "starting_ability": "Can add and read a short dataset.",
        "prerequisites": "Paper or notes.",
        "default_scope": "bounded",
        "promised_material_ids": ["worked-even", "worked-skew"],
        "facets": [
            {
                "id": "learning",
                "relationship": "required",
                "disposition": "exercised",
                "reason": "Retrieval and correction are directly exercised.",
                **{k: [anchor] for k in ("teaching", "practice", "evidence", "next_route")},
            },
            {
                "id": "transfer",
                "relationship": "required",
                "disposition": "pathway",
                "reason": "Broader settings require subsequent practice.",
                **{k: [anchor] for k in ("teaching", "practice", "evidence", "next_route")},
            },
        ],
    }
    (folder / "scope-plan.json").write_text(json.dumps(plan))
    current = reviews.snapshot(tmp_path, CID, canonical, exercise)
    return tmp_path, canonical, exercise, current, anchor


def receipt(case, dimension="scope", rid="A-1"):
    _root, _canonical, _exercise, current, anchor = case
    return {
        "schema_version": "GG-M6K-RECEIPT-1.0",
        "id": rid,
        "competency_id": CID,
        "dimension": dimension,
        "state": "pass",
        "actor": {"kind": "agent", "reference": "synthetic-fixture", "run": "author-run"},
        "previous": None,
        "start_revision": copy.deepcopy(current),
        "finish_revision": copy.deepcopy(current),
        "dependencies": [],
        "inputs": [anchor],
        "outputs": [anchor],
        "criteria": [
            {
                "id": key,
                "verdict": "pass",
                "reason": "Synthetic fixture records the separated delayed attempt artifact.",
                "anchors": [anchor],
            }
            for key in sorted(reviews.required_criteria(dimension))
        ],
        "findings": [],
        "evidence": [
            {
                "kind": "simulated",
                "execution": "executed",
                "claim": "simulated",
                "command_or_method": "Synthetic pytest fixture",
                "environment": "Temporary repository",
                "result": "Desk example only",
                "limit": "Not a participant or editorial acceptance",
                "anchors": [anchor],
            }
        ],
        "decision_reference": None,
        "cold_start": None,
    }


def validate(case, row, accepted=None, records=None):
    root, canonical, exercise, current, _ = case
    reviews.validate_schema(row, "receipt")
    reviews.validate_receipt(
        root, row, current, accepted or set(), records or {}, canonical, exercise
    )


def b_receipt(case):
    row = receipt(case, "instructional", "B-1")
    row["dependencies"] = ["A-1"]
    return row


def test_complete_synthetic_scope_and_instruction_receipts(case):
    a = receipt(case)
    validate(case, a)
    validate(case, b_receipt(case), {"A-1"}, {"A-1": a})


@pytest.mark.parametrize(
    "defect",
    [
        "missing_criterion",
        "blanket",
        "missing_outputs",
        "no_evidence",
        "blocked_finding",
        "missing_closure",
        "simulated_as_live",
        "duplicate_criterion",
        "blank_reason",
        "future_revision",
    ],
)
def test_invalid_passes_fail_closed(case, defect):
    row = receipt(case)
    if defect == "missing_criterion":
        row["criteria"].pop()
    elif defect == "blanket":
        row["criteria"] = [{**row["criteria"][0], "id": "ALL"}]
    elif defect == "missing_outputs":
        row["outputs"] = []
    elif defect == "no_evidence":
        row["evidence"] = []
    elif defect in ("blocked_finding", "missing_closure"):
        row["findings"] = [
            {
                "id": "F1",
                "facet": "transfer",
                "severity": "major",
                "blocking": True,
                "repair": "Supply missing prompt",
                "closed": defect == "missing_closure",
                "closure": [],
            }
        ]
    elif defect == "simulated_as_live":
        row["evidence"][0]["claim"] = "actual_learner"
    elif defect == "duplicate_criterion":
        row["criteria"].append(copy.deepcopy(row["criteria"][0]))
    elif defect == "blank_reason":
        row["criteria"][0]["reason"] = " "
    else:
        row["finish_revision"]["scope"] = "f" * 64
    with pytest.raises((reviews.ReviewError, ValidationError)):
        validate(case, row)


@pytest.mark.parametrize("defect", ["missing", "stale", "wrong_stage", "foreign"])
def test_dependency_cannot_be_omitted_substituted_or_stale(case, defect):
    row, a = b_receipt(case), receipt(case)
    accepted = {"A-1"}
    if defect == "missing":
        row["dependencies"] = []
    elif defect == "stale":
        accepted = set()
    elif defect == "wrong_stage":
        a["dimension"] = "integration"
    else:
        a["competency_id"] = "10.02"
    with pytest.raises(reviews.ReviewError):
        validate(case, row, accepted, {"A-1": a})


def test_instruction_change_reopens_b_but_not_unchanged_scope(case):
    root, canonical, exercise, _, anchor = case
    a, b = receipt(case), b_receipt(case)
    changed = copy.deepcopy(exercise)
    changed["actions"][0]["instructions"] += " Keep the first response."
    current = reviews.snapshot(root, CID, canonical, changed)
    new_case = root, canonical, changed, current, anchor
    validate(new_case, a)
    with pytest.raises(reviews.ReviewError, match="Stale"):
        validate(new_case, b, {"A-1"}, {"A-1": a})


def test_same_domain_neighbor_and_yaml_reformat_do_not_stale_entry(case):
    root, canonical, _exercise, before, _ = case
    path = root / "docs/authoring/exercises/10.yaml"
    data = reviews.load_document(path)
    data["exercises"]["10.02"]["title"] = "A neighboring entry was changed"
    path.write_text(yaml.safe_dump(data, sort_keys=True))
    after = reviews.snapshot(root, CID, canonical, reviews.load_document(path)["exercises"][CID])
    assert after == before
    anchor = reviews.make_anchor(root, str(path.relative_to(root)), "/exercises/10.01")
    data["exercises"]["10.02"]["title"] += " again"
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    reviews.verify_anchor(root, anchor)


@pytest.mark.parametrize("component", ["scope", "key", "renderer", "runtime"])
def test_changes_bind_only_affected_review_dimensions(case, component):
    root, canonical, exercise, before, _ = case
    if component == "scope":
        exercise["scope_note"] += " New scope."
    elif component == "key":
        exercise["instructional_content"]["checks"][0]["body"] += " New key."
    elif component == "renderer":
        path = root / "templates/growth/practice_guide.html"
        path.write_text(path.read_text() + "\nChanged rendering\n")
    else:
        path = next((root / "data/practices/protocols/10").glob("*1001*"))
        path.write_text(path.read_text().replace("schema_version:", "changed_schema_version:", 1))
    after = reviews.snapshot(root, CID, canonical, exercise)
    expected = {"scope": "scope", "key": "materials", "renderer": "renderer", "runtime": "evidence"}
    assert before[expected[component]] != after[expected[component]]
    if component != "scope":
        assert before["scope"] == after["scope"]


@pytest.mark.parametrize(
    "defect",
    ["missing_brief", "missing_example", "leaked_field", "leaked_body", "metadata", "duplicate_id"],
)
def test_qa01_qa02_qa05_negative_fixtures(case, defect):
    root, canonical, exercise, _current, anchor = case
    guide = exercise["instructional_content"]
    prompt = next(s for s in guide["sections"] if s["kind"] == "prompt")
    if defect == "missing_brief":
        prompt["references"] = ["absent-brief"]
    elif defect == "missing_example":
        guide["sections"] = [s for s in guide["sections"] if s["id"] != "worked-even"]
    elif defect == "leaked_field":
        prompt["answer"] = "Answer must not be inline"
    elif defect == "leaked_body":
        key = next(k for k in guide["checks"] if k["id"] == prompt["check_id"])
        prompt["body"] += key["body"]
    elif defect == "metadata":
        exercise["scope_note"] = "Keep retained_typed stable_id: unchanged"
    else:
        guide["sections"].append(copy.deepcopy(guide["sections"][0]))
    new_case = root, canonical, exercise, reviews.snapshot(root, CID, canonical, exercise), anchor
    if defect == "missing_example":
        row, a = b_receipt(new_case), receipt(new_case)
        with pytest.raises(reviews.ReviewError, match="Missing promised"):
            validate(new_case, row, {"A-1"}, {"A-1": a})
    else:
        assert reviews.mechanical_errors(exercise, CID)


def test_one_facet_default_cannot_claim_all_canonical_facets(case):
    root, canonical, exercise, _current, anchor = case
    path = root / reviews.QUALITY / CID / "scope-plan.json"
    plan = json.loads(path.read_text())
    plan["default_scope"] = "full"
    path.write_text(json.dumps(plan))
    fresh = root, canonical, exercise, reviews.snapshot(root, CID, canonical, exercise), anchor
    with pytest.raises(reviews.ReviewError, match="full scope"):
        validate(fresh, receipt(fresh))


@pytest.mark.parametrize("dimension", ["learner", "qualified", "owner"])
def test_agent_cannot_clear_human_dimensions(case, dimension):
    row = receipt(case, dimension)
    i = receipt(case, "integration", "I-1")
    row["dependencies"] = ["I-1"]
    with pytest.raises(reviews.ReviewError, match="actual minimized"):
        validate(case, row, {"I-1"}, {"I-1": i})
    row["actor"]["kind"] = "human"
    row["decision_reference"] = "authorized-private-record:test-only"
    with pytest.raises(reviews.ReviewError, match="cannot become a human"):
        validate(case, row, {"I-1"}, {"I-1": i})


def cold_receipt(case):
    root, _, exercise, _, anchor = case
    row = receipt(case, "cold_start", "C-1")
    row["actor"] = {
        "kind": "independent_agent",
        "run": "cold-run",
        "reference": "synthetic-separate-run",
    }
    row["dependencies"] = ["B-1"]
    guide = exercise["instructional_content"]
    attempt_id = next(s["id"] for s in guide["sections"] if s["kind"] == "prompt")
    bundle = {
        "projection": reviews.learner_projection(guide, CID, attempt=attempt_id),
        "attempt_id": attempt_id,
        "prerequisites": "Paper or notes.",
    }
    path = root / reviews.QUALITY / CID / "learner-only.json"
    path.write_text(json.dumps(bundle))
    bound = reviews.make_anchor(root, str(path.relative_to(root)))
    key_path = path.with_name("checking-keys.json")
    key_path.write_text(json.dumps(guide["checks"]))
    key_anchor = reviews.make_anchor(root, str(key_path.relative_to(root)))
    row["cold_start"] = {
        "bundle": bound,
        "attempt": anchor,
        "key": key_anchor,
        "scope_audit": anchor,
        "initial_inputs": [bound],
        "phases": ["learner_only", "attempt", "key_reveal", "scope_audit"],
    }
    return row


def test_separate_cold_start_run_and_learner_projection(case):
    row, b = cold_receipt(case), b_receipt(case)
    validate(case, row, {"B-1"}, {"B-1": b})
    row["actor"]["run"] = "author-run"
    with pytest.raises(reviews.ReviewError, match="own cold start"):
        validate(case, row, {"B-1"}, {"B-1": b})


def test_cold_start_rejects_hidden_rationale_even_with_fresh_bundle_hash(case):
    row, b = cold_receipt(case), b_receipt(case)
    root = case[0]
    path = root / row["cold_start"]["bundle"]["path"]
    bundle = json.loads(path.read_text())
    bundle["author_rationale"] = "Expected to pass"
    path.write_text(json.dumps(bundle))
    row["cold_start"]["bundle"]["sha256"] = reviews.anchor_hash(root, row["cold_start"]["bundle"])
    with pytest.raises(reviews.ReviewError, match="hidden rationale"):
        validate(case, row, {"B-1"}, {"B-1": b})


def write_ledger(case, rows):
    root = case[0]
    index = []
    for row in rows:
        path = reviews.QUALITY / CID / "receipts" / (row["id"] + ".json")
        (root / path).parent.mkdir(exist_ok=True)
        raw = (json.dumps(row, indent=2) + "\n").encode()
        (root / path).write_bytes(raw)
        index.append(
            {"id": row["id"], "path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}
        )
    (root / reviews.QUALITY / "ledger.json").write_text(
        json.dumps({"schema_version": "GG-M6K-LEDGER-1.0", "receipts": index})
    )
    return index


def test_append_chain_and_duplicate_receipt_ids(case):
    row = receipt(case)
    index = write_ledger(case, [row])
    _, loaded = reviews.load_ledger(case[0])
    assert loaded["A-1"] == row
    next_row = {**row, "id": "A-2", "previous": index[0]["sha256"], "state": "revise"}
    write_ledger(case, [row, next_row])
    reviews.load_ledger(case[0])
    next_row["previous"] = None
    write_ledger(case, [row, next_row])
    with pytest.raises(reviews.ReviewError, match="append-only"):
        reviews.load_ledger(case[0])
    write_ledger(case, [row, row])
    with pytest.raises(reviews.ReviewError, match="Duplicate receipt"):
        reviews.load_ledger(case[0])


def test_history_cannot_be_rehashed_to_rewrite_an_old_decision(case):
    root = case[0]
    row = receipt(case)
    write_ledger(case, [row])
    for args in (
        ["init", "-q"],
        ["add", "."],
        [
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-qm",
            "Synthetic baseline",
        ],
    ):
        subprocess.run(["git", *args], cwd=root, check=True)
    reviews.preserve_history(root, "HEAD")
    row["state"] = "revise"
    write_ledger(case, [row])
    with pytest.raises(reviews.ReviewError, match="rewritten"):
        reviews.preserve_history(root, "HEAD")


@pytest.mark.parametrize("defect", ["missing", "stale", "escape", "pointer"])
def test_unresolved_artifact_anchors_fail(case, defect):
    row = receipt(case)
    anchor = copy.deepcopy(row["outputs"][0])
    if defect == "missing":
        anchor["path"] = "not-supplied.txt"
    elif defect == "stale":
        anchor["sha256"] = "0" * 64
    elif defect == "escape":
        anchor["path"] = "../outside.txt"
    else:
        anchor["path"] = "docs/authoring/exercises/10.yaml"
        anchor["pointer"] = "/exercises/10.99"
    row["outputs"] = [anchor]
    with pytest.raises(reviews.ReviewError):
        validate(case, row)


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    path = tmp_path / "duplicated.yaml"
    path.write_text("exercises:\n  10.01: first\n  10.01: silently overwritten\n")
    with pytest.raises(reviews.ReviewError, match="Duplicate mapping key"):
        reviews.load_document(path)


def test_repository_report_is_current_and_does_not_accept_recovered_drafts():
    actual = reviews.report(ROOT)
    expected = json.loads((ROOT / reviews.QUALITY / "current-report.json").read_text())
    assert actual == expected
    assert actual["recovered_drafts"] == 383
    assert actual["tailored_runtime"] == 102 and actual["runtime_rewrites_pending"] == 281
    assert all(n == 0 for n in actual["counts"].values())
    assert actual["invalid_current_receipts"] == 0


def test_collection_is_not_executed_verification(case):
    row = receipt(case)
    row["evidence"][0]["execution"] = "collected"
    with pytest.raises(reviews.ReviewError, match="Collected or unavailable"):
        validate(case, row)
    row = receipt(case, "integration", "I-1")
    row["dependencies"] = ["C-1"]
    with pytest.raises(reviews.ReviewError, match="executed software"):
        validate(case, row, {"C-1"}, {"C-1": receipt(case, "cold_start", "C-1")})


def test_stale_material_reopens_b_c_and_integration_in_current_report(case, monkeypatch):
    root, canonical, exercise, _, _ = case
    # Use a one-entry synthetic repository for the dependency graph, not real acceptances.
    monkeypatch.setattr(reviews, "corpus", lambda _: ({CID: canonical}, {CID: exercise}))
    contract = root / "contracts/tailored-practice-authoring.yaml"
    contract.parent.mkdir()
    contract.write_text(yaml.safe_dump({"implemented_competency_ids": [CID]}))
    for path in (root / "data/practices/protocols/10").glob("*.yaml"):
        if reviews.load_document(path)["parent_competency_id"] != CID:
            path.unlink()
    a, b, c = receipt(case), b_receipt(case), cold_receipt(case)
    i = receipt(case, "integration", "I-1")
    i["dependencies"] = ["C-1"]
    i["evidence"][0].update(kind="software", claim="software")
    write_ledger(case, [a, b, c, i])
    before = reviews.report(root)
    assert all(
        before["counts"][d] == 1 for d in ("scope", "instructional", "cold_start", "integration")
    )
    exercise["instructional_content"]["checks"][0]["body"] += " Changed answer."
    after = reviews.report(root)
    assert after["counts"]["scope"] == 1
    assert all(after["counts"][d] == 0 for d in ("instructional", "cold_start", "integration"))
    assert after["invalid_current_receipts"] == 3
    exercise["instructional_content"]["checks"][0]["body"] = exercise["instructional_content"][
        "checks"
    ][0]["body"].removesuffix(" Changed answer.")
    # A later explicit revise disposition also invalidates dependent passes.
    index = write_ledger(case, [a, b, c, i])
    revise = {**a, "id": "A-2", "state": "revise", "previous": index[0]["sha256"]}
    write_ledger(case, [a, b, c, i, revise])
    after = reviews.report(root)
    assert all(
        after["counts"][d] == 0 for d in ("scope", "instructional", "cold_start", "integration")
    )


def test_na_cannot_clear_owner_or_be_simulated_human_evidence(case):
    row = receipt(case, "owner")
    row["state"] = "justified_not_applicable"
    with pytest.raises(reviews.ReviewError, match="N/A cannot excuse"):
        validate(case, row)
    row["dimension"] = "qualified"
    row["actor"]["kind"] = "human"
    row["decision_reference"] = "synthetic-fixture-only"
    with pytest.raises(reviews.ReviewError, match="real decision"):
        validate(case, row)


@pytest.mark.parametrize("index", ["-1", "01", "+1", "-"])
def test_array_pointer_rejects_noncanonical_indices(case, index):
    anchor = {
        "path": "docs/authoring/exercises/10.yaml",
        "pointer": f"/exercises/10.01/actions/{index}",
        "sha256": "0" * 64,
    }
    with pytest.raises(reviews.ReviewError, match="nonnegative canonical index"):
        reviews.anchor_value(case[0], anchor)


def test_check_requires_a_pinned_history_base(monkeypatch):
    monkeypatch.setattr("sys.argv", ["reviews.py", "check"])
    with pytest.raises(reviews.ReviewError, match="pinned --base"):
        reviews.main()
