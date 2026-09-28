# Competency product integration — local evidence

Owner request: implement the report and per-competency feedback throughout the product. Baseline: `4bb8a17`; branch: `codex/catalog-quality-audit-20260927`. This is the product integration of the completed five-pass editorial remediation, not another source editorial sweep.

## Delivered scope

All 383 competencies have authenticated learner guides: 275 compiled companion bundles, 107 existing structured lessons and compact 13.16. The remaining 270 generic typed practices now project their individually authored actions, for 378 tailored typed practices and five frozen legacy companions. There are 1,151 actions, 498 prompt/check groups and 549 resource pages. Teaching, fictional materials, later outcomes and corrective answers use explicit server selections and exports. Markdown is escaped safely; wide tables scroll by keyboard on mobile.

The [383-row catalog](../authoring/catalog-product-integration-20260928/catalog.csv) and [detailed register](../authoring/catalog-product-integration-20260928/register.json) bind each competency’s original feedback, editorial repair, domain/context, source hashes, runtime implementation and learner route. The [integration report](../authoring/catalog-product-integration-20260928/README.md) explains compilation, compatibility and verification boundaries.

## Preserved behavior

All stable competency/protocol/action IDs, action counts, completion rules, canonical mapping, activation and scoring mathematics are unchanged. Five frozen legacy package files are byte-identical; four retained typed evidence rules and their original privacy exclusions are exact. Non-retained primary observation criteria follow the existing prospective compiler rules; historical events remain immutable and active/paused practice replacement is rejected.

Canonical content SHA-256: `ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`.
Legacy runtime projection SHA-256: `9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.

Recovery reports `preserved_with_prospective_content`. Historical source documents, audit/remediation reports, quality ledger and recovery checkpoint are unchanged. The new quality snapshot fingerprints published materials and rendering, including legacy sidecars, without promoting any human acceptance state.

## Local verification

Exact commands, raw receipts, artifact/input hashes and superseded failures are in [verification.json](../authoring/catalog-product-integration-20260928/verification.json).

- Source suite: 1,234 passed.
- Full non-browser regression run: 1,901 passed; one old assertion against the historical 108-practice report failed. It was replaced with checks of both immutable historical and current reports, unchanged human review states, and material/renderer fingerprint changes. The complete review component then passed 52 tests; all 30 affected continuation tests passed. This is a full run plus targeted repair verification, not an uninterrupted green full-suite claim.
- Browser: 10 distinct desktop/mobile guide cases passed; the two companion cases were extended and rerun with wide-table keyboard scrolling. Four retained screenshots were visually inspected. Guide navigation/security recheck: six passed, one database test deselected; the full suite covers all 383 authenticated routes and no evidence/credit writes.
- Similarity audit: five parity tests passed; the exact LCS bound preserves the original alignment decisions and report ordering.
- Deterministic compiler, all-competency source/runtime parity, review history, recovery, governance and scoring reports passed.
- Ruff, Django system checks and no-migration check passed. Pilot, curriculum expansion and competency-evidence readiness passed against isolated synthetic data.
- Compose: the complete fresh smoke run passed with exit code 0, covering bootstrap, HTTP login, migration/seed idempotency, replay/readiness, persistence, backup/restore hash equality and clean shutdown. Its synthetic container and volume were removed afterward. Earlier health-grace failure and interrupted diagnostics are retained; they are not passing evidence.

## Remaining evidence boundaries

This batch provides source, software, browser and synthetic container evidence. It does not certify independent human authorship, learner-only cold-start acceptance, actual learner outcomes or qualified specialist acceptance. Formal quality passes remain zero; existing research and specialist gaps remain open. No hosted CI, merge, release, deployment or live participant data write is claimed.
