# M6L-05 — History and reassessment continuity

Baseline: `3cfa88dc9a8dbcbc25ba6ad59f171bd4f5cd285e` (M6L-04 draft).
Branch: `codex/m6l-05-history-continuity`. Owner request: “go for 5”.
Implementation and verification only; no merge, publication or live-data action.

## Delivered behavior

- Owner-only assessment-period history with independently paginated practices
  and weekly revisions, original provenance and immutable proof/review detail.
- Reassessment entry explains new baseline/context/coverage boundaries and
  identifies the existing practice. Demonstration data remains explicitly labeled.
- Optional selected intention reuse: no defaults, exact replacement preview,
  separate signed confirmation, current/source/target conflict checks and atomic
  writes. Unselected target values and all earlier records are preserved.
- Older active/paused practices retain their original period, check-in and
  stop/resume/closeout paths. Paused practices whose evidence meets requirements
  now expose the already-supported closeout action. New weekly plans cannot mix
  periods; older closeout credit remains attached to its original assessment.

See [behavior, provenance and rollback](../history-continuity.md). No migration,
canonical content change, scoring-mathematics change or historical contract change.
Historical weekly reading is separate from current-period write authorization.

## Verification status

- Focused Django regression: 34 passed (`/tmp/m6l05-focused.xml`).
- Refinement: 2 passed (`/tmp/m6l05-refined.xml`), including a paused older-practice
  closeout with credit confined to the original period and current-period state intact.
- Six distinct browser journeys passed: history/reuse at 390px and 1280px, weekly
  execution, real assessment completion, share-code import and practice lifecycle
  (`/tmp/m6l05-browser.xml`, `/tmp/m6l05-integration-browser.xml`).
- Two browser polish rechecks passed (`/tmp/m6l05-browser-polish.xml`). Final
  completed/stopped copy checks passed: one Django and two browser cases
  (`/tmp/m6l05-terminal.xml`). Terminal practices no longer suggest continuation.
- Ten screenshots retained at `test-results/pilot-walkthrough/history-*.png`.
  Inspected mobile reuse preview, desktop period history and mobile older-practice
  controls; browser checks cover both widths, navigation and horizontal overflow.
- Full regression: **1,968 passed**, zero failures/errors/skips
  (`/tmp/m6l05-full.xml`, 1,192.55 seconds). All six contract checks passed.
  All **17 required readiness commands passed** in the uninterrupted full profile
  (exit 0, completed 20:13:52 UTC). The executed command inventory exactly matches
  `contracts/verification.commands`. Receipt: `/tmp/m6l05-full.log`, also retained
  at `docs/evidence/local/verify-full-20260929T193220Z.log`.
- `make compose-smoke`: passed, exit 0 (`/tmp/m6l05-compose.log`). Isolated project
  `ggsmokelocal03873800` verified build/health, migrations, canonical seed idempotency,
  login, all applicable readiness/replay contracts, persisted synthetic intentions,
  recreation, verified online backup/restore, matching critical state and clean
  Gunicorn shutdown. The script cleaned up its own containers and volume.

Draft [PR #109](https://github.com/tranquilWorks/gitg-self-host/pull/109) is stacked
on Batch 4's draft #108. Implementation head `23be1a5` passed hosted browser and Docker checks in
[CI run 36620822685](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36620822685);
its quality job was still running at local closeout. The final documentation head
requires its own aggregate CI gate before merge. Neither this
batch nor its preceding M6L drafts is merged or published.

The full profile began with the implementation in the working tree before its
first commit, so its log header records baseline `3cfa88d`. The Docker image also
predates the final terminal-state wording adjustment in `23be1a5`; that adjustment
has the separate three-case passing receipt above. No service, schema or runtime
configuration changed after the full profile and Docker drill started.

## Reproducible full and browser commands

```bash
PYTEST_ADDOPTS='-n 4 --dist=load --maxschedchunk=1 --maxfail=1 --output=/tmp/m6l05-full-artifacts --junitxml=/tmp/m6l05-full.xml' ./scripts/agent-verify.sh full

make compose-smoke

PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers" .venv/bin/pytest tests/e2e/test_history_continuity.py tests/e2e/test_core_flow.py::test_weekly_execution_plans_one_action_and_reviews_only_existing_proof -q --output=/tmp/m6l05-browser-artifacts --junitxml=/tmp/m6l05-browser.xml

PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers" .venv/bin/pytest tests/e2e/test_core_flow.py::test_complete_assessment_and_save_canonical_outputs tests/e2e/test_core_flow.py::test_import_gga11_and_supported_gga1 tests/e2e/test_core_flow.py::test_guided_practice_draft_pause_and_completion_flow -q --output=/tmp/m6l05-integration-browser-artifacts --junitxml=/tmp/m6l05-integration-browser.xml

PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers" .venv/bin/pytest tests/e2e/test_history_continuity.py -q --output=/tmp/m6l05-browser-polish-artifacts --junitxml=/tmp/m6l05-browser-polish.xml

PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers" .venv/bin/pytest tests/test_history_continuity.py::test_paused_older_practice_can_close_without_transferring_credit tests/e2e/test_history_continuity.py -q --output=/tmp/m6l05-terminal-artifacts --junitxml=/tmp/m6l05-terminal.xml
```

## Acceptance coverage

| Action | Implementation and verification |
| --- | --- |
| M6L-05-01 readable history | Owner-filtered period/practice/weekly pages; pagination, original proof cutoff/replay, corrupted-history refusal, owner isolation and read-only tests. |
| M6L-05-02 reassessment consequences | Entry notice names the current practice and explains new baseline/coverage, context review, retained earlier credit and optional reuse; actual assessment and share-code journeys pass. |
| M6L-05-03 selected reuse | Unchecked choices, exact preview and signed confirmation; unchanged source/unselected target values, stale source/target/assessment, expiry/tampering, ownership and atomic rollback tests. |
| M6L-05-04 older practices | Active/paused navigation, current-week mixed-period refusal, paused closeout, credit isolation and completed/stopped copy checks; existing lifecycle browser journey passes. |

## Final scope audit

The active contract validates against the vendored schema. All 28 changed/new
paths are allowed, with zero forbidden-path changes. Final manifest, Ruff format
and lint, Django checks, migration-drift and whitespace checks pass. No new model,
migration, fingerprint update or runtime dependency. `MANIFEST.tsv` covers 3,453
files. All four Batch 5 actions are locally verified; final-head CI remains pending.

## Scope and remaining work

The 383 practices / 1,151 actions are untouched. Content hash remains
`ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`; legacy projection
`9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.
No fingerprint or historical guard is weakened.

Software and synthetic-browser evidence only. The new history does not claim
retrospective score comparison, empirical effectiveness or specialist acceptance.
Confirmed intentions are ordinary current-period revisions; their selected source
is shown during preview, without a new persistent copy-receipt table.

After Batch 5, three batches / ten actions remain planned: 06 whole-application
consistency, 07 operator convenience and 08 empirical product validation. Batch 08
still requires real consented observations and qualified analysis.
