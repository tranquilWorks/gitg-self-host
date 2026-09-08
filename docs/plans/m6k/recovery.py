#!/usr/bin/env python3
"""Recover exact M6K sources and verify the immutable, source-only checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile

import yaml

BASE = "8aaf3a27b2522e09c7796fb3ad256ce481eb7932"
SOURCE_BASE = "c3491a4ff4c0ba77c7d8f2244bae7218ae568880"
ARCHIVE_HASH = "c22e69229a8836b8e21dbf74228ac014205f3bef9e2a68b2d50dae9ddfe82597"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DIMENSIONS = (
    "scope",
    "instructional",
    "cold_start",
    "integration",
    "learner",
    "qualified",
    "owner",
)
FROZEN = {"08.02", "11.10", "16.03", "17.03", "26.01"}
RETAINED = {"08.06", "09.12", "10.02", "13.02"}
PROTECTED = (
    "data/practices/protocols",
    "data/practices/registries/activation_ledger.yaml",
    "data/curriculum",
    "data/model",
    "data/assessment",
    "growth/models.py",
    "growth/migrations",
    "growth/services/canonical_import.py",
    "growth/domain/evidence.py",
    "growth/domain/typed_evidence.py",
    "growth/domain/scoring.py",
    "growth/domain/composite_scoring.py",
    "growth/services/score_state.py",
    "growth/services/composite_score_state.py",
    "tests/fixtures",
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fingerprint(value: object) -> str:
    return digest(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    )


def git_bytes(root: Path, revision: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=root)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def verified_archive(raw: bytes) -> dict[str, bytes]:
    if digest(raw) != ARCHIVE_HASH:
        raise ValueError("Unpublished source archive SHA-256 mismatch.")
    with ZipFile(io.BytesIO(raw)) as archive:
        manifest = json.loads(archive.read("INPUT_MANIFEST.json"))
        files = {}
        for group, prefix in (("files", "overlay/"), ("supporting_files", "supporting/")):
            for item in manifest[group]:
                name = prefix + item["path"]
                content = archive.read(name)
                if len(content) != item["bytes"] or digest(content) != item["sha256"]:
                    raise ValueError(f"Archive member checksum mismatch: {name}")
                files[name] = content
        expected = set(files) | {"INPUT_MANIFEST.json", "README.md"}
        if set(archive.namelist()) != expected or len(archive.namelist()) != len(expected):
            raise ValueError("Archive contains unexpected or duplicate members.")
        files["INPUT_MANIFEST.json"] = archive.read("INPUT_MANIFEST.json")
        return files


def curriculum(root: Path) -> dict[str, dict]:
    path = root / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
    return {
        row["id"]: row
        for domain in yaml.safe_load(path.read_text())["curriculum"]["domains"]
        for row in domain["competencies"]
    }


def selected_sources(root: Path, files: dict[str, bytes]) -> tuple[dict, dict]:
    canonical = curriculum(root)
    selected, origins = {}, {}
    for domain in sorted({cid[:2] for cid in canonical}):
        path = f"docs/authoring/exercises/{domain}.yaml"
        archived = "overlay/" + path
        raw = files[archived] if archived in files else git_bytes(root, SOURCE_BASE, path)
        existing = root / path
        if existing.exists() and existing.read_bytes() != raw:
            raise ValueError(f"Reconcile newer main source explicitly before recovery: {path}")
        document = yaml.safe_load(raw)
        expected = {cid for cid in canonical if cid.startswith(domain + ".")}
        if document["domain_id"] != domain or set(document["exercises"]) != expected:
            raise ValueError(f"Missing or foreign canonical source ID: {path}")
        selected[path] = raw
        origins[path] = {
            "origin": "unpublished_archive" if archived in files else SOURCE_BASE,
            "sha256": digest(raw),
            "bytes": len(raw),
            "main_disposition": "identical" if existing.exists() else "absent_recovered",
        }
    return selected, origins


def invariant_snapshot(root: Path, *, protected_paths: list[str] | None = None) -> dict:
    # Always enumerate the pinned historical tree, never new fixtures added by this work.
    paths = protected_paths
    if paths is None:
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", BASE, "--", *PROTECTED], cwd=root, text=True
        ).splitlines()
    protected = {path: digest((root / path).read_bytes()) for path in paths}
    rows = {}
    actions = []
    for path in sorted((root / "data/practices/protocols").rglob("*.yaml")):
        package = yaml.safe_load(path.read_text())
        cid = package["parent_competency_id"]
        if cid in rows:
            raise ValueError(f"Duplicate protocol competency: {cid}")
        ids = [action["stable_id"] for action in package["intervention"]["actions"]]
        actions.extend(ids)
        rows[cid] = {
            "protocol_id": package["stable_id"],
            "action_ids": ids,
            "sha256": digest(path.read_bytes()),
            "completion_sha256": fingerprint(package["completion_and_review"]),
            "evidence_sha256": fingerprint(
                {
                    "evidence": package["evidence_and_scoring"],
                    "rules": [a["evidence_rules"] for a in package["intervention"]["actions"]],
                }
            ),
            "runtime_disposition": "frozen_companion"
            if cid in FROZEN
            else "retained_typed"
            if cid in RETAINED
            else "typed",
        }
    if set(rows) != set(curriculum(root)) or len(actions) != 1151 or len(set(actions)) != 1151:
        raise ValueError("Canonical 383 protocol / 1151 action inventory mismatch.")
    return {"base_commit": BASE, "protected_files": protected, "protocols": rows}


def initialize(root: Path, archive_path: Path, checkpoint: Path) -> None:
    if checkpoint.exists():
        raise ValueError("Checkpoint already exists; never silently rebaseline reviewed sources.")
    files = verified_archive(archive_path.read_bytes())
    selected, origins = selected_sources(root, files)
    snapshot = invariant_snapshot(root)
    for path, sha in snapshot["protected_files"].items():
        if digest(git_bytes(root, BASE, path)) != sha:
            raise ValueError(f"Protected input differs from baseline: {path}")
    checkpoint.mkdir(parents=True)
    shutil.copyfile(archive_path, checkpoint / "GITG_M6J_Unpublished_Inputs.zip")
    (checkpoint / "INPUT_MANIFEST.json").write_bytes(files["INPUT_MANIFEST.json"])
    index = {}
    canonical = curriculum(root)
    for path, raw in selected.items():
        target = checkpoint / "selected" / path.removeprefix("docs/authoring/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        for cid, entry in yaml.safe_load(raw)["exercises"].items():
            index[cid] = {
                "name": canonical[cid]["name"],
                "canonical_sha256": fingerprint(canonical[cid]),
                "source_sha256": fingerprint(entry),
                "source_path": str(target.relative_to(root)),
                **origins[path],
            }
    sources = files["overlay/docs/authoring/sources.yaml"]
    (checkpoint / "selected/sources.yaml").write_bytes(sources)
    current_sources = yaml.safe_load((root / "docs/authoring/sources.yaml").read_text())["sources"]
    recovered_sources = yaml.safe_load(sources)["sources"]
    # The archived ledger is cumulative; keep exact changed entries for review.
    key = "source_id"
    current = {row[key]: row for row in current_sources}
    recovered = {row[key]: row for row in recovered_sources}
    if set(current) - set(recovered):
        raise ValueError("Recovered source ledger drops a current source.")
    changed = {
        sid: {
            "main": row,
            "recovered": recovered[sid],
            "disposition": "Preserve both; cumulative source note is not new claim verification.",
        }
        for sid, row in current.items()
        if row != recovered[sid]
    }
    write_json(
        checkpoint / "reconciliation.json",
        {
            "source_base": SOURCE_BASE,
            "runtime_base": BASE,
            "origins": origins,
            "current_source_count": len(current),
            "recovered_source_count": len(recovered),
            "changed_source_notes": changed,
            "unresolved_source_conflicts": [],
            "missing_integration": (
                "Later completion compiler overlay was not archived; reconstruct separately."
            ),
        },
    )
    write_json(checkpoint / "source-inventory.json", index)
    write_json(checkpoint / "runtime-invariants.json", snapshot)
    write_json(
        checkpoint / "initial-quality-ledger.json",
        {
            "claim": "Immutable initial pending states, not quality acceptance.",
            "authored_runtime_count": 91,
            "runtime_rewrite_pending": 292,
            "recovered_source_count": len(index),
            "rows": {cid: dict.fromkeys(DIMENSIONS, "pending") for cid in sorted(index)},
            "open_findings": {
                "QA-01": "21.03",
                "QA-02": "10.01",
                "QA-03": "12.05",
                "QA-04": "12.08",
                "QA-05": "10.02",
            },
        },
    )


def verify(root: Path, checkpoint: Path) -> dict:
    files = verified_archive((checkpoint / "GITG_M6J_Unpublished_Inputs.zip").read_bytes())
    if (checkpoint / "INPUT_MANIFEST.json").read_bytes() != files["INPUT_MANIFEST.json"]:
        raise ValueError("Archived input manifest copy changed.")
    origins = json.loads((checkpoint / "reconciliation.json").read_text())["origins"]
    index = json.loads((checkpoint / "source-inventory.json").read_text())
    canonical = curriculum(root)
    actual = {}
    for path, origin in origins.items():
        selected = checkpoint / "selected" / path.removeprefix("docs/authoring/")
        raw = selected.read_bytes()
        expected = files.get("overlay/" + path)
        # Eight Git-sourced files were verified at initialization. Their pinned
        # byte hashes permit verification from a shallow CI checkout or source ZIP.
        if (expected is not None and raw != expected) or digest(raw) != origin["sha256"]:
            raise ValueError(f"Selected source bytes changed: {path}")
        for cid, entry in yaml.safe_load(raw)["exercises"].items():
            if cid in actual or cid not in canonical:
                raise ValueError(f"Duplicate or foreign selected source: {cid}")
            actual[cid] = fingerprint(entry)
            if index[cid]["source_sha256"] != actual[cid]:
                raise ValueError(f"Selected source fingerprint mismatch: {cid}")
            if index[cid]["canonical_sha256"] != fingerprint(canonical[cid]):
                raise ValueError(f"Canonical fingerprint mismatch: {cid}")
    if set(actual) != set(canonical) or set(index) != set(canonical):
        raise ValueError("Missing selected source or inventory row.")
    if (checkpoint / "selected/sources.yaml").read_bytes() != files[
        "overlay/docs/authoring/sources.yaml"
    ]:
        raise ValueError("Recovered source ledger bytes changed.")
    baseline = json.loads((checkpoint / "runtime-invariants.json").read_text())
    if invariant_snapshot(root, protected_paths=list(baseline["protected_files"])) != baseline:
        raise ValueError("Protected runtime, identity, completion or evidence baseline changed.")
    ledger = json.loads((checkpoint / "initial-quality-ledger.json").read_text())
    pending = {cid: dict.fromkeys(DIMENSIONS, "pending") for cid in canonical}
    if ledger["rows"] != pending:
        raise ValueError("Initial review ledger must retain all 383 independent pending states.")
    if (
        ledger["authored_runtime_count"] != 91
        or ledger["runtime_rewrite_pending"] != 292
        or ledger["recovered_source_count"] != 383
        or ledger["open_findings"]
        != {
            "QA-01": "21.03",
            "QA-02": "10.01",
            "QA-03": "12.05",
            "QA-04": "12.08",
            "QA-05": "10.02",
        }
    ):
        raise ValueError("Initial counts and open audit findings must retain the pinned baseline.")
    return {
        "recovered_sources": len(actual),
        "protocols": 383,
        "actions": 1151,
        "quality_passes": 0,
        "protected_baseline": "unchanged",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize", type=Path, metavar="ARCHIVE")
    args = parser.parse_args()
    checkpoint = HERE / "recovery"
    if args.initialize:
        initialize(ROOT, args.initialize, checkpoint)
    print(json.dumps(verify(ROOT, checkpoint), indent=2))


if __name__ == "__main__":
    main()
