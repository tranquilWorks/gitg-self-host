# M6L-08 — Empirical validation preparation

Owner requested Batch 08 on 30 September 2026. Baseline
`941fb78d6bca780920a805a03cff9dad690a8dfd`; branch
`codex/m6l-08-empirical-validation`. Implementation and stacked draft PR only.
Main remains `c0208be6c031b37c75657f8190e50305a691c463`.

## Delivered preparation

- 08-01: executable entry/three-week protocol, neutral prompts, recruitment/access
  plan, separate observation/calibration consent, retention/withdrawal and stops.
- 08-02: strict local observation format and private aggregate CLI; absent versus
  stopped/skipped outcomes, help, participant-selected time bands, fit and barriers.
- 08-03: exact eight-axis input/method/role matrix and existing consented export /
  analysis commands; unsupported additional measures explicitly need reviewed work.
- 08-04: qualified-review packet and versioned correction register, including
  inconclusive/negative findings, provenance, retest and permitted-claim boundaries.

No actual participant records or named reviewer receipts were supplied. The
historical single-session pilot is not current multi-cycle evidence. Preparation
can complete 08-01; the other three actions and the overall batch remain open.
No recruitment, contacts, participant session, live data access or deletion occurred.

## Local verification

Focused CLI/privacy/semantic checks initially passed 25 cases, then **27 passed**
in 1.61 seconds after adding strict fixed-length revision/reference checks
(`/tmp/m6l08-focused-final.xml`). Covers real command entry points, strict allowlists,
duplicate/invalid records, withdrawn exclusion, missing observations, repeated
review semantics, small-cell and complementary suppression, private mode-0600
output, oversized/malformed input, symlinks, no overwrite and zero evidence claims.
Ruff formatting/lint passed after correcting one overlong error-message line.
The documented JSON example also passed a real init/edit/summarize rehearsal with
five explicitly synthetic records (`/tmp/m6l08-manual-cli.log`): private output,
unchanged input, no participant references in output and zero completed axes.

The host had only 493 MiB available before testing. Removed only the completed
Batch 07 synthetic `/tmp/pytest-of-kbianco/pytest-272` fixture directory after
verifying its zero-exit receipt and absent active lock. Batch 08 temporary test
state uses a dedicated runtime temporary directory; receipts remain retained.

Relevant existing browser journeys passed **seven cases**, 23 deliberately
unselected, in 95.17 seconds (`/tmp/m6l08-browser.xml`, exit zero). Includes
assessment consent/contribution/withdrawal, optional feedback, weekly planning,
missed-plan recovery and history continuity. Inspected fresh mobile feedback and
desktop weekly-review screenshots in `test-results/pilot-walkthrough/`.

Full nonbrowser regression passed **2,031 cases** with six existing intentional
DATABASES-override warnings in 658.09 seconds (`/tmp/m6l08-full.xml`). The same
`./scripts/agent-verify.sh full` invocation passed all 17 exact readiness commands
in contract order and exited zero at 14:55 UTC (`/tmp/m6l08-full.log`).
The complete isolated `make compose-smoke` drill passed on `db8bf54`
(`/tmp/m6l08-compose.log`, exit zero): personal/demo startup, authenticated HTTP,
revision and diagnostics, idempotency, all runtime readiness, synthetic user state,
container recreation, password persistence, verified offline restoration, exact
replay and clean shutdown. Confirmed cleanup of its private
`ggsmokelocal0807208` container, volume and image tag. No runtime/UI
change; all test data is conspicuously synthetic. [Draft PR #112](https://github.com/tranquilWorks/gitg-self-host/pull/112)
is stacked on #111, unmerged and unpublished. No human evidence was synthesized.
Hosted browser and Compose jobs passed on implementation head `db8bf54` in
[run 36728774388](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36728774388);
quality/aggregate CI was still pending at closeout. The final documentation-only
commit triggers a fresh run; final-head CI remains pending.

## Invariants and limits

All 383 practices / 1,151 actions, canonical content and historical runtime files
are unchanged. No migration, source registry, scoring, feedback or calibration
contract change. Content hash:
`ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`;
legacy projection:
`9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.
The new observation reference is independent of the calibration token; no joins
or unconsented secondary use. Suppressed summaries remain sensitive. Automated
checks cannot authenticate an operator's provenance/consent assertion or establish
psychometrics, population accessibility, fairness, longitudinal effects or mastery.
`ER-M6A-003` and `RG-M6A-002` remain pending/open; zero evidence axes completed.

## Acceptance disposition and next execution

| Action | Disposition | Evidence still required |
| --- | --- | --- |
| 08-01 | Preparation locally verified | Named operators/reviewers and study launch record before real activity |
| 08-02 | Awaiting participant evidence | Consented observations across the planned cycles; known/unknown non-return and barriers |
| 08-03 | Awaiting participant evidence | Actual appropriate data for eight axes, including separately reviewed missing inputs |
| 08-04 | Awaiting qualified review | Named competence/provenance receipts, analysis conclusions and versioned follow-up decisions |

The batch remains prepared/awaiting evidence, with three empirical actions open.
Assign the responsible people, complete the reviewed launch record, run the actual
cycles, and supply authorized private evidence paths for analysis. No software
preparation, owner acceptance or synthetic rehearsal substitutes for that work.
The existing specialist governance and all eight assessment axes remain open.

Final contract/schema, scope, manifest, Ruff, Django and migration checks passed.
All 19 changed files are allowed; zero forbidden runtime/content paths changed.
MANIFEST contains 3,488 entries. Study-kit local links were checked. Final prose
clarifies that normal private assessment timing already exists while the new
observation study adds no tracking; calibration reuse stays separately optional.

## Execution follow-up

The owner requested execution of the remaining actions. Added the
[fieldwork packet](../pilot/m6l08/fieldwork.md): invitation, neutral screening,
reviewer brief and relative Day 0/7/14/21 task/deliverable sequence. These are
unsent drafts; no people, consent, dates or findings were invented. Requested the
coordinator/recruitment route, reviewer assignments and any authorized existing
evidence paths. Those inputs remain unavailable, so participant collection and
qualified review have not begun. The three empirical actions remain open.

This follow-up changes documentation only. Verified local links, batch scope,
manifest and the repository contract checks; prior full runtime/test evidence
remains applicable. No new runtime tests or Docker run were needed for these
reversible prose additions. Final-head CI status remains separate.
