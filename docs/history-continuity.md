# History and reassessment continuity

M6L-05 adds owner-only history and explicit selected reuse over unchanged
assessment, Personal OS, context, weekly and practice contracts. No migration.

## History

History is available in primary navigation. Assessment periods paginate by ten;
each period paginates practices and weekly plan revisions independently by twelve.
Dates, assessment source/version, original practice status and weekly revision
provenance remain visible. Demonstration periods are labeled. Periods display
the latest verified Personal OS and season/capacity values on demand, with their
revision and date. This is a record of each period, not a retrospective score
comparison or a claim that completion established mastery.

Historical weekly detail is GET-only. It verifies owner, assessment ownership,
the complete plan revision chain, canonical hashes and actual evidence replay.
Saved reviews retain their original proof cutoff; unreviewed revisions show only
eligible proof from their original window. No review choice can mutate a practice
from the historical page. Current-period review/replan/calendar services retain
their latest-assessment checks. Invalid snapshots fail closed without private text.

## Reassessment and older practices

Before starting an assessment, the page explains that a new saved assessment
creates a new baseline and completion-coverage period. Existing evidence and
credit stay with their original period. An identical assessment can return its
existing record under the unchanged assessment persistence contract. Current
active/paused practices are named, with a link to review them before proceeding.

An older practice is not reassigned or stopped automatically. Its page identifies
its original period and links back to that history. Its original check-in,
resume/stop and closeout services still apply. A paused practice with sufficient
existing evidence can now reach its existing closeout page directly; otherwise
resume before adding evidence. Closeout credit remains in the original period.
The owner must complete or stop a current practice before starting another.
New weekly planning continues to reject an older-period practice.

## Selected intention reuse

History, Profile and Personal OS expose an optional review-and-reuse flow. The
owner chooses an earlier period, with no items preselected. Eligible items are
provided mission, principles, anti-goals, twelve-month direction, priorities,
season and capacity. Unknown, not-applicable and deferred source fields are not
copy candidates. Audit observations, practice-fit decisions, deferrals, direction
connections, weekly plans, evidence, baseline data, consent and scores are not
copied. Review those current-period choices through their existing workflows.

The first POST produces a preview of exact earlier values and the current values
that they would replace; it writes nothing. A separate confirmation appends normal
current-period Personal OS/context revisions. Unselected current fields, including
audit observations and intentional unknown/deferred states, remain unchanged.
Capacity/season use the existing context-fit rules and can affect contextual
recommendations when the owner confirms them. Free prose is never interpreted.

The confirmation is signed, owner/source/target bound and valid for 20 minutes.
It contains selected field identifiers and revision/hash expectations, not authored
text. Confirmation locks the owner's assessment rows, re-verifies both chains and
latest assessment, and rejects stale source/target/new-assessment state. Combined
Personal OS/context writes are atomic. Replays after a changed revision are
rejected; an unchanged-content save retains existing service idempotence.

Source provenance is presented during review. Confirmed values become ordinary
current-period revisions under the original contracts; no persistent cross-period
copy receipt or new relationship is introduced. Earlier records remain intact.
All new routes require authentication, owner filtering and private no-cache
responses. No remote service, analytics or automatic transfer is added.

## Rollback and evidence boundary

Revert the additive history/reuse service, routes, forms and presentation. No data
migration or restore is required. Already confirmed revisions remain valid
ordinary Personal OS/context records. Existing practice transitions and immutable
history keep their original semantics. Validation uses synthetic software/browser
fixtures, not participant, specialist or longitudinal-effectiveness evidence.
