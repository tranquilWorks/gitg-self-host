"""Build the documentary audit from preserved editorial notes and exact sources.

Generation does not perform semantic review and never grants a review pass.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = "8377d21e348eda14dd5e66153637293aeaca1a5b"
CANONICAL = "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
LEDGER = "docs/authoring/quality/ledger.json"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def stable(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def quote_text(text):
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def read_json(path):
    return json.loads(path.read_text())


def snapshot(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}


def main():
    notes = read_json(HERE / "editorial-notes.json")
    contexts = read_json(HERE / "context-excerpts.json")
    similarity = read_json(HERE / "similarity.json")
    canon = yaml.safe_load((ROOT / CANONICAL).read_text())["curriculum"]
    companions = {}
    for p in (ROOT / "docs/authoring").glob("*/*/learner-guide.md"):
        if re.fullmatch(r"\d{2}\.\d{2}", p.parent.name):
            assert p.parent.name not in companions
            companions[p.parent.name] = p
    exercises = {}
    source_lines = {}
    for p in sorted((ROOT / "docs/authoring/exercises").glob("*.yaml")):
        data = yaml.safe_load(p.read_text())
        if not isinstance(data, dict) or "exercises" not in data:
            continue
        exercises.update({c: (p, x) for c, x in data["exercises"].items()})
        for i, line in enumerate(p.read_text().splitlines(), 1):
            m = re.fullmatch(r"  '(\d{2}\.\d{2})':", line)
            if m:
                source_lines[m[1]] = i
    rows = []
    all_files = {}
    provenance = {}
    for domain in canon["domains"]:
        for c in domain["competencies"]:
            cid = c["id"]
            ep, exercise = exercises[cid]
            p = companions.get(cid, ep)
            kind = "companion" if cid in companions else "implemented_exercise"
            relative = str(p.relative_to(ROOT))
            primary = (
                p.read_text()
                if kind == "companion"
                else yaml.safe_dump(exercise, sort_keys=False, allow_unicode=True, width=110)
            )
            files = {ep, p}
            if kind == "companion":
                files.update(q for q in p.parent.rglob("*") if q.is_file())
                files.update(
                    q
                    for q in p.parent.parent.glob("*")
                    if q.is_file()
                    and q.name
                    in {
                        "SOURCES.md",
                        "QUALITY-REVIEW.md",
                        "cohort.json",
                        "README.md",
                        "fixtures.json",
                    }
                )
            else:
                quality = ROOT / "docs/authoring/quality" / cid
                if quality.is_dir():
                    files.update(q for q in quality.rglob("*") if q.is_file())
            artifacts = [snapshot(q) for q in sorted(files)]
            for item in artifacts:
                all_files[item["path"]] = item["sha256"]
            if relative not in provenance:
                provenance[relative] = subprocess.run(
                    ["git", "log", "-1", "--format=%H", BASELINE, "--", relative],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=True,
                ).stdout.strip()
            metadata = []
            if kind == "companion":
                for line, text in enumerate(primary.splitlines(), 1):
                    if (
                        "professional_boundary" in text
                        or "Formal M6K" in text
                        or "**Compatibility boundary:**" in text
                    ):
                        metadata.append({"path": relative, "line": line, "quote": text})
            note = notes.get(cid)
            assert note, f"Missing completed editorial review: {cid}"
            depth = "full_primary"
            findings = []
            if metadata:
                findings.append("F-METADATA")
            if note and note["disposition"] == "revision_required":
                findings.append("E-" + cid)
            checks = exercise.get("instructional_content", {}).get("checks", [])
            sections = exercise.get("instructional_content", {}).get("sections", [])
            missing_check_refs = [
                s["check_id"]
                for s in sections
                if s.get("check_id") and s["check_id"] not in {k["id"] for k in checks}
            ]
            prompt_paths = [q for q in artifacts if q["path"].endswith("check-prompts.md")]
            answer_paths = [q for q in artifacts if q["path"].endswith("check-answers.md")]
            row = {
                "competency_id": cid,
                "name": c["name"],
                "domain_id": domain["id"],
                "domain_name": domain["name"],
                "canonical_scope": c["scope"],
                "canonical_progress": c["evidence_of_progress"],
                "canonical_record_sha256": digest(stable(c)),
                "source_kind": kind,
                "source_path": relative,
                "source_line": 1 if kind == "companion" else source_lines[cid],
                "source_pointer": None if kind == "companion" else f'exercises["{cid}"]',
                "source_file_sha256": digest(p.read_bytes()),
                "source_record_sha256": digest(stable(exercise)),
                "exercise_path": str(ep.relative_to(ROOT)),
                "primary_content_sha256": digest(primary.encode()),
                "last_file_commit_at_baseline": provenance[relative],
                "provenance_limit": (
                    "File history shows publication, not independent creation "
                    "or per-entry authorship."
                ),
                "context_evidence": contexts[cid],
                "domain_fit_status": (
                    "canonical_scope_and_selected_task_or_case_compared; "
                    "full_facet_acceptance_not_established"
                ),
                "distinctness_status": (
                    "no_exact_normalized_primary_body_duplicate; "
                    "semantic_independence_not_certified"
                ),
                "nearest_text_records": similarity["nearest"][cid],
                "review_depth": depth,
                "editorial_note": note,
                "finding_category": note["finding_category"],
                "companion_materials_read": note["bundle_review"],
                "confirmed_maintainer_metadata": metadata,
                "findings": findings,
                "instructional_structure": {
                    "separate_prompt_files": [x["path"] for x in prompt_paths],
                    "separate_answer_files": [x["path"] for x in answer_paths],
                    "structured_prompt_count": sum(s.get("kind") == "prompt" for s in sections),
                    "structured_check_count": len(checks),
                    "missing_structured_check_ids": missing_check_refs,
                    "limit": (
                        "Presence and references only; not a verdict that prompts are fresh "
                        "or keys discriminate correctly."
                    ),
                },
                "artifacts": artifacts,
                "professional_quality": "not_demonstrated_by_current_revision_acceptance",
                "formal_receipts": [],
                "independent_cold_start": "not_performed",
                "actual_learner_review": "not_performed",
                "qualified_review": "not_performed",
                "owner_acceptance": "not_recorded_in_ledger",
                "disposition": "revision_findings_open"
                if findings
                else "acceptance_not_established",
                "next_action": (
                    note["required_action"]
                    if note
                    else (
                        "Move the quoted engineering/review status into editorial records; then "
                        if metadata
                        else ""
                    )
                    + "complete the full learner bundle and facet review for this scope, "
                    "including keys and later materials; obtain a separate learner-only C "
                    "review before acceptance."
                ),
            }
            rows.append(row)
    assert len(rows) == 383 and len({r["competency_id"] for r in rows}) == 383
    assert set(contexts) == {r["competency_id"] for r in rows}
    ledger = read_json(ROOT / LEDGER)
    assert ledger["receipts"] == [], "Reassess acceptance evidence before regenerating."
    governance = [
        CANONICAL,
        LEDGER,
        "docs/plans/m6k/program.json",
        "docs/plans/m6k/AUDIT.md",
        "docs/plans/m6k/README.md",
        "docs/plans/m6k/REVIEW_RECORD.md",
        "docs/plans/m6k/REVIEW_IMPLEMENTATION.md",
        "docs/authoring/sources.yaml",
        "data/practices/release_manifest.yaml",
    ]
    for cid in ["1003", "1009"]:
        governance.extend(
            str(p.relative_to(ROOT))
            for p in (ROOT / "data/practices/protocols/10").glob(f"PRACTICE-COMP-{cid}-*.yaml")
        )
    governance.append("data/practices/protocols/10/PRACTICE-DELIBERATE-PRACTICE-01.yaml")
    for s in governance:
        all_files[s] = digest((ROOT / s).read_bytes())
    counts = dict(Counter(r["review_depth"] for r in rows))
    summary = {
        "total": 383,
        "companions": len(companions),
        "implemented_primary": 383 - len(companions),
        "review_depth": counts,
        "detailed_editorial_notes": len(notes),
        "companion_bundles_read": sum(r["companion_materials_read"] for r in rows),
        "editorial_categories": dict(Counter(r["finding_category"] for r in rows)),
        "confirmed_metadata_competencies": sum(
            bool(r["confirmed_maintainer_metadata"]) for r in rows
        ),
        "competencies_with_open_findings": sum(bool(r["findings"]) for r in rows),
        "formal_receipts": 0,
        "professional_quality_certified": 0,
        "implemented_without_structured_instructional_content": sum(
            r["source_kind"] == "implemented_exercise"
            and not r["instructional_structure"]["structured_prompt_count"]
            for r in rows
        ),
        "companions_with_separate_prompt_and_answer_files": sum(
            r["source_kind"] == "companion"
            and bool(r["instructional_structure"]["separate_prompt_files"])
            and bool(r["instructional_structure"]["separate_answer_files"])
            for r in rows
        ),
        "exact_normalized_body_duplicate_groups": len(
            similarity["exact_normalized_body_duplicates"]
        ),
        "fingerprinted_files": len(all_files),
        "compared_primary_pairs": similarity["pair_count"],
        "limit": (
            "All 383 primary texts editorially reviewed and all 275 competency-folder "
            "companion bundles read. This is not formal A/B/C, independent authorship "
            "certification, complete facet acceptance or qualified/participant acceptance."
        ),
    }
    audit = {
        "schema_version": "GG-CATALOG-QUALITY-AUDIT-1.0",
        "baseline_commit": BASELINE,
        "audit_date_utc": "2026-09-27",
        "summary": summary,
        "governing_sources": governance,
        "rows": rows,
    }
    (HERE / "audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
    (HERE / "source-fingerprints.json").write_text(
        json.dumps(all_files, indent=2, sort_keys=True) + "\n"
    )
    with (HERE / "catalog.csv").open("w", newline="") as f:
        columns = [
            "competency_id",
            "name",
            "domain_name",
            "source_path",
            "source_line",
            "source_file_sha256",
            "source_record_sha256",
            "review_depth",
            "finding_category",
            "companion_materials_read",
            "disposition",
            "professional_quality",
            "findings",
            "next_action",
        ]
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in rows:
            w.writerow({k: ";".join(r[k]) if k == "findings" else r[k] for k in columns})
    for domain in canon["domains"]:
        selected = [r for r in rows if r["domain_id"] == domain["id"]]
        out = [
            f"# {domain['id']} — {domain['name']}",
            "",
            "Every entry is pinned to the audit baseline. "
            "Every primary text received individual editorial review; companion-folder "
            "prompts, keys, later packets and supplied materials were also read. "
            "No entry below is a formal A/B/C, independent, learner, qualified or owner pass. "
            "Textual distinctness cannot prove independent authorship.",
            "",
        ]
        for r in selected:
            cid = r["competency_id"]
            n = r["editorial_note"]
            source = f"../../../..//{r['source_path']}#L{r['source_line']}".replace("//", "/")
            out += [
                f"## {cid} — {r['name']}",
                "",
                f"**Source:** [{r['source_path']}]({source}). **Depth:** `{r['review_depth']}`. "
                f"**Disposition:** `{r['disposition']}`.",
                "",
                f"**Editorial category:** `{r['finding_category']}`. "
                "Categories describe the review note, not a severity grade or acceptance decision.",
                "",
                "**Canonical task:** " + r["canonical_scope"],
                "",
                "**Context evidence (selected source excerpt, not a complete packet):**",
                "",
                "> " + quote_text(r["context_evidence"]["excerpt"]),
                "",
            ]
            if n:
                out += [
                    "**Specific design:** " + n["distinctive_design"],
                    "",
                    "**Editorial assessment:** " + n["substantive_finding"],
                    "",
                    "**Criteria:** " + ", ".join(n["criteria"]) + ". " + n["review_method"],
                    "",
                ]
            else:
                out += [
                    "**Assessment boundary:** The canonical scope and selected task/case "
                    "were inspected; the full lesson, facet map, later branches and answer "
                    "quality remain unaccepted. The excerpt documents a context, "
                    "not evidence that every requested skill is taught or assessed.",
                    "",
                ]
            if r["confirmed_maintainer_metadata"]:
                first = r["confirmed_maintainer_metadata"][0]
                out += [
                    f"**B4 finding F-METADATA:** learner guide line {first['line']} "
                    "exposes editorial/schema status:",
                    "",
                    "> " + quote_text(first["quote"]),
                    "",
                ]
            near = r["nearest_text_records"][0]
            out += [
                f"**Comparison lead:** {near['other']} has filtered five-gram Jaccard "
                f"{near['filtered_fivegram_jaccard']:.5f}. "
                "This is a text-screening lead, not an originality grade.",
                "",
                "**Required next step:** " + r["next_action"],
                "",
                "**Acceptance:** Not demonstrated; no current formal receipt exists. "
                "See audit.json for record/file hashes and all related artifact fingerprints.",
                "",
            ]
        (HERE / "domains" / f"{domain['id']}.md").write_text("\n".join(out))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
