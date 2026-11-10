# UXA-10 — integrated acceptance boundary

Issue #124, parent #114. Owner's 10 November 2026 request authorizes the
remaining sequence. This is the last UXA slice, separately integrated after
UXA-08/09 (#129), not a new product or scoring milestone.

| Pass | Real browser actions | Authoritative assertions |
| --- | --- | --- |
| 0: fresh | Create ordinary account, sign in, follow assessment path, visit guarded roots | No seeded assessment or staff privileges; downstream partial states redirected |
| 1: assessed | Answer all 50 questions/automatic follow-ups with opt-in keys; mouse/keyboard help and Share; cancel Retake | One application assessment, eight capability follow-ups, exact share code, no premature closeout/empty Weekly review |
| 2: active | Save direction through nine-question form; seven setup steps; same attempt from Home/browser/guide; plan; invalid input, draft, recovery, two submissions; export and review | Same assessment/protocol/attempt; no invalid/draft evidence; exact replay/export, private context excluded, no premature credit |
| 3: completed | Real GUI final review for 75% credit; Home/Weekly/Profile/browser | One completed attempt, not current; retained direction/recomputed suggestions; unchanged assessment/evidence and frozen Weekly proof |

The continuous case runs at 390/1280 CSS pixels. It seeds only canonical global
content before any account exists. It does not persist an assessment shortcut,
fabricate completion, or post setup/check-ins through a test HTTP client.
Existing independent tests remain; this layer does not replace them.

## Integration repair and accessibility

An assessed owner without a practice still saw an empty Weekly review section.
Render it only with an actionable plan form, unreviewed plan or saved current
review. Next-practice/direction and independent historical-plan navigation stay.
No query, service, stored record, proof cutoff or completion gate changes.

Each capture checks one main heading, labelled visible controls, valid description
targets, unique IDs and reflow. Orientation/archetype native help opens by mouse
and keyboard; Escape restores focus. Share/Retake and disabled closeout have
explicit focus/help checks. Existing no-JavaScript cases remain; the new actual
assessment uses JavaScript and is not a new no-JavaScript browser receipt.

Preserve genuine safety/completion-not-mastery information, while excluding
technical audit labels from ordinary UI. Seven days is a planning checkpoint,
not a canonical deadline. Written direction is not an opaque scoring input.
Suggestions match existing recommendation order; partial credit does not ban a
protocol from future suggestions. Frozen assessment/golden checks stay exact.

## Retained images and merge boundary

Inspect `uxa-integrated-{state}-{390,1280}.png`, all 16 states (32 PNGs): fresh,
help, archetype, share, assessed, gate, active, planned, error, evidence, review,
complete, completed-home, completed-weekly, completed-profile, completed-browser.
Also inspect representative existing assessment, Personal OS, guide/typed check-in,
Weekly and Account/privacy captures.

Require final-head full quality/pytest/all readiness, every browser case, Docker
backup/restore and aggregate Pilot readiness. Verify artifact provenance and ZIP
SHA256; inspect actual images/logs, reviews and head/main/integrated candidate.
Only exact-head normal merge; no permissions/settings changes or rule bypass.
Local browser/Docker restrictions are not worked around or relabelled as passes.

Software and agent image checks are not owner/participant, specialist,
assistive-technology, source or psychometric validation. Evidence axes/human
acceptance counts remain unchanged. No deployment.
