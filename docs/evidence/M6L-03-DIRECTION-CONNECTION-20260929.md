# M6L-03 — Direction-to-practice connection

Baseline: `80faeac57c183ce9038d3479a60f0ec0a6a59e97` (M6L-02 draft).
Branch: `codex/m6l-03-direction-connection`.
[Draft PR #107](https://github.com/tranquilWorks/gitg-self-host/pull/107), stacked
on #106. Owner request: “lets do batch 3”. Implementation and verification only;
no merge, publication or live-data operation is claimed.

## Delivered behavior

- The owner explicitly selects a saved priority, authors an intended outcome,
  leaves the connection unknown, or declines. Changed choices append immutable
  assessment/practice revisions with source Personal OS provenance and hashes.
- Setup and weekly planning show the current connection and allow revision.
  Changing Personal OS does not silently retarget an old priority; earlier
  choices remain readable and past weekly plans/reviews remain unchanged.
- A concise review edits mission, anti-goals, priorities and twelve-month
  direction, preserving principles, audit responses and previous revisions.
  Stale forms, ownership, assessment period and saved snapshots are checked.
- Additive migration 0014, owner archive v4, deletion counts/order, backup table
  fingerprints and operations verification include the new records. See the
  [contract and rollback boundary](../practice-direction-contract.md).

The connection is the **current intention for a practice in an assessment
period**, not an immutable link attached to each sprint or weekly plan. The UI
states this distinction. Cross-period history and explicit reuse remain Batch 5.
No intention or reflection changes recommendations, evidence or scoring.

## Verification

- **All 1,939 nonbrowser cases have passing coverage:** 322 in the initial full
  profile run, 1,569 in the first continuation, and 48 in the final continuation.
  The XML union was compared with all 1,939 collected node IDs: zero uncovered
  cases. These are aggregate receipts across the repairs below, not a claim that
  the initial full-profile command exited successfully.
- Initial focused checks: **79 passed**, including the 52 catalog-quality tests.
  After the final model isolation, **29 connection/lifecycle/backup/migration
  integration tests passed**. Both historical migration repairs also passed
  focused checks; the new migration’s retained-data assertions passed separately.
- **Five distinct local browser journeys passed:** new desktop/mobile direction
  journeys, weekly planning, account data, and the existing practice lifecycle.
  The two new journeys passed again after final model registration changed.
- Eight new screenshots cover setup, weekly planning, connection history and
  direction history at 1280px and 390px. Representative local and hosted images
  were inspected; the journeys assert no horizontal overflow and exercise
  keyboard history expansion. This is not a formal assistive-technology audit.
- New migration: isolated 0013→0014→0013→0014, checking retained fixture data and
  the additive table. Populated SQLite backup preserves an intention and its
  hash; the manifest contains counts/hashes and no intention text.
- **All 17 required readiness commands passed** in the separate serial run:
  catalog governance, composite catalog/scoring, applicability, assessment
  calibration/collection/analysis, pilot, curriculum, competency evidence,
  context, Personal OS, context priority, M6C, M6D, weekly and owner operations.
  The readiness runner exited 0, and its command inventory matches the full
  profile’s 17 commands.
- Ruff, Django system checks, migration drift, contract schema and scope passed
  during implementation and were repeated successfully at closeout.

Receipts on the working machine:
`/tmp/m6l03-full.xml`, `/tmp/m6l03-continuation.xml`, `/tmp/m6l03-final.xml`,
`/tmp/m6l03-coverage.json`, `/tmp/m6l03-model-focused.xml`,
`/tmp/m6l03-browser.xml`, `/tmp/m6l03-model-browser.xml`, and
`/tmp/m6l03-readiness.log`. Screenshots: `test-results/pilot-walkthrough/direction-*.png`.

## Failures found and repaired

1. Two historical migration tests included the new table in digests of state
   predating that table. Their existing newer-table exclusion lists now include
   `growth_practicedirectionrevision`; all historical-row comparisons remain.
   The new table has its own forward/rollback/reapply and populated-backup tests.
2. Recovery pins **all bytes of `growth/models.py`**, so appending the new class
   tripped its guard. The original module was restored exactly. The new class
   lives in `growth/models_direction.py`, registered during Django’s model-loading
   phase through `GrowthConfig.import_models`. The schema did not change. The
   recovery guard and final integration/browser rechecks pass. No recovery
   fingerprint, canonical report or quality gate was weakened or rebaselined.
3. New test fixtures initially omitted required assessment provenance, inherited
   test settings in an isolated migration subprocess, and used a colon-sensitive
   browser label locator. Those test defects were repaired. An interrupted
   longer browser process was replaced with a completed, logged affected-journey
   run; it is not counted as a pass.

The canonical content hash remains
`ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a` and the legacy
projection remains `9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.
All 383 practices and 1,151 actions remain unchanged. Historical models, guide
routes/styles, scoring and canonical source/report files are byte-preserved.

## Hosted status and claim boundary

The first implementation head `d1f669a` passed the complete hosted browser suite
and Docker Compose migration/persistence/backup/restore drill in
[run 36580437479](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36580437479).
Its quality job predates the migration-test corrections and model isolation;
those early successes are **not** final-head aggregate verification. The final
head requires its own Pilot readiness gate before any merge. PR #107 remains a
draft, and no image is published by this batch.

Software and synthetic-browser evidence only. No new participant observations,
specialist acceptance or empirical validation is claimed. Batches 04–08 remain
planned.

Final-head update, 29 September 2026: `10b040f3976f06e4e7fa53fe07b928ef4b60931a` passed all hosted quality, browser, Compose and aggregate Pilot readiness checks in [run 36583693381](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36583693381). PR #107 remains draft and unmerged; publication was skipped.
