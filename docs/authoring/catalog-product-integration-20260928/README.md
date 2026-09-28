# Competency product integration — 28 September 2026

All **383 competencies now have learner guides in the application**. The 275 repaired companion bundles are compiled from their own source documents, alongside the 107 existing structured lessons and the adequate compact 13.16 lesson. The remaining **270 generic typed practices now use their individually authored actions**. Five frozen legacy practices receive companion guides while retaining their exact original behavior.

The [per-competency catalog](catalog.csv) and [detailed register](register.json) connect every original finding and editorial disposition to its source, distinct context, implemented practice, learner route, materials, checks and fingerprints. This integration follows the completed five-pass [editorial remediation](../catalog-remediation-20260927/README.md); it is not a sixth editorial sweep or a new claim of independent authorship.

## What learners receive

- Tailored instructions, observation checks, adaptations and review examples in each practice's existing recommendation/setup/action journey.
- The matching lesson through **Open learning guide, materials and practice checks** on recommendation, setup and sprint pages.
- Readable tables (including keyboard-scrollable wide tables on mobile), lists, code/text materials and public references; source-file links resolve to authenticated application pages.
- Practice prompts and corrective answers selected separately on the server. Later fictional outcomes and supplementary materials open only when explicitly requested. Default and attempt exports exclude unrevealed answer bodies.
- Existing compact and structured lessons retain their own content and reveal structure. No common fictional case or generic teaching template replaces the individually authored materials.

The unscored guide does not complete actions, submit evidence or award credit. Reading a fictional outcome is not performing the real action.

## Compatibility and provenance

All 383 stable protocol IDs, 1,151 action IDs, completion rules, canonical mappings, activation and scoring mathematics remain unchanged. The four retained typed evidence contracts and all five legacy packages remain exact. The retained typed practices also preserve their original privacy exclusions; regression testing caught and repaired a lost legal-privilege exclusion before completion. The existing authoring compiler updates other primary observation criteria prospectively to match the authored checks; prior events retain their frozen rule snapshots. Imports continue to reject replacement of instructions or rules used by an active or paused practice.

The immutable recovery checkpoint still verifies as `preserved_with_prospective_content`. The [runtime originals](runtime-baselines/) and explicit projection declaration preserve the original bytes. Historical source-stage receipts, cohort counts and source documents remain unchanged. Tests of those historical receipts use an explicitly enumerated [input snapshot](historical-inputs.json); current source-to-runtime and application tests enforce the new projection separately.

The [current quality snapshot](quality-status.json) fingerprints the published learner materials, including legacy companions and the Markdown renderer. Changing those inputs invalidates earlier review evidence. The historical quality report remains unchanged; no human review state is promoted by this integration. Its `runtime_rewrites_pending: 5` counter denotes the five intentionally frozen, non-selected legacy practices, each of which now has a companion guide. There are no missing learner guides.

The guide compiler uses an explicit competency-to-source contract. It changes navigation and heading levels, preserves authored teaching/prompts/answers, and excludes author-only scope maps. Links to author-only scope maps become plain reminders of the guide’s scope and limits. Plain-text materials remain preformatted. Markdown rendering disables raw HTML and images, following the parser's [documented security configuration](https://markdown-it-py.readthedocs.io/en/latest/security.html); links are checked before compilation.

The full-catalog similarity audit now rejects impossible candidates using an exact [longest-common-subsequence bound](https://rapidfuzz.github.io/RapidFuzz/Usage/distance/LCSseq.html) before running its existing Python alignment. Every ordered matching block is a common subsequence, so the bound cannot exclude a pair that meets the existing threshold. The original similarity decision, order, rounding and queue limit remain unchanged; parity tests cover empty, Unicode, asymmetric, repetitive, random and threshold-boundary cases. This removes the verification bottleneck revealed when generic copy was replaced by distinct authored practices.

The container’s startup health grace is 180 seconds: full-catalog validation, seeding and score-state rebuild run before Gunicorn starts. The former 20-second grace could mark a progressing fresh install unhealthy under load. The actual HTTP health probe and post-start retry policy remain unchanged.

## Verification and remaining evidence

Completed local checks and exact commands are recorded in [verification](verification.json), with raw receipts and explicit superseded failures. Retained browser artifacts show the [mobile guide](browser/catalog-privacy-guide-390.png), [desktop guide](browser/catalog-privacy-guide-1280.png), and wide tables on [mobile](browser/catalog-wide-table-390.png) and [desktop](browser/catalog-wide-table-1280.png). These are source, software, browser and synthetic deployment checks, not participant evidence. The per-competency report is reproducible with:

```sh
.venv/bin/python scripts/verify_catalog_product_integration.py --check
.venv/bin/python scripts/author_full_competency_frontier.py --check
.venv/bin/python docs/plans/m6k/recovery.py
```

The non-browser regression run finished with **1,901 passes and one obsolete historical-report assertion**. That assertion was repaired while retaining the original report; all **52 review-component tests and 30 affected continuation tests** then passed. The source suite passed **1,234 tests**. Browser verification passed **10 distinct desktop/mobile cases**, with two cases subsequently extended and rerun for wide-table keyboard scrolling. The receipts preserve this sequence rather than describing the full run as uninterrupted green.

The complete fresh Docker Compose smoke run passed bootstrap, authenticated HTTP, migration/seed idempotency, replay/readiness, volume persistence, backup/restore hash equality and clean shutdown. Its isolated container and volume were removed afterward.

No separate learner-only cold-start review, qualified specialist acceptance, actual longitudinal/physical/relational performance or owner acceptance is invented. The existing formal quality ledger and research gaps remain open. Local implementation and verification do not imply hosted CI, merge, release or deployment.
