# M6L-04 — Recurring weekly execution

Baseline: `10b040f3976f06e4e7fa53fe07b928ef4b60931a` (M6L-03 draft).
Branch: `codex/m6l-04-recurring-weekly`. Owner request: “next batch and bath
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

Verification is in progress. Three local browser journeys passed, including
mobile/desktop recovery, review, download and explicit pause, plus the existing
weekly loop. Screenshots at 390px and 1280px were inspected; the journeys assert
no horizontal overflow. Focused checks and the full local profile must finish
before this batch is described as locally verified. Hosted aggregate checks and
Compose are still pending.

Local receipts: `/tmp/m6l04-focused.xml`, `/tmp/m6l04-browser.xml`,
`/tmp/m6l04-browser.log`; screenshots:
`test-results/pilot-walkthrough/weekly-followup-*.png`.

## Claim boundary and remaining batches

Software and synthetic browser evidence only. Calendar vendor import behavior,
real-user usability, specialist acceptance and longitudinal effectiveness have
not been established. No remote calendar service or telemetry is used.

After this batch, M6L-05 history/reassessment, M6L-06 whole-application consistency,
M6L-07 operator convenience and M6L-08 empirical product validation remain planned.
Batch 08 requires actual consented participant evidence; software tests cannot
close those axes. M6L-01–03 remain separate, CI-verified draft PRs, unmerged.
