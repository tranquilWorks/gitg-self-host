# Catalog editorial remediation — 27–28 September 2026

The five-pass editorial follow-up covers all **383 competencies**. **310 entries received repairs; 73 required no source change.** Each disposition preserves the original finding, the competency's distinct context and mechanism, concrete repair anchors, and current source fingerprints in the [catalog](catalog.csv) and [detailed register](register.json).

This closes the identified **source-level editorial follow-ups**. It does not certify independent authorship, grant formal A/B/C acceptance, or substitute for actual learner, specialist or owner review. Those requirements remain visible per competency. “No edit required” means no new defect was found in the reviewed source, not universal validation.

## What changed

- Added individually authored teaching, complete fictional materials, practice and separate changed-case checks to 90 earlier lessons. There are now 107 structured instructional lessons within the existing 108 implemented set; 13.16 retains its adequate compact design.
- Corrected facts, missing inputs, promise/authority distinctions, contradictory answer keys and reveal order. Examples include the 10.03 overlap count, 10.06 assistance/accuracy distinction, 10.11 disciplinary accounting, complete household/shelf/picnic materials, and the 24.03 unfunded-cash case.
- Added new checks where unseen application was needed; labeled repeated worked questions as consolidation. Narrated outcomes remain fictional case analysis, not learner performance.
- Added bounded progression for regulation across contexts, community participation, cultural media and instruction-led higher-intensity activity. Broader physical proficiency and cultural/clinical judgments remain unclaimed.
- Removed internal governance, schema and scoring-system commentary from 195 learner guides, preserving useful privacy, consent, access, role-choice and safety guidance. [Relocated metadata](relocated-metadata.json) preserves author-facing information.
- Synchronized 101 changed canonical runtime packages within the existing 108 implemented lessons. The 275 companions remain source-only; their underlying runtime packages are byte-for-byte unchanged. No new activation occurred.

## Five passes, no sixth sweep

| Pass | Scope |
| --- | --- |
| 1 | Facts, complete materials and answer separation |
| 2 | Canonical scope, capability fit and progression |
| 3 | Professional learner copy and bounded primary-source verification |
| 4 | Adversarial nonblinded desk review and plausible wrong answers |
| 5 | Regression repairs, source tests, reveal projections, protected invariants and delivery evidence |

[Pass status](passes.json), [desk-review examples](DESK-REVIEW.md) and [source checks](SOURCE-CHECKS.md) distinguish the evidence produced from the evidence still missing. The five new bounded source checks supplement, rather than replace, the historical audit's 25 checks. One inaccessible sewing PDF was replaced with a readable university-extension source; it was not represented as inspected.

## Verification

- **1,234 source tests passed**; **3 compiler/source tests passed**, with 16 application/database tests deliberately deselected under the standing source-work scope.
- **223 prompt/check projections** validated across 107 structured lessons; unrevealed whole keys are absent from their default and attempt payloads. This is a source-level projection check, not browser verification or a claim that no phrase resembles prior teaching.
- **2,892 local links** resolve; **1,353 primary/bundle files** are fingerprinted. All 73 no-edit records are checked against the baseline.
- All **383 protocols / 1,151 actions**, evidence rules, canonical definitions/mappings, activation and formal quality ledger are preserved. Recovery reports `preserved_with_prospective_content`; immutable originals remain pinned.
- **73,153 primary-text pairs** screened; no exact normalized duplicates. The [screen](similarity.json) and per-entry mechanisms support inspection of distinctness, not proof of independent creation.
- Deterministic compiler, regenerated coverage/risk/originality/governance reports, repository scope, Ruff and manifest checks are recorded in [verification](verification.json).

The historical [audit](../catalog-quality-audit-20260927/README.md) remains unchanged at baseline commit `5bf1f629d7419ed320042eca0f3547a5f11508b6`. Its old-current-tree fingerprints are intentionally superseded, not silently rebaselined. Cohort verification files retain their historical commands and explicitly identify their new prospective hash pins.

## Remaining evidence boundaries

Formal learner-only cold-start review has not occurred in a separate context. Live physical, relational, clinical and longitudinal performance was not performed. Source reading and synthetic case analysis do not supply specialist acceptance. The formal ledger and research gaps remain open; nothing here declares clinical effectiveness, psychometric validity, universal accessibility, cultural representativeness or mastery.

Application/browser/Compose/CI/CD, participant exposure, release and deployment remain outside this source-focused delivery. The work is local and reviewable; publication is not implied.

Reproduce the source checks from the repository root:

```sh
.venv/bin/python -m unittest discover -s tests -p '*sources.py'
.venv/bin/python -m pytest tests/test_tailored_practice_authoring.py -m 'not django_db' -q
.venv/bin/python scripts/author_full_competency_frontier.py --check
.venv/bin/python docs/plans/m6k/recovery.py
.venv/bin/python docs/authoring/catalog-remediation-20260927/verify.py
.venv/bin/python scripts/catalog_governance_audit.py --check
.venv/bin/python scripts/verify-manifest.py
```
