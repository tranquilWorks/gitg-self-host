# M6L-04 — Recurring weekly execution

Baseline: `10b040f3976f06e4e7fa53fe07b928ef4b60931a` (M6L-03 draft).
Branch: `codex/m6l-04-recurring-weekly`. [Draft PR #108](https://github.com/tranquilWorks/gitg-self-host/pull/108), stacked on #107. Owner request: “next batch and bath
remaining update at end of it”. Implementation and verification only; no merge,
publication or live-data operation is claimed.

## Delivered behavior

All four review choices now lead to a deliberate next step. Replanning preserves
original dates, proof and saved reviews; earlier revisions remain readable.
The previous planned week shows its evidence, adjustment and intended next step,
with the actual week gap and no inferred failure. A generic, optional all-day
calendar download supports upcoming plans without private narrative or automatic
reminders. Separate confirmation is required to pause or stop a practice.

See [behavior, privacy and rollback](../weekly-followup.md). Existing weekly v1,
practice transitions, model bytes, historical records, canonical content,
assessment, evidence and scoring contracts are preserved. No migration.

## Verification status

- **21 focused tests passed**, including all 15 new follow-up cases and six
  existing weekly cases. They cover retained revisions, stale forms, all four
  next steps, owner/assessment boundaries, corruption, calendar privacy and
  review cutoff replay. Intentional status transitions are the only expected
  nonweekly state difference.
- **Three distinct local browser journeys passed**, then all three passed again
  after navigation/button polish. The two new journeys cover 390px and 1280px
  recovery, review, calendar download and explicit pause; the existing journey
  also checks 200% zoom. Eight screenshots were retained and representative
  mobile/desktop views inspected. No horizontal overflow; the pause page now
  asserts exactly one current navigation entry.
- Complete hosted browser suite and Docker deployment drill passed on
  implementation commit `a7f0c47` in
  [run 36595706183](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36595706183).
  This predates the navigation polish and is not final-head aggregate approval.
- **All 1,954 nonbrowser tests passed** in the uninterrupted full-profile run
  (20m13s; zero failures/errors in the retained JUnit receipt).
- **The isolated Docker Compose drill passed**: image build, mapped-port health
  and login, migrations, idempotent seeding, readiness/replay, populated weekly
  and Personal OS state, recreation, verified backup/restore, restored login
  credentials, preserved data and clean shutdown. Exit status 0.
- **All 17 serial readiness commands passed** in `scripts/agent-verify.sh full`,
  which exited 0: catalog governance, composite catalog/scoring, applicability,
  assessment calibration/collection/analysis, pilot, curriculum, competency
  evidence, context, Personal OS, context priority, M6C, M6D, weekly and owner
  operations. The run was uninterrupted and required no repair.
- Final Ruff, Django checks, migration drift, contract schema, scope and manifest
  checks pass. Final-head hosted aggregate verification is still required before
  merge; earlier-commit successes are not final-head approval.
- Initial focused failures were fixture mistakes: one assertion incorrectly
  expected confirmed practice status to remain unchanged; another submitted a
  second check-in as a first record. Both were repaired without changing product
  logic or weakening invariants. Screenshot review caught dual navigation
  highlighting on the new decision route; the route and button spacing were
  corrected and all affected browser journeys rerun successfully.

Local receipts: `/tmp/m6l04-focused.xml`, `/tmp/m6l04-browser.xml`,
`/tmp/m6l04-browser-polish.xml`, `/tmp/m6l04-full.xml`, `/tmp/m6l04-full.log`,
`/tmp/m6l04-compose.log`; screenshots:
`test-results/pilot-walkthrough/weekly-followup-*.png`.

Canonical content and protected files are unchanged: 383 practices, 1,151 actions,
content hash `ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`,
legacy projection `9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.
Scope and schema checks pass; no recovery fingerprint or historical contract was
rebaselined. The full run began on the working implementation before commit;
its header therefore records the baseline head. The isolated image also predates
the later route/button polish, which has separate browser rechecks.

## Claim boundary and remaining batches

Software and synthetic browser evidence only. Calendar vendor import behavior,
real-user usability, specialist acceptance and longitudinal effectiveness have
not been established. No remote calendar service or telemetry is used.

After this batch, M6L-05 history/reassessment, M6L-06 whole-application consistency,
M6L-07 operator convenience and M6L-08 empirical product validation remain planned.
Batch 08 requires actual consented participant evidence; software tests cannot
close those axes. M6L-01–03 remain separate, CI-verified draft PRs, unmerged.
