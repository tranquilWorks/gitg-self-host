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
Final browser, full required profile and expanded Compose drill are pending.

## Invariants and limits

All 383 practices / 1,151 actions and their stable IDs are unchanged. No migration,
canonical data, historical scoring, evidence, consent or renderer-source change.
Demo selection is installation behavior, not research consent or personalization.
Diagnostics never print passwords, hosts, private paths or record values and do
not repair data or replace backup verification. Embedded revision is build metadata,
not a signature or registry digest. No empirical evidence axis is closed.
After this batch, one batch / four actions remain: M6L-08 empirical validation.
