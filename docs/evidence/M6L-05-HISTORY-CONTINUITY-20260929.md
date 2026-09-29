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

Initial focused run: 34 tests passed. Two refinement checks passed, including a
paused older-practice closeout that leaves current-period completion state intact.
Three browser journeys passed (new 390px/1280px history/reuse journeys and existing
weekly execution). Full local profile, broader affected browser checks, screenshot
inspection and Docker recovery validation are pending.

Receipts: `/tmp/m6l05-focused.xml`, `/tmp/m6l05-refined.xml`,
`/tmp/m6l05-browser.xml`. Screenshots: `test-results/pilot-walkthrough/history-*.png`.

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
