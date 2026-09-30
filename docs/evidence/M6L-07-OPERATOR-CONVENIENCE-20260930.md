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

## Verification in progress

Focused operator/deployment/bootstrap/backup checks: 29 passed (38.73 seconds),
`/tmp/m6l07-focused.xml`. Six warnings come from intentional test-only DATABASES
settings overrides. Initial browser checks found a test reading innerText from a
collapsed native menu; corrected to check its text content and the visible
More · Account summary. No product behavior changed for that selector correction.
Focused browser rerun: two passed at 320/1280px (18.82 seconds),
`/tmp/m6l07-browser-fixed.xml`, including keyboard disclosure, current navigation,
revision display and enlarged text. Final complete browser, full required profile
and expanded Compose drill are running on `fa7794e`.

Initial broad runs hit a full host filesystem: SQLite I/O errors and a Chromium
crash invalidate those attempts. Stopped the affected regression and reclaimed
inactive synthetic pytest databases and five untagged images from this project's
prior disposable drills; no user volume or unrelated image was removed. Retained
receipts: `/tmp/m6l07-full-initial.log`, `/tmp/m6l07-browser-initial.log` and XML.

The first Compose attempt correctly reached a personal account with no assessment.
Its existing Personal OS HTTP probe expected no redirect, so the personal-mode
probe now uses the authenticated installation page. After explicit demo opt-in,
all original Personal OS/replay/recovery probes remain. Failure receipt:
`/tmp/m6l07-compose-initial.log`. No application behavior was weakened. A subsequent drill was intentionally
stopped to add verification immediately before copying the backup and again
before restarting the restored application; five deployment-contract checks pass.
Interrupted drill receipts remain `...compose-pre-offline-check.log`.

The complete nonbrowser run then passed 2,000 cases and failed the historical
importer fingerprint (`/tmp/m6l07-full.xml`, 784.85 seconds). This was a real
protected-file violation. The historical importer was restored byte-for-byte;
personal startup now uses an additive library-only orchestrator that reuses its
validators, projections and in-progress-practice guard. No fingerprint or gate
was changed. New tests compare every shared field except the expected ingestion
timestamp and verify rollback for both active and paused practices. Broad
regression is repeated for this implementation; all 17 exact full-profile
readiness commands run separately in contract order.

The complete browser suite passed 54 cases (`/tmp/m6l07-all-browser.xml`,
825.54 seconds). The two personal-start journeys are repeated for the new import
entry point. A first parity assertion included the automatically refreshed
`imported_at` timestamp; it was narrowed only by excluding that metadata field.
All canonical IDs, fields, weights, instructions and rules remain compared.

[Draft PR #111](https://github.com/tranquilWorks/gitg-self-host/pull/111) is stacked
on #110. Hosted CI is pending; no merge or publication.

## Invariants and limits

All 383 practices / 1,151 actions and their stable IDs are unchanged. No migration,
canonical data, historical scoring, evidence, consent or renderer-source change.
Demo selection is installation behavior, not research consent or personalization.
Diagnostics never print passwords, hosts, private paths or record values and do
not repair data or replace backup verification. Embedded revision is build metadata,
not a signature or registry digest. No empirical evidence axis is closed.
After this batch, one batch / four actions remain: M6L-08 empirical validation.
