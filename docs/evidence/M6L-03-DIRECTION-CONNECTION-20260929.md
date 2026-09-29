# M6L-03 — Direction-to-practice connection

Baseline: `80faeac57c183ce9038d3479a60f0ec0a6a59e97` (M6L-02 draft).
Branch: `codex/m6l-03-direction-connection`.
Owner request: “lets do batch 3”. Implementation, verification and draft review;
no merge or publication is claimed.

## Implementation

- Explicit priority, intended outcome, unknown and declined connections; immutable
  assessment/practice revisions with source Personal OS provenance and hashes.
- Setup and weekly planning show the current connection and let the owner revise
  it. Previous choices remain readable; weekly history is not reinterpreted.
- Concise direction review preserves principles, audit responses and earlier
  revisions, with stale-form and owner/epoch validation.
- Additive migration 0014, owner archive v4, deletion counts/order, backup table
  fingerprints and operations verification. See the
  [contract and rollback boundary](../practice-direction-contract.md).
- Protected guide routes/styles, canonical content, scoring and source reports
  remain unchanged. New routes live in `grounded_growth/urls.py` to preserve the
  catalog’s existing file-level quality fingerprints.

## Verification in progress

- Focused connection/lifecycle/backup/catalog-quality run: 79 passed. Initial
  connection test fixture omitted required assessment provenance; repaired that
  synthetic fixture. No application defect was masked by the correction.
- New desktop/mobile browser journey: 2 passed after correcting a colon-sensitive
  label locator. Final polished screenshots and existing core journeys are running.
- Isolated migration 0013→0014→0013→0014 with retained fixture data: passed after
  explicitly selecting production settings for the subprocess (the test settings
  originally routed it to `tests.sqlite3`). Populated backup preservation: passed.
- Ruff, Django checks, migration drift, contract schema and scope: passed.
- Full verification and hosted gates: pending. The local full run began before
  the migration-test environment correction; any failure there needs a focused
  continuation against the corrected test, not a change to the migration.

Software and synthetic-browser evidence only. No new participant observations,
specialist acceptance, empirical validation, container publication or live-data
operation is claimed. Batches 04–08 remain planned.
