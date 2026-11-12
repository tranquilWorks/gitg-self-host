# UXA software closeout and human-test handoff

Owner requested final software/administrative closeout on 12 November 2026.
All ten UXA implementation slices are merged. This document reconciles the
tracking record; it adds no runtime capability and grants no deployment approval.
The remaining owner verification and next test wave are tracked in
[issue #131](https://github.com/tranquilWorks/gitg-self-host/issues/131), open
and unaccepted. Administrative issue closure is not human acceptance.

## Verified implementation ledger

| UXA | Issues | Merged implementation PR | Merge commit |
| --- | --- | --- | --- |
| 01 | #115 | #125 | bc55fe6ef9a8f4b94b26052096a9e320b0791e0c |
| 02–03 | #116, #117 | #126 | 98b8bc6e74e37c0472ff37b8f1dcb3baa89c0a3b |
| 04–05 | #118, #119 | #127 | 2f5f9f9ac98f6bd3eb4a255ec497fa00ff1f7cf0 |
| 06–07 | #120, #121 | #128 | d68708e3fa759a91b95363de975342165c612671 |
| 08–09 | #122, #123 | #129 | 23395d40e224d3883ea86a4196651c13c49ee8e5 |
| 10 | #124 | #130 | b36adaddb46222f27d43cc505d774f610915b199 |

Fresh GitHub reads confirmed every merge above and main unchanged at the last
entry. Final application tree: `0b041a5dddbe3d7ae591b96b7bb28ff98c5fb85b`.
Parent #114 is the software implementation umbrella. Child checkboxes record
implemented/software-covered dispositions, not owner judgments of clarity or
usability. Human findings can reopen a child or create a linked bounded repair.
The original owner-feedback document remains unchanged.

## Final integrated application evidence

[PR #130](https://github.com/tranquilWorks/gitg-self-host/pull/130) and its
merge receipt comment6775694553 retain the final software evidence:

- Exact head `81803f3ba52b1318559aee1bff730f8148bb556c`,
  run [42862784325](https://github.com/tranquilWorks/gitg-self-host/actions/runs/42862784325), attempt1.
- Full pytest: **2,070 passed, six retained DATABASES override warnings,
  1,082.98s**. Ruff/format2,063 Python files, manifest3,527, Django and all17
  readiness/catalog checks passed. No incomplete local run is promoted to a pass.
- Browser: **69 passed, 2,070 deselected, 773.02s**. Two continuous real
  ordinary-account-to-GUI-closeout journeys cover390/1280; no fabricated
  assessment or service-closeout shortcut substitutes for those UI stages.
- Compose and aggregate passed. Online backup/restored critical-state SHA256:
  `4a090b55831056566b8da12d80d8642f4d662d67a286ccd19b2588b0a115c226`;
  startup/login,29migrations,idempotent seed,replay,recreation/persistence,
  isolated restore and clean shutdown were verified.
- Artifact13785778551,65,941,233bytes; downloaded ZIP SHA256
  `4d5bfdb866e3c401b93fbf1bc9837aeba329303328866c259f7685e454f19f3d`
  matched metadata/upload log and exact run/head/branch provenance. All32new
  images plus6representative regressions were actually reviewed (38total).
  Retention is finite: do not assume an expired download is still available.
- Visual limits remain: tall Profile views paired with desktop legibility;
  fixed skip-link/full-page modal-backdrop capture artifacts; unusual but
  readable error-checkbox label alignment with successful recovery. No human
  or assistive-technology validation inferred from these software receipts.

## Deliberate dispositions, not unimplemented semantic changes

- Seven days is the **planning checkpoint**, not a new completion deadline.
  Canonical10/14day durations, action intervals and historical records remain.
- Reflection is visually separate where authored labels support it but remains
  in the same required action; no completion requirement was removed.
- Personal OS direction-history route remains because partial revision,
  conflict/expected-revision handling and history are not redundant with fillout.
- Direction free text is a planning reminder, not an analyzed/scored input.
  Suggestions retain existing scoring/context semantics; partial-credit
  practices may legitimately recur. Display filtering is not random reranking.
- Native disclosures supply keyboard help; no-JavaScript coverage is retained
  independently. The actual assessment browser journey uses JavaScript.
- Auth/owner/epoch, CSRF, immutable proof/evidence, replay, frozen assessment
  IDs/values/golden outputs, completion-not-mastery and human dignity remain.

## What is left

Run the open #131 checklist on an owner-selected exact revision and record
device/browser/date, stage, expected/actual behavior and severity. Re-test fresh,
assessed, active and completed states; question/copy comprehension; keyboard,
focus and reflow; same practice identity; draft/error recovery; Weekly proof;
explicit closeout; next-practice handoff; and privacy/data/operator distinctions.
Use synthetic accounts; never attach private share codes, archives or live data.
New findings need a separately bounded repair and another test cycle.

Owner flow/copy acceptance, source/content and specialist/privacy/safety reviews,
participant exposure/release approval, and empirical assessment validation are
**not passed** by this closeout. `ER-M6A-003` stays pending, `RG-M6A-002` open,
all eight empirical axes open/zero completed. No deployment performed/authorized.
This is UXA software closeout only, not a claim that the entire research/content
backlog is validated. No new feature batch starts here.
