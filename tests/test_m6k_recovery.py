import copy
import json
import shutil
from pathlib import Path

import pytest

from docs.plans.m6k import recovery

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "docs/plans/m6k/recovery"


def test_recovered_corpus_and_protected_runtime_are_exact(monkeypatch):
    def no_git_history(*args, **kwargs):
        raise AssertionError("Verification must also work in shallow CI checkouts.")

    monkeypatch.setattr(recovery, "git_bytes", no_git_history)
    assert recovery.verify(ROOT, CHECKPOINT) == {
        "recovered_sources": 383,
        "protocols": 383,
        "actions": 1151,
        "quality_passes": 0,
        "protected_baseline": "preserved_with_prospective_content",
    }


def test_tampered_archive_fails_before_any_content_is_used():
    raw = (CHECKPOINT / "GITG_M6J_Unpublished_Inputs.zip").read_bytes()
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        recovery.verified_archive(raw[:-1] + bytes([raw[-1] ^ 1]))


def test_source_edit_cannot_reuse_the_recovered_fingerprint(tmp_path):
    clone = tmp_path / "checkpoint"
    shutil.copytree(CHECKPOINT, clone)
    path = clone / "selected/exercises/10.yaml"
    path.write_bytes(path.read_bytes() + b"\n# changed\n")
    with pytest.raises(ValueError, match="Selected source bytes changed"):
        recovery.verify(ROOT, clone)


def test_initial_ledger_cannot_be_reclassified_as_acceptance(tmp_path, monkeypatch):
    clone = tmp_path / "checkpoint"
    shutil.copytree(CHECKPOINT, clone)
    path = clone / "initial-quality-ledger.json"
    ledger = json.loads(path.read_text())
    ledger["rows"]["10.01"]["instructional"] = "pass"
    path.write_text(json.dumps(ledger))
    baseline = json.loads((CHECKPOINT / "runtime-invariants.json").read_text())
    monkeypatch.setattr(recovery, "invariant_snapshot", lambda root, **kwargs: baseline)
    with pytest.raises(ValueError, match="383 independent pending"):
        recovery.verify(ROOT, clone)


def test_protected_rule_change_cannot_rebaseline_itself(monkeypatch):
    baseline = json.loads((CHECKPOINT / "runtime-invariants.json").read_text())
    changed = copy.deepcopy(baseline)
    changed["protocols"]["10.02"]["evidence_sha256"] = "0" * 64
    monkeypatch.setattr(recovery, "invariant_snapshot", lambda root, **kwargs: changed)
    with pytest.raises(ValueError, match="Protected runtime"):
        recovery.verify(ROOT, CHECKPOINT)
    with pytest.raises(ValueError, match="never silently rebaseline"):
        recovery.initialize(ROOT, CHECKPOINT / "GITG_M6J_Unpublished_Inputs.zip", CHECKPOINT)
