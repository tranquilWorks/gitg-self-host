# M6L-02 — Explicit context and alternatives

Owner requested the next batch after M6L-01. This branch is stacked on
`1274ff1969178bd863c5ab1e2d21c436a9ea2ef5` (draft PR #105), whose full local
verification passed: 1,918 tests and all readiness commands; hosted run
[36515667838](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36515667838)
passed the aggregate Pilot readiness gate, including all browser and Compose
checks. Neither batch is merged or published by this action.
Batch 2 is [draft PR #106](https://github.com/tranquilWorks/gitg-self-host/pull/106),
based on PR #105 rather than main.

## Implemented acceptance

1. Explicit N/A and deferred choices are removed from assessment fallback even
   with missing capacity or no eligible reviewed candidates. Vacancies are not
   silently filled from the catalog. Invalid saved context pauses suggestions.
2. The default one-practice review offers three expandable factor groups and a
   partial-save mode. Blanks remain unknown, explicit zero remains zero, saved
   values reload and subsequent changes append revisions. The existing all-six
   mode remains available. Inactive mode fields are omitted from browser posts.
3. When no distinct reviewed alternative exists, the user can deliberately
   explore another practice and review its fit. Browsing is not a context rank.
4. The authenticated saved-context page offers a three-choice shortlist and
   paginated deferred/N/A/all views for the current assessment. Review horizons
   show dates without changing deferral or creating a timer/penalty. Reconsider
   opens the form; only an explicit save changes context.
5. [Browser policy 2.0](../context-discovery-policy.md) records these selection
   rules separately from unchanged context-priority/scoring mathematics.

No canonical content, domain algorithm, model/migration, prior snapshot, score,
activation, privacy export or shared practice-guide renderer is changed. No
live owner data is accessed. Existing context append/idempotency and ownership
checks remain authoritative. Batches 03–08 remain planned.

## Local verification closeout

- Regression coverage: **1,926 distinct nonbrowser cases passed across runs**.
  The first broad run had 1,881 passes and one failure before stopping. After
  repair, all 45 failed/unfinished cases passed in 90.00s. A JUnit class/name
  comparison against the complete collection confirms 1,926 passing IDs with
  none omitted. This is not a claim of one clean full-suite invocation.
- Repair verification: **60 passed** in 61.33s (eight new behavior cases plus
  52 catalog review tests). Earlier selection: 22 integration tests passed,
  including the original three new cases. Final Home audit-message guard and
  guided-entry regression: **9 passed** in 27.35s.
- Browser: three distinct journeys passed, including desktop/mobile context
  saves, deferral, exploration and reconsideration plus the existing private
  context/alternative journey. Final route recheck: **2 passed** in 61.08s.
  Desktop/mobile screenshots inspected; retained names are
  `context-partial-{1280,390}.png` and `context-deferred-{1280,390}.png` under
  `test-results/pilot-walkthrough/`.
- **All 17 full-profile readiness commands passed**, executed from the unchanged
  `contracts/verification.commands` after the repaired contract gate. This
  includes catalog governance, composite scoring, applicability, calibration
  software/consent/analysis, pilot, curriculum, competency evidence, context,
  Personal OS, priority, M6C/M6D, weekly and owner-operations backup verification.
- Batch schema/scope, manifest (3,413 files), Ruff, Django and no-migration checks
  passed. Protected canonical data, authoring/reports, domain algorithms,
  models/migrations, shared guide CSS and guide URL configuration are identical
  to the baseline. Content hash remains
  `ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`;
  frozen legacy projection remains
  `9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.

Local receipts: `/tmp/m6l02-full.log` and `.xml`,
`/tmp/m6l02-continuation.log` and `.xml`, `/tmp/m6l02-repair.log`,
`/tmp/m6l02-browser-route.log`, `/tmp/m6l02-home-errors.log`, and
`/tmp/m6l02-readiness.log` (exit sentinel `0`). These are temporary local files;
PR CI retains hosted artifacts. Reproduce with `scripts/agent-verify.sh full`
and the selected pytest files. Browser runs use
`PLAYWRIGHT_BROWSERS_PATH=$PWD/.playwright-browsers` locally.

## Repairs and hosted boundary

Pre-repair behavior tests reproduced the two exclusion failures and absent
partial-save behavior. The broad failure exposed that the complete
`growth/urls.py` file participates in catalog review fingerprints. It was
restored byte-identically and the new route registered in
`grounded_growth/urls.py`; its public URL and authentication remain the same.
No quality report, historical receipt or test gate was weakened. A final audit
also made the context-verification failure message visible on Home.

The hosted browser and Compose jobs passed on the repaired routing commit
`f4b3dca` in [run 36525895575](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36525895575).
The final Home-message/evidence commit needs its own aggregate gate; consult
[PR #106](https://github.com/tranquilWorks/gitg-self-host/pull/106) for current
status. The locally reviewed screenshots and earlier hosted browser artifacts
were inspected. Exact-final hosted aggregate/artifact approval is pending.
Neither merge nor publication is claimed. Synthetic software checks do not
establish participant or specialist acceptance.

## Rollback

Revert this batch's browser service, forms, routes and templates. No migration
or data restore is required; newly saved partial contexts remain valid under
the existing `GG-CONTEXT-1.0` contract. Reverting presentation restores the prior
fallback limitation, so keep explicit exclusions visible during operator review.

## Successor verification update

On 29 September, the exact final head `80faeac57c183ce9038d3479a60f0ec0a6a59e97`
passed hosted quality, browser, Docker Compose and aggregate Pilot readiness
gates in [run 36527658512](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36527658512).
PR #106 remains a draft; publish was correctly skipped.
