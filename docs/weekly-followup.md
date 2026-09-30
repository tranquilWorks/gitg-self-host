# Recurring weekly execution

M6L-04 adds explicit follow-up over the unchanged weekly execution v1 plan and
review contracts. No schema, evidence, scoring or ranking rule changes.

The Weekly page carries forward the latest prior **planned** week in the current
assessment period, including its original date, submitted proof, saved adjustment
and next-step choice. It shows how many weeks ago that plan was made; gaps are not
fabricated as failed weeks. No submitted proof is distinct from contradictory or
adverse evidence. A saved review retains its original submission cutoff.

The plan page makes each review choice actionable:

- Continue: open the action guide or deliberately plan the same action again.
- Next action: preview the next action in sequence and choose a day. If there is
  no next action, the user must choose explicitly; nothing is automatically saved.
- Pause: a separate confirmation pauses the active practice; it can be resumed
  from the practice page.
- Different practice: a separate confirmation stops this attempt, preserving its
  records, then opens practice choices. Starting a replacement is still explicit.

Adjustment guidance points to timing, allowed scope/support, practice fit or
season/capacity. It never rewrites protocol instructions or evidence requirements.
Saving a review alone changes no practice status. A superseded review cannot pause
or stop the current practice. Transitions use the existing lifecycle service.

Replanning uses a deliberate GET preview followed by POST into the current week.
It keeps the original plan and review, appending a revision if the action or date
changes. Earlier revisions remain readable from the plan page. A repeated,
unchanged save uses the existing idempotent contract. Hidden revision, assessment,
sprint, status and week fields are checked against current state; stale forms
cannot overwrite a newer plan or act on a replaced practice. New browser plans
must use today or a later day in the current week. Historical service/replay
contracts still accept their original historical inputs.

## Optional calendar entry

An authenticated download creates an all-day `.ics` event for the current upcoming
plan. It contains a fixed generic label, date, pseudorandom-looking deterministic
UID derived from the plan UUID, creation timestamp, PRIVATE classification and
TRANSPARENT availability. It includes no user identifier, private narrative,
action title, evidence, scores, URL, attendee or alarm. It sends nothing remotely.
Calendar applications may apply their own default alerts. Users disable those
entries by deleting them in their calendar. Replanning does not synchronize or
cancel a downloaded event: remove the old entry and import the new one.

The serializer follows [RFC 5545](https://www.rfc-editor.org/rfc/rfc5545.html),
sections 3.1 and 3.6.1: CRLF lines, bounded ASCII content, UID/DTSTAMP, DATE start
and exclusive next-day DATE end. The response disables caching. Expired,
superseded, cross-owner, old-assessment or inactive-practice downloads fail closed.
Tests cover the file contract and browser download; importing into individual
calendar vendors has not been validated.

## Privacy, verification and rollback

Every new route requires authentication and owner lookup. Plan chains, review
hashes and actual submitted proof are replayed before display or action. No
reflection or plan itself creates evidence, completion credit or a score change.
No automatic reminders, analytics, background service or remote calendar API is
introduced. Auxiliary routes live in the project URL configuration to preserve
the frozen historical guide route fingerprint.

Revert the new views, forms, service, routes and templates to undo this feature.
There is no migration. Appended plans/reviews remain valid under the existing
contract. Explicit pause/stop actions retain their existing lifecycle semantics;
imported calendar entries must be removed by the owner in their calendar.
Cross-assessment continuity belongs to M6L-05.
