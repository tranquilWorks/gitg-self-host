"""Verify audit identity/coverage and reproduce bounded factual findings.

A successful run means the audit evidence is internally consistent. It is not a
semantic, professional, independent reviewer or participant acceptance gate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean, median

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stable(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def main():
    audit = json.loads((HERE / "audit.json").read_text())
    rows = audit["rows"]
    fingerprints = json.loads((HERE / "source-fingerprints.json").read_text())
    for path, expected in fingerprints.items():
        assert sha((ROOT / path).read_bytes()) == expected, f"Stale source: {path}"
    canonical = yaml.safe_load((ROOT / audit["governing_sources"][0]).read_text())["curriculum"]
    expected = {c["id"]: c for d in canonical["domains"] for c in d["competencies"]}
    assert len(rows) == len(expected) == 383
    assert len({r["competency_id"] for r in rows}) == 383
    assert {r["competency_id"] for r in rows} == set(expected)
    notes = json.loads((HERE / "editorial-notes.json").read_text())
    assert set(notes) == set(expected)
    assert len({n["distinctive_design"] for n in notes.values()}) == 383
    documents = {}
    for r in rows:
        cid = r["competency_id"]
        assert r["canonical_record_sha256"] == sha(stable(expected[cid])), cid
        assert r["canonical_scope"] == expected[cid]["scope"]
        path = ROOT / r["source_path"]
        assert r["source_file_sha256"] == sha(path.read_bytes()), cid
        ep = r["exercise_path"]
        if ep not in documents:
            documents[ep] = yaml.safe_load((ROOT / ep).read_text())["exercises"]
        exercise = documents[ep][cid]
        assert r["source_record_sha256"] == sha(stable(exercise)), cid
        primary = (
            path.read_text()
            if r["source_kind"] == "companion"
            else yaml.safe_dump(exercise, sort_keys=False, allow_unicode=True, width=110)
        )
        assert r["primary_content_sha256"] == sha(primary.encode()), cid
        excerpt = r["context_evidence"]["excerpt"].removesuffix(" […]")
        assert excerpt in " ".join(primary.split()) or excerpt == exercise["goal"], (
            f"Stale context: {cid}"
        )
        assert r["professional_quality"] == "not_demonstrated_by_current_revision_acceptance"
        assert r["formal_receipts"] == []
        assert (
            r["independent_cold_start"]
            == r["actual_learner_review"]
            == r["qualified_review"]
            == "not_performed"
        )
        assert r["editorial_note"] == notes.get(cid)
        assert r["review_depth"] == "full_primary"
        assert r["companion_materials_read"] == (r["source_kind"] == "companion")
        assert r["finding_category"] == notes[cid]["finding_category"]
        assert not r["instructional_structure"]["missing_structured_check_ids"], cid
        for f in r["confirmed_maintainer_metadata"]:
            assert (ROOT / f["path"]).read_text().splitlines()[f["line"] - 1] == f["quote"], cid
        page = (HERE / "domains" / f"{r['domain_id']}.md").read_text()
        assert page.count(f"## {cid} — ") == 1, cid
    csv_rows = list(csv.DictReader((HERE / "catalog.csv").open()))
    assert [r["competency_id"] for r in csv_rows] == [r["competency_id"] for r in rows]
    ledger = json.loads((ROOT / "docs/authoring/quality/ledger.json").read_text())
    assert ledger["receipts"] == [], (
        "Acceptance state changed; re-audit rather than carrying forward zeros."
    )
    assert audit["summary"]["review_depth"] == dict(Counter(r["review_depth"] for r in rows))
    assert audit["summary"]["detailed_editorial_notes"] == len(notes)
    assert audit["summary"]["companion_bundles_read"] == 275
    assert audit["summary"]["editorial_categories"] == dict(
        Counter(r["finding_category"] for r in rows)
    )
    assert audit["summary"]["confirmed_metadata_competencies"] == sum(
        bool(r["confirmed_maintainer_metadata"]) for r in rows
    )
    assert audit["summary"]["competencies_with_open_findings"] == sum(
        bool(r["findings"]) for r in rows
    )
    assert audit["summary"]["fingerprinted_files"] == len(fingerprints)
    assert audit["summary"]["compared_primary_pairs"] == 383 * 382 // 2

    # 10.03: parse the actual supplied pairs, not a duplicated answer literal.
    ex = documents["docs/authoring/exercises/10.yaml"]
    sections = {s["id"]: s for s in ex["10.03"]["instructional_content"]["sections"]}
    packet = sections["board-packet"]["body"]
    pairs = re.findall(r"\bN(\d+)/N(\d+)\b", packet)
    assert "Twelve same-size notices" in packet and len(pairs) == 5
    overlapping = {int(n) for pair in pairs for n in pair}
    nonoverlap = sorted(set(range(1, 13)) - overlapping)
    assert len(overlapping) == 8 and nonoverlap == [4, 7, 11, 12]
    assert "Seven notices do not overlap" in packet, "Finding repaired; revise the audit."
    # 10.01: independently recompute the delayed key, including deltas.
    a, b = [2, 5, 11], [2, 5, 17]

    def stats(values):
        return [mean(values), median(values), max(values) - min(values)]

    first, second = stats(a), stats(b)
    changes = [y - x for x, y in zip(first, second, strict=True)]
    assert first == [6, 5, 9] and second == [8, 5, 15] and changes == [2, 0, 6]
    # 10.09: establish prior exposure in the same learner bundle.
    action = ex["10.09"]["actions"][2]["instructions"]
    adaptation = ex["10.09"]["adaptation"]
    transfer = next(
        s["body"]
        for s in ex["10.09"]["instructional_content"]["sections"]
        if s["id"] == "four-bit-extension"
    )
    assert "represent 9" in action and "verify 1001" in action
    assert "1111 is 15" in adaptation
    assert all(value in transfer for value in ["1001", "1010", "1111"])
    # 10.11: the selected two lenses and five-field remainder disagree.
    breadth = ex["10.11"]["instructional_content"]
    synthesis = next(s for s in breadth["sections"] if s["id"] == "two-lens-synthesis")
    synthesis_key = next(k for k in breadth["checks"] if k["id"] == "two-lens-key")
    assert synthesis["title"] == "Connect display technology and social access"
    assert (
        "History, economics, humanities, arts and society remain only mapped"
        in synthesis_key["body"]
    )
    # Original craft correction: all three briefs and matching checks agree on facts.
    craft = documents["docs/authoring/exercises/21.yaml"]["21.03"]["instructional_content"]
    secs = {s["id"]: s for s in craft["sections"]}
    keys = {k["id"]: k for k in craft["checks"]}
    for stem in ["seed-swap", "repair-cafe", "sketch-walk"]:
        assert secs[stem + "-brief"]["body"].strip() in keys[stem + "-key"]["body"]
        assert secs[stem + "-attempt"]["check_id"] == stem + "-key"
    assert "seeds@events.example" in keys["retest-key"]["body"]
    assert (
        "16 May 2027" in keys["defect-key"]["body"] and "17 May 2027" in keys["defect-key"]["body"]
    )
    assert 150 * 12 - 25 * 70 - 150 == -100  # 24.11 fresh numerical key.
    evidence = {
        "verification_kind": "static_identity_and_synthetic_arithmetic",
        "competencies": len(rows),
        "source_files_hash_verified": len(fingerprints),
        "review_depth": audit["summary"]["review_depth"],
        "10.03": {
            "pairs": pairs,
            "distinct_overlapping_notices": sorted(overlapping),
            "nonoverlapping_notices": nonoverlap,
            "supplied_nonoverlap_count": 7,
            "correct_nonoverlap_count": len(nonoverlap),
            "finding_reproduced": True,
        },
        "10.01": {"first_statistics": first, "second_statistics": second, "deltas": changes},
        "10.09": {"prior_answers_reappear_in_transfer": ["1001 = 9", "1111 = 15"]},
        "10.11": {
            "selected_lenses": ["technology", "social access"],
            "key_lists_society_as_uninvestigated": True,
            "key_omits_science_from_uninvestigated_list": True,
            "limit": (
                "Literal contradiction in the stated two-lens partition; no expert redesign claim."
            ),
        },
        "21.03": {
            "three_matching_briefs_keys": True,
            "changed_contact_and_wrong_date_checks_present": True,
        },
        "24.11": {"fresh_check_balance": -100},
        "quality_or_acceptance_pass": False,
    }
    (HERE / "verification.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
