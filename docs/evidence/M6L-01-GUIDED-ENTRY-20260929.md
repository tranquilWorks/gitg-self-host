# M6L-01 — Guided entry and practice discovery

## Scope

Owner requested all non-competency design gaps be captured as actions/batches
and the first batch begun. [Program](../plans/m6l/README.md): eight batches,
31 actions. Baseline `c0208be6c031b37c75657f8190e50305a691c463`;
branch `codex/m6l-01-guided-entry`.

Implemented a direction/action-led Home and first-use guide; explicit seed/demo
notice; three existing recommendations by default; explicit public-metadata
search and domain filtering; deterministic twelve-result pages; empty-state
recovery. Personal OS copy reflects account archive/deletion; generic closeout
no longer asserts that a substantive interaction occurred.

No canonical content, ID, scoring, ranking mathematics, activation, schema,
private authored text surface or historical user data is changed. The demo
seed remains intact. Context/exclusion fallback behavior is explicitly tracked
in M6L-02; demo opt-in installation in M6L-07. The action register distinguishes
those remaining tasks from this presentation slice.

## Verification checkpoint

- Active contract validated against the existing vendored batch schema; final
  scope and manifest checks are repeated before committing.
- Exact final focused Django run: **60 passed** (8 guided-entry/discovery tests
  and 52 catalog quality/review-record tests). Covers no-assessment, demo and
  real-assessment entry; all 383 browse results without duplicates; safe composed
  filters; unchanged recommendations/state; stopped-practice weekly review;
  visible audit errors; and page-specific stylesheet isolation.
- Exact final browser run: **3 passed**, covering discovery at 1280px and 390px
  plus the complete friendship workflow. Desktop/mobile Home and explorer
  screenshots inspected. Earlier runs cover 28 distinct selected browser cases
  across runs; this is not a claim of a single clean full browser-suite run.
- Isolated Compose deployment drill reports **passed**: mapped-port health and
  real login, migrations/idempotent seed, replay/readiness, recreation, volume
  persistence, backup/restore and clean shutdown. Pre-backup and restored critical
  state hash both `a73cfc00a1d9362671f70a4943975d03a1311c39d5d7e3bd31236a4e1adc5609`.
  Its image predates the final stylesheet isolation only; the final styling is
  browser-tested. Hosted CI must check the committed image.
- Full final local verification: **running**, 1,918 nonbrowser tests followed by
  all readiness commands in `contracts/verification.commands`.
- Required hosted **Pilot readiness gate**: pending; no merge or publication.

Reproducible commands: `scripts/agent-verify.sh full` (local pytest used four
workers), `make compose-smoke`, and focused pytest runs of
`tests/test_guided_entry.py`, catalog review-record tests,
`tests/e2e/test_guided_entry.py`, and the friendship browser workflow. Synthetic
browser screenshots are retained under `test-results/pilot-walkthrough/` by the
browser artifact workflow. Local diagnostic logs are `/tmp/m6l-full-final.log`,
`/tmp/m6l-final-focus.log`, `/tmp/m6l-browser-isolated.log`, and
`/tmp/m6l-compose-final.log`; these are temporary, not committed receipts.

## Audit and limitations

Initial checks caught a ForeignKey search lookup error, an immutable-assessment
fixture error, and stale copy/first-card selectors; all were corrected and their
paths retested. The HTTP login probe now uses the stable Home heading marker.
An earlier broad run ended with status 143 near completion and had a failure
indicator without a final traceback; it is not counted as a pass.

Shared `app.css` participates in the catalog review fingerprints. It is restored
byte-identically to baseline. New Home/discovery styles load only on those pages
through an empty-by-default template block; practice guides do not load them.
Canonical content, quality reports and fingerprint gates were not rewritten.

Software and synthetic-browser evidence cannot close the empirical actions in
M6L-08. No live owner data was accessed or changed. Context fallback/exclusion
semantics remain scheduled for M6L-02, not claimed repaired here.

## Rollback

Revert this batch's presentation and discovery changes. No database migration,
data deletion or historical record rewrite is required.
