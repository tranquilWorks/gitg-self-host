# M6K prepared repairs

These are three source drafts reconstructed from the owner's execution ZIP.
They are grouped because each addresses instructional integrity: absent inputs,
answer leakage, or maintainer commentary in learner copy. They are not selected
for runtime compilation and do not clear formal M6K-02 or A/B/C acceptance.

| Competency | Prepared change | Inspect |
|---|---|---|
| 21.03 Foundational craft competence | Three fictional briefs, fixed accuracy/access criteria, matching keys and a fresh contact-change retest | [Guide](21.03/learning-guide.md), [briefs](21.03/event-briefs.json), [synthetic checks](21.03/desk-test.json) |
| 10.01 Learning methods | Six definitions, two worked examples, separate first/second/delayed prompts and recomputed keys | [Guide](10.01/learning-guide.md), [delayed prompt](10.01/delayed-transfer-prompt.md), [separate check](10.01/delayed-transfer-check.md) |
| 10.02 Deliberate practice | Learner scope explains the skill, evidence limit and next decision; four actions stay exact | [Revision](10.02/revision-note.md), [compatibility](10.02/compatibility.md) |

Each folder contains the original entry, the revision note and exact before/
after source fingerprints. `draft-record.json` is provenance for prepared work,
not a production review receipt. M6K-01-02 must implement current-revision
evidence enforcement; the formal fixes and A/B/C then follow their declared
dependencies. The archived baseline ledger remains entirely pending.

The text/Markdown copies are generated from the same projection used by the
guide route. Prompt and check files are deliberately separate. An independent
cold-start run must receive only the selected learner-visible material and
prerequisites first; do not send this authoring directory with hidden checks
and author rationale as its first input. No independent C run, actual learner
session, qualified decision or professional credential is claimed here.

## Current-revision review enforcement

`ledger.json` now indexes immutable, per-competency receipts; it starts empty.
`current-report.json` derives seven independent dimensions from valid current
receipts and keeps draft mechanical findings visible. The implementation and
recording procedure are in [REVIEW_IMPLEMENTATION.md](../../plans/m6k/REVIEW_IMPLEMENTATION.md).
Existing `draft-record.json` files are provenance and are deliberately not imported
as acceptance. Run `reviews.py check` with the pinned PR base before publishing
new review records. No actual A/B/C or human pass has been recorded by this batch.
