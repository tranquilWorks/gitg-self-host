# M6K evidence, humility, and forecasting — source checkpoint

Date: 12 September 2026. Repository: `tranquilWorks/gitg-self-host`.
Baseline: main `d93532696d3ea9d04e50f47350b90fa255208511` (PR #77).
Intended branch: `codex/m6k-evidence-humility-forecasting-source-2026-09-12`.

## Delivered source

Exactly 09.04 Source and evidence evaluation, 09.05 Epistemic humility, and 09.06 Probabilistic and scenario thinking. Eleven instructional Markdown files contain **8,592 whitespace-delimited words**: three distinct learner guides, three two-check prompt files, three separate corrective keys, one later-evidence packet, and one forecast-outcome packet. Scope map, bounded sources, fixtures, tests, and integration handoff accompany them.

09.04 supplies complete sample/response counts, exhaustive missing-answer bounds, source-dependence tracing, and a contrast with independently collected stronger evidence. 09.05 preserves versions, context, assumptions and revision conditions; its fresh checks distinguish relevant corrections from unsupported pressure. 09.06 preserves forecasts before separately presented outcomes, uses fixed cancellation/missing-data rules, computes sensitivity and expected values, and checks calibration separately from Brier accuracy.

The previous 09.01–09.03 source group remains in separate draft PR #78. This publication does not integrate or merge it. **Runtime remains 108 tailored / 275 pending / 383 protocols / 1,151 actions.** Neither source cohort is promoted to runtime or formal human acceptance.

## Verification actually executed

`python -m unittest discover -s tests -p test_m6k_evidence_humility_forecasting_sources.py -v`: **44 passed**.

`python -m unittest discover -s tests -p '*sources.py' -v`, with the preceding uploaded source bundle present: **85 passed**, comprising 44 new tests and 41 retained previous-cohort tests. The new branch does not duplicate those preceding source files; the combined run is recorded in the downloadable evidence bundle.

Checks include exhaustive missing binary-response assignments, denominator and dataset identity distinctions, preserved context and version records, probability validation, resolved/void/unresolved handling, exact Brier and expected-value arithmetic, boundary cases, calibration groups, and visible table/prompt/fixture alignment. These are source and synthetic-case checks, not production score tests or learner evaluation.

An initial test asserted a past-tense paraphrase rather than the actual survey question. It was corrected to assert the exact supplied question while retaining all measurement/replication boundary checks. Review also removed an incorrect count phrase from the humility key. Final results above follow those corrections.

## Standalone reader

A generated HTML reader was checked in system Chromium through Playwright `set_content` at desktop 1280 x 900 and mobile 390 x 844. Both views contain three guides, six fresh checks, nine answer reveals and two later-packet reveals. All eleven controlled disclosures begin closed, keep content hidden, and open/close by keyboard. Navigation works; no page-wide horizontal overflow appears with disclosures closed or opened; no external network requests occur. Desktop and mobile screenshots were inspected.

This verifies the generated standalone reader only. It does not exercise the Django application, production assets, canonical import, or live deployment. The HTML, reproducible preview/browser scripts, screenshots, JSON result, source tests, and logs are in the conversation artifact, not the production asset pipeline.

## Exact local source identifiers

Source folder Git tree: `957a17dd87487b94a2d1261123d12269762d1f4e`.
Test Git blob: `a1fd6746b75fe494f65b947d729256d0ce421bef`.
Active-batch Git blob: `f310fd669376c21aa2e04c62d2a7e2e946b62415`.

The source inventory records individual UTF-8 byte sizes, Git blob identifiers and SHA-256 digests. These identify the tested candidate. Remote publication parity is to be checked against these exact objects and reported in the PR; publication alone is not a test result.

## Unverified and blocking

GitHub and package-index DNS resolution fails in this workspace. No full checkout or Django installation is available. Authenticated connector reads and writes do work. Full repository contract, Ruff, canonical compiler, runtime projection, readiness, historical replay, production browser, Compose, and hosted CI verification are **not claimed**.

`MANIFEST.tsv` is intentionally not fabricated from an incomplete checkout. Its new-file entries and changed active-batch byte size must be regenerated and verified before merge. This is an open merge prerequisite, not a waived gate. The source-only draft is not merge-ready.

No canonical curriculum, practice package, activation ledger, scoring implementation, completion rule, model, migration, or deployment file is in the authored change set. Formal scope, instructional, cold-start, application integration, actual learner, qualified-where-needed, and owner reviews remain separate pending evidence. A research link or synthetic test cannot close them.

## Next engineering action

Obtain a complete checkout, verify main and the exact source branch, synchronize the manifest, and run the source/contract gates. Finish the earlier and current source cohorts through the existing authoring compiler, preserving original package hashes and historical replay. Generate current/recovery projections and reports, then exercise actual guide/reveal, readiness and recovery paths. Retain all human evidence boundaries. Do not begin calling the two groups six additional runtime-complete competencies until those operations are verified.
