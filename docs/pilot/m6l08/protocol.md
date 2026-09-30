# M6L-08 study protocol — version 1.0

## Questions and design

Evaluate whether intended users can connect an assessment, their chosen
direction and context, one practice, and a repeatable weekly review. Observe
fit, comprehension, burden, recovery after a missed plan, accessibility and
voluntary return. This is a formative product study, not an effectiveness trial
or assessment validation study. No developmental score is an outcome here.

Proposed first cohort: 8–12 consenting adults using the supported language,
with an entry session and three weekly cycles. This is an operational budget
for finding problems, not a powered sample or representative prevalence claim.
A qualified researcher must decide later sample sizes from the actual question,
expected variability, precision, missingness and analysis design.

Recruit beyond the owner and technically confident acquaintances. Seek varied
experience of planning tools, current time/capacity, mobile/desktop use,
keyboard/assistive-technology use and low-bandwidth conditions. Ask only about
access accommodations needed for the session; do not require diagnoses, sensitive
demographics, orientation/archetype or assessment results for recruitment.
Document recruitment channels and coverage gaps in a private coordinator record.
Do not infer subgroup fairness from this convenience sample. Participation must
not be tied to employment evaluation, access to care or product scores.

## Before any participant activity

Complete the private execution record in `review-and-corrections.md`: study
owner, contact, observers, qualified research/accessibility/privacy reviewers,
approved practice scope, exact source revision/image, CI/artifact review,
retention dates, recruitment wording, withdrawal method and protocol approval.
The existing `ER-M6A-003` review remains pending and `RG-M6A-002` remains open;
this kit does not bypass those participant-release requirements. Use the
[operator guide](../../operator-convenience.md) and existing
[private-pilot operations](../PRIVATE_PILOT_OPERATIONS.md) for operational checks.

Use personal mode and individual accounts. Explain the example status if someone
chooses a separate demonstration installation; exclude demo records from the real
study. Review the bounded practice choices for the proposed population before
launch. Do not assign crisis, clinical, legal or unsafe relationship exercises
as research tasks. Preserve all participant access aids and boundaries.

Rehearse every task with conspicuously synthetic accounts; those records remain
outside the participant dataset. Confirm login, private export inspection,
backup/restore, withdrawal and stop procedures. No screen/audio/video recording,
keystroke collection, automatic timing or remote telemetry is introduced.

## Entry session — cycle 0

Budget 30–45 minutes including disclosure and breaks; stop sooner when requested.
Obtain specific observation consent before notes. Assessment reuse has a separate
per-run in-app choice and can be declined without leaving the usability study.
Use neutral prompts, observe the first attempt, then offer assistance only when
requested or needed to avoid distress. Record prompted help, not an invented
unassisted success. Stop viewing the screen during private authored responses.

| Task ID | Prompt / observable outcome |
| --- | --- |
| `entry` | “Starting here, show me what you would do next.” Can the user find a personal start and distinguish an example assessment? |
| `assessment` | “Take or import your assessment if you want to; tell me when you want to pause.” Can they submit or deliberately leave? Never inspect answers/share codes. |
| `context_choice` | “Review whether this suggestion fits now; show what you would do if it does not.” Observe N/A, defer or distinct alternatives without dictating which to select. Ask whether the eventual suggestion fits. |
| `direction_link` | “If useful, connect this practice to a direction you choose.” Can they make or decline an explicit connection without the observer collecting their private text? |
| `start_practice` | “Choose a bounded next practice you would actually consider.” Can they understand its action and start, decline or stop without inventing instructions? Ask fit again. |

If assessment is skipped, dependent tasks may remain unobserved; do not force
completion or invent an assessment. Evaluate optionality, not compliance.

## Cycles 1, 2 and 3 — ordinary use plus optional check-ins

Each cycle is a seven-day product window, with one optional 10–15 minute contact
at the participant's agreed time. Do not require an action every day. A practice
may span windows. Keep notes about interface behavior only, never details of a
private real-world interaction. No contact without prior agreement; send no more
than one agreed reminder for a missed session and accept nonresponse.

| Task ID | Cycle | Prompt / observable outcome |
| --- | --- | --- |
| `check_in` | 1–3 | “If a real action happened and you want to record it, show how.” Otherwise retain a draft/skip; never submit fabricated evidence. Observe comprehension and participant-reported time band. |
| `weekly_review` | 1–3 | “Review this week and choose what happens next.” Can they distinguish proof, no evidence and completion from mastery? |
| `next_week` | 1–2 | “Plan the next week, or change/pause the plan to fit your capacity.” Observe continuity and missed-plan recovery without requesting an artificial failure. |
| `history` | 3 | “Find what happened earlier and decide whether anything is useful now.” Can they distinguish past records from the current week/assessment? |
| `exit` | 3 | “Show where you control your data or stop participating.” Explain feedback purge, assessment-consent withdrawal and account deletion as separate actions; do not delete data during a task without a deliberate owner request. |

Do not backfill missed sessions with assumed failure or success. A missing row
means not observed; it is not abandonment. `stopped` means a task started and the
participant chose to stop; `skipped` means it was offered and declined. Track
contact/non-return reasons only when volunteered, in the private coordinator
record. Report enrolled, reached, observed and unavailable denominators with
reasons/unknowns at closeout; the tool knows only currently consented participants
and their observation opportunities, not invitation or recruitment totals.

## Analysis planned before collection

Use descriptive counts and concrete interface defects. Separate assisted and
unassisted outcomes; never average ordinal categories into a score. Keep timing
bands as bands, without invented midpoints or imputed duration. Fit ratings are
participant judgments for observed recommendations, not efficacy or instrument
validity. A participant seen completing weekly review in at least two cycles is
an observed return, not a retention estimate. Publish no small-sample percentages.

Before interpreting an apparent improvement, inspect build changes, practice
selection, prompting, access conditions, missed contacts and self-selection.
Retain contradictions and negative/inconclusive observations. After changes,
start a versioned follow-up cohort and recheck the affected journey; do not pool
it with the original as though conditions were unchanged.

Pause immediately for withdrawal, distress, private-data exposure, broken
consent, unsafe guidance or a barrier that prevents meaningful participation.
Record only the minimum defect description, preserve the participant's choice,
and escalate to the assigned responsible reviewer. Do not reward completing a
research task at the expense of safety. Review severity before any further session.

## Source basis and limits

Reviewed 30 September 2026: [GOV.UK informed consent guidance](https://www.gov.uk/service-manual/user-research/getting-users-consent-for-research)
supports clear disclosure and ongoing choice. [W3C guidance on involving users](https://www.w3.org/WAI/test-evaluate/involving-users/)
supports including people with disabilities alongside conformance evaluation.
These inform the method; they do not certify this product, authorize a study, or
establish a jurisdiction-specific legal conclusion. The cadence and cohort size
above are this project's proposed feasibility choices.
