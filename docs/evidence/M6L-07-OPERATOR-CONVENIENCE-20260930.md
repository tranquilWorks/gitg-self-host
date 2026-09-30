# M6L-07 — Operator convenience

Owner explicitly requested Batch 07 on 30 September 2026. Baseline
`7078f9723d500d3f18eac78fcfc9df5163a21180`; branch
`codex/m6l-07-operator-convenience`. Implementation, verification and stacked draft
PR only. No merge, publication or live-volume operation.

## Implementation

- 07-01: new container startup defaults to personal mode; explicit demo opt-in,
  idempotent seed, no removal of existing assessments/passwords/history, malformed
  flag fails before database creation. Legacy seed command/service defaults remain
  compatible; `--without-demo` is the operator's library-only route.
- 07-02: full revision embedded at build time through Compose/CI build arguments;
  authenticated installation page and local CLI expose valid metadata or honest
  unknown. No remote check, silent update or new telemetry.
- 07-03: allowlisted database/configuration diagnostics, password recovery,
  pinned update, active-practice guard and ordered verified offline restore docs.
  Existing backup/replay contracts remain unchanged.

## Verification

Final regression on the repaired runtime: **2,004 passed**, six intentional
test-only DATABASES override warnings, 759.45 seconds. Receipt:
`/tmp/m6l07-regression.xml`; `scripts/agent-verify.sh quick` exited zero.
The final harness-only edits separately passed all five deployment-contract
checks (`/tmp/m6l07-harness.xml`). All 17 exact full-profile readiness commands
then passed in contract order (`/tmp/m6l07-readiness-final.log`, exit zero).

Expanded `make compose-smoke` passed on `f928157` (exit zero;
`/tmp/m6l07-compose-final.log`). Verified mapped-port authentication, personal
startup without assessment, explicit demo opt-in, embedded revision, diagnostics,
seed idempotency, both score replays, all readiness gates, synthetic Personal OS /
context / weekly state, changed-password persistence, verified backup, offline
verification before copying and before restart, exact restored state, restored
password behavior and clean Gunicorn shutdown. The disposable project
`ggsmokelocal0453901`, its volume and private image tag were removed by cleanup.

Focused operator/deployment/bootstrap/backup checks: 29 passed (38.73 seconds),
`/tmp/m6l07-focused.xml`. Six warnings come from intentional test-only DATABASES
settings overrides. Initial browser checks found a test reading innerText from a
collapsed native menu; corrected to check its text content and the visible
More · Account summary. No product behavior changed for that selector correction.
Focused browser rerun: two passed at 320/1280px (18.82 seconds),
`/tmp/m6l07-browser-fixed.xml`, including keyboard disclosure, current navigation,
revision display and enlarged text. These initial focused checks preceded the
frozen-importer repair described below.

Initial broad runs hit a full host filesystem: SQLite I/O errors and a Chromium
crash invalidate those attempts. Stopped the affected regression and reclaimed
inactive synthetic pytest databases and five untagged images from this project's
prior disposable drills; no user volume or unrelated image was removed. Retained
receipts: `/tmp/m6l07-full-initial.log`, `/tmp/m6l07-browser-initial.log` and XML.

The first Compose attempt correctly reached a personal account with no assessment.
Its existing Personal OS HTTP probe expected no redirect, so the personal-mode
probe now uses the authenticated installation page. After explicit demo opt-in,
all original Personal OS/replay/recovery probes remain. Failure receipt:
`/tmp/m6l07-compose-initial.log`. No application behavior was weakened.
A subsequent drill was intentionally
stopped to add verification immediately before copying the backup and again
before restarting the restored application; five deployment-contract checks pass.
Interrupted drill receipts remain `...compose-pre-offline-check.log`.

The complete nonbrowser run then passed 2,000 cases and failed the historical
importer fingerprint (`/tmp/m6l07-full.xml`, 784.85 seconds). This was a real
protected-file violation. The historical importer was restored byte-for-byte;
personal startup now uses an additive library-only orchestrator that reuses its
validators, projections and in-progress-practice guard. No fingerprint or gate
was changed. New tests compare every shared field except the expected ingestion
timestamp and verify rollback for both active and paused practices. The fresh
2,004-case regression above passed for this implementation. All 17
exact full-profile readiness commands passed separately in contract order; this is
a repaired continuation, not a claim that the initial full harness exited zero.

The complete browser suite passed 54 cases (`/tmp/m6l07-all-browser.xml`,
825.54 seconds). Both personal-start journeys passed again for the new import
entry point and final layout/capture polish: two passed in 25.66 seconds
(`/tmp/m6l07-capture-browser.xml`). Inspected final 320px/1280px screenshots:
`test-results/pilot-walkthrough/operator-installation-320.png` and
`operator-installation-1280.png`. They cover keyboard disclosure, current
navigation, wrapped revision text, semantic/overflow checks and 200% text.
All 18 operator tests plus five unchanged frozen-recovery tests passed together
(`/tmp/m6l07-frozen-fixed.xml`, 23 passed in 133.42 seconds). A first parity
assertion included the automatically refreshed
`imported_at` timestamp; it was narrowed only by excluding that metadata field.
All canonical IDs, fields, weights, instructions and rules remain compared.

The final Compose harness uses a unique `ggsmoke…:verification` image tag,
so the drill does not overwrite an operator image tag. Its exit/signal cleanup
removes only its own disposable project and image. The superseded drill was
stopped and its synthetic resources removed before this final run; receipt:
`/tmp/m6l07-compose-before-image-isolation.log`.

[Draft PR #111](https://github.com/tranquilWorks/gitg-self-host/pull/111) is stacked
on #110. On implementation head `f928157`, hosted browser and Compose jobs passed
in [run 36665161382](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36665161382);
the quality/aggregate gate was still running at closeout. The documentation-only
closeout triggers a new run; final-head CI remains pending. No merge or publication.

Final scope/schema, manifest (3,477 entries), Ruff formatting/lint, Django system
and migration checks passed. All 30 changed paths are allowed; none match a
forbidden path. Protected importer, canonical data and historical services remain
byte-identical to the Batch 06 baseline.

## Invariants and limits

All 383 practices / 1,151 actions and their stable IDs are unchanged.
Catalog content hash:
`ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`.
Legacy projection hash:
`9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`. No migration,
canonical data, historical scoring, evidence, consent or renderer-source change.
Demo selection is installation behavior, not research consent or personalization.
Diagnostics never print passwords, hosts, private paths or record values and do
not repair data or replace backup verification. Embedded revision is build metadata,
not a signature or registry digest. No empirical evidence axis is closed.
After this batch, one batch / four actions remain: M6L-08 empirical validation.

Final head `941fb78d6bca780920a805a03cff9dad690a8dfd` subsequently passed all
hosted quality, browser, Compose and aggregate gates in
[run 36666899420](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36666899420).
Publication was skipped; PR #111 remains a draft and unmerged.
