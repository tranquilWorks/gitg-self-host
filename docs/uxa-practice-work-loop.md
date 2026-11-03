# UXA-06 + UXA-07 — practice selection and work loop

Owner scope is issues #120 and #121 only, after verified PR #127 merge
`2f5f9f9ac98f6bd3eb4a255ec497fa00ff1f7cf0`. Weekly redesign, closeout redesign
and integrated UXA-10 acceptance remain separate; no #122–124 implementation.

## Entry points and identity

`/practices/` keeps the existing search, area filter and 12-item pagination.
It highlights the owner-scoped active/paused attempt before suggestions. The
same protocol's browsing card opens that attempt; its old recommendation URL
redirects to the attempt instead of presenting another setup. The guide links
back to that attempt. Other practices remain clearly separate future choices.
Home's existing display filter is reused, not a new ranking algorithm. Completed
work appears as completed, not current; suggestions are recomputed by the
unchanged ranking service and may legitimately include another attempt at the
same practice. No random reranking, hidden omission or inferred context.

Cards name the selected area and source of the suggestion. Explicit Skip for
now uses the existing CSRF-protected, owner/epoch/revision-guarded append-only
user-choice deferral; it neither marks N/A nor changes score state.

## Timing and immutable content

The UI now proposes a **seven-day planning checkpoint**, not a new completion
deadline. The old display date derived from protocol duration is no longer
presented as a deadline. Canonical 10/14-day durations, action-specific intervals,
completion conditions, historical attempts and evidence/replay remain unchanged.
The first week can end before all required intervals have elapsed; users must
still follow those instructions. No timer or automatic completion is introduced.
This is a presentation default, not authorization to rewrite canonical timing.

Action text is segmented only at explicit author-supplied Observation checks,
Examples and Final review labels. Reflection is visually distinct but remains
part of the same required action; no action, check or completion gate is moved
or removed. The known vague 26.13 action title gets a display-only direct title;
its stable ID, body, criteria and stored label stay exact. No generic content
rewrite, new practice version or corpus/source judgment is claimed.

## Guide, check-in and evidence

The selected protocol's existing verified instructional projection remains the
only guide source. One Resources and materials area links its resources; the
recursive Teaching and materials link is gone. Prompt/check/later-packet reveal
boundaries and text/Markdown downloads remain unchanged. No source is imported
from another practice, and no source-validity judgment is fabricated.

There is one check-in mode, with editable drafts and immutable submissions.
Display-only field/choice labels preserve exact values, validation, observation
rules and action scoping. Existing JavaScript and no-JavaScript recovery remain.
Submitted records show the actual action, direction, relevant observations and
notes, without empty inference/repetition cards or technical mass/algorithm UI.
False/zero typed results remain visible; legacy unchecked boxes say Not marked,
not an inferred negative observation. Mixed/contrary notes stay available.

Evidence remains verified by the existing read-only ledger and export services.
Its direction filter is a plain question, cards are readable action summaries,
and the minimized replay JSON is behind an explicit Account/Data disclosure.
It remains separate from optional assessment-research consent/export and the
complete private account archive. No backend evidence/audit information is
deleted or weakened.

## Acceptance boundary

Run complete repository, replay/golden, owner/epoch, stage/identity, browser and
backup/restore gates. Review retained exact-head desktop/mobile captures before
the owner-authorized guarded merge. Agent/software inspection is not owner,
participant, specialist, psychometric or assistive-technology validation.
