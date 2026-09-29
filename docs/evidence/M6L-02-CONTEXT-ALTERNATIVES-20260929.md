# M6L-02 — Explicit context and alternatives

Owner requested the next batch after M6L-01. This branch is stacked on
`1274ff1969178bd863c5ab1e2d21c436a9ea2ef5` (draft PR #105), whose full local
verification passed: 1,918 tests and all readiness commands; hosted run
[36515667838](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36515667838)
passed the aggregate Pilot readiness gate, including all browser and Compose
checks. Neither batch is merged or published by this action.

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

## Verification checkpoint

- Pre-repair tests reproduced both excluded-fallback cases and the absent
  partial-save behavior (3 failures).
- Focused behavior tests: **8 passed** in 38.73s. Context/browser integration
  selection: **22 passed** in 189.69s (includes the original three new cases).
- Browser journeys: **3 passed** in 101.08s: desktop/mobile partial save,
  deferral, explore and explicit reconsideration; existing private context and
  distinct-reviewed-alternative journey. Final card-layout recheck is running.
  Initial browser invocation used the wrong cache path; rerun uses the existing
  project `.playwright-browsers` installation.
- Full local gate: running with 1,926 nonbrowser tests and all readiness gates;
  detached log `/tmp/m6l02-full.log`, exit sentinel `/tmp/m6l02-full.exit`, JUnit
  `/tmp/m6l02-full.xml`. Hosted aggregate pending.
- Schema and 23-file scope check passed. Manifest, Ruff, Django and migration
  drift checks passed at the start of the full gate; repeat manifest after the
  final evidence update. Desktop and mobile screenshots inspected; final card
  spacing recheck pending.

Synthetic checks cannot establish participant or specialist acceptance. No
merge, publication or live deployment is claimed.

## Rollback

Revert this batch's browser service, forms, routes and templates. No migration
or data restore is required; newly saved partial contexts remain valid under
the existing `GG-CONTEXT-1.0` contract. Reverting presentation restores the prior
fallback limitation, so keep explicit exclusions visible during operator review.
