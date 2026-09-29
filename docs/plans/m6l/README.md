# M6L — Complete the guided product experience

Owner direction, 29 September 2026: capture every non-content design gap as
actions and batches, and begin the first batch. Baseline: `c0208be6c031b37c75657f8190e50305a691c463`.
This program implements Decision 046 and M6 Phase F. Competency authoring is
excluded. The executable action register is [actions.yaml](actions.yaml).

## Delivery order

| Batch | Outcome | Dependencies | Status |
| --- | --- | --- | --- |
| M6L-01 | Guided entry, explicit demonstration labeling, concise recommendations and searchable exploration, immediate copy repairs | Published catalog | CI verified; draft PR #105 |
| M6L-02 | Easier explicit context collection and dependable N/A/defer/alternative journeys | 01 | CI verified; draft PR #106 |
| M6L-03 | User-chosen links between direction, priority and practice | 01 | CI verified; draft PR #107 |
| M6L-04 | Review-to-next-week handoff, recovery after missed plans, upcoming-action support | 02, 03 | CI verified; draft PR #108 |
| M6L-05 | Readable history and deliberate continuity across reassessment | 03, 04 | CI verified; draft PR #109 |
| M6L-06 | Whole-application language, navigation and accessibility consistency | 02–05 | Implemented; verification in progress |
| M6L-07 | Installation, version visibility and operator recovery convenience | 01 | Planned |
| M6L-08 | Real-user multi-cycle evaluation and assessment calibration evidence | 02–06; operator readiness for pilot | Planned; empirical evidence remains open |

## Batch 1 boundary

Deliver a working entry and discovery journey without changing recommendation
mathematics or stored user state. Home prioritizes direction, weekly action and
the current practice. The existing demonstration assessment is visibly labeled;
a real assessment has a prominent entry. Keep its seed/history intact.
Recommendations show at most three choices. Explicit browsing adds search,
domain filtering and stable pages of twelve results. Filtering searches public
practice metadata only and does not become a new ranking input.

Repair the stale Personal OS privacy/lifecycle paragraph and the unconditional
relationship-specific completion claim. Preserve private authored text on its
existing Personal OS/weekly surfaces. Do not copy it onto Home.

Deeper onboarding persistence/demo opt-in installation belongs to 07; lower-burden
context entry, alternative discovery and exclusion/fallback semantics belong to
02. This separates navigation changes from versioned recommendation decisions.

## Acceptance and execution

Every action has observable acceptance and status in the register. `planned`
does not mean implemented; `implemented` does not mean verified. Record exact
verification in the batch evidence and update statuses only from that evidence.
Every implementation batch needs its own bounded active contract, relevant
regression/browser coverage and required CI. Archive previous contracts here.
The first contract validates against the repository's existing vendored
`docs/plans/m6k/portfolio/batch.schema.json` (the generic skill's suggested
`contracts/batch.schema.json` is absent).

Preserve canonical content, stable IDs, assessment mathematics, historical
evidence, scoring, activation, and in-flight practices. Later changes to
context behavior must version their contracts and retain replay. Goal links
must be user-authored, not inferred from private prose. No plan, reminder or
reflection itself creates completion credit or evidence.

Batch 08 must distinguish software preparation from actual recruitment,
consented observations, qualified analysis and review. Existing tests and the
owner's product acceptance cannot close empirical axes. Record unsuccessful
and inconclusive observations as well as successful ones.

Current authorization covers planning the entire program and implementing 01–06.
The owner requested the next batch after M6L-05.
Batches 07–08 remain planned. Publication of the catalog
was completed under the previous authorization; this new batch's merge and
publication are separate from implementation.

## Rollback and evidence

Batch 01 is presentation-only, with no migration. Revert its code/templates to
restore previous presentation without restoring or deleting a database. The
catalog release remains independently available. Each later batch must specify
its own migration/rollback boundary before implementation.

See [M6L-01 evidence](../../evidence/M6L-01-GUIDED-ENTRY-20260929.md).
