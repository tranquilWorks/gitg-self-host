# UXA-10 implementation / verification receipt

## Final state — merged and main verified, 10 November 2026

PR #130 normally merged as `b36adaddb46222f27d43cc505d774f610915b199`.
Main matched reviewed tree `0b041a5dddbe3d7ae591b96b7bb28ff98c5fb85b` and
the expected baseline/head parents. Run42862784325 attempt1 on head81803f3
passed2,070pytest/six warnings1082.98s,69browser773.02s, all17readiness,
Compose and aggregate. Artifact13785778551 downloaded ZIP SHA256
`4d5bfdb866e3c401b93fbf1bc9837aeba329303328866c259f7685e454f19f3d`
matched metadata/upload log;32new+6regression PNGs actually reviewed.
Full final receipts/limits are in PR #130 and
[the software closeout ledger](UXA-SOFTWARE-CLOSEOUT.md).
Human/owner verification stays open in #131; nothing deployed or empirically
validated. The publication-time pending/local-limit notes below are historical,
not current blockers and never evidence of a clean local full-suite pass.

## Authorization and source boundary

Owner requested all remaining UXA work on 10 November 2026. #124 is last,
separately integrated after #129. Prework branch
`codex/uxa-10-integrated-acceptance` initially rested on #129 repaired head.
PR #129 is now normally merged as `23395d40e224d3883ea86a4196651c13c49ee8e5`;
main's tree was verified as `8cf11d33dd79e451615032f6733e8d246f333546` with
the expected parents. This branch was rebased onto that exact merge before
publication; the application/test tree is unchanged from the prework checks.
Its contract baseline and dependency receipt now name that actual merged main.

PR #129 final run42850562829 passed 2,066 pytest/six warnings in2,018.96s,
67 browser cases in597.74s, all readiness/Compose/aggregate; artifact13781750737
ZIP SHA25676500dc3d7f43bee92d354019dde1cf2984068f17785d1e0a97a04d545a2093a
verified and30PNG inspected. Those are dependency receipts, not UXA-10 passes.

## Implemented / actual checks

- Continuous ordinary registration, actual assessment/follow-ups, saved direction,
  GUI setup, same-attempt routes, invalid/draft/submitted check-ins, exact evidence
  export/replay, frozen Weekly review, GUI closeout and completed-state handoff.
- Mobile/desktop semantics/reflow, help/modal keyboard/focus, visible closeout
  requirements and unchanged records asserted. No protected semantics changed.
- Hide the observed empty Weekly review before a practice/plan. Active and
  historical meaningful review entry remains available.
- Four request tests **passed in 26.68s**. Initial development: one pass/three
  failures in28.10s due to incorrect test ORM paths to event owners. Corrected
  queries use assessment or check-in/sprint ownership; no schema/guard weakening.
  Counts overlap, not additive. Ruff format/lint of both new Python files passed.
- Overlapping final focused stage/Weekly/entry/Profile/assessment integration
  suite: **33 passed in 131.34s**. Browser registration selectors subsequently
  aligned to actual colon-labelled Django signup fields before publication.
- Contract passed: **3,527 manifest entries, 2,063 formatted Python files**,
  whole-repo Ruff and Django/no migration drift. Two new browser cases collected,
  not executed. Full harness still required.
- Browser code is not execution evidence. Local launch is permission-blocked,
  Docker absent; no installation/escalation/workaround. Hosted CI still executes
  legitimately, so require final-head hosted evidence while available.

Read docs/uxa-integrated-acceptance.md for all32 required retained images and
merge conditions. Record subsequent actual run/head/tree/artifact/digest/counts
and merge receipts in PR metadata after source freeze, not evidence-only pushes.
The full local harness started on frozen prework commit a50611d, before the
dependency metadata-only rebase. It remains incomplete at publication; no clean
full local pass is claimed. Require fresh final-head hosted full verification.
No UXA-10 full-suite/browser/Docker pass, human acceptance or deployment claimed.
