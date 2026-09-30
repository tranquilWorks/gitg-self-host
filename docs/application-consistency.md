# Application consistency and accessibility follow-up

M6L-06 covers ordinary application presentation. Canonical competency content,
assessment mathematics, historical scoring and lifecycle services are unchanged.
No migration or new dependency. The frozen lesson renderer and original app CSS
remain byte-identical; shared application improvements use separate assets.

## Navigation and recovery

Home, Personal OS, Weekly, Practices, History and Profile remain primary links.
Assessment, Evidence, Account, Feedback and sign-out live in a native More
disclosure. Its label names the current secondary section. It works without
JavaScript; with scripting, Escape closes it and returns focus, and leaving the
menu closes the overlay. Current-section matching distinguishes Personal OS
practice-context pages from practice pages. The header scrolls with the page so
it cannot obscure a focused field at narrow widths or increased text size.

HTML validation/conflict/export-error responses keep their HTTP status and show
safe links to a fresh GET page and Home. The links never resubmit the failed
POST. Messages contain reviewed text, not exception details, request paths or
submitted private values. Error responses are private and non-cacheable.
400/403/404/500 and CSRF failures get usable recovery; the 500 page renders without
request/session/database context. Assessment CSRF failures retain a JSON error;
successful archives, calibration/evidence/feedback exports and calendars retain
their existing formats, content and authorization.

Forms share a server-rendered error summary with field links. Duplicate references
to the same form are deduplicated. Hidden-field and non-field errors have no dead
focus link. Inline Django errors and help text retain their actual description
IDs. Context, withdrawal and retention forms have distinct IDs. Invalid collapsed
Personal OS sections open even without JavaScript; shared scripting reveals error
sections and focuses the summary, then the selected control. Existing contextual
forms continue to expose fields with errors.

## Assessment interaction

Each answer exposes its selected state with `aria-pressed` and a visible check.
The current question has a focusable heading; changing questions or stages moves
focus to the new content. Count and save-status updates have status semantics.
Tab and native button Enter/Space activation remain available. Native Enter on an
answer selects it without also advancing. Optional character shortcuts start off,
operate only inside the focused question, and ignore editable controls, modifier
combinations and composition. Answers, timing capture, score calculations, local
storage, imports and save payloads use their unchanged code paths. With scripting disabled,
a visible notice explains the assessment requirement and which other pages remain
usable.

## Copy and screen inventory

| Surface / templates | Audit disposition |
| --- | --- |
| `base`, shared navigation, form errors, recovery, `500`; registration login/password form/done | Consistent navigation and recovery, one main landmark, preserved skip link; form errors and focus share one implementation. Login/password boundaries and server validation retained. |
| Home, practice list, practice card | Retained concise suggestions and discovery; removed “protocol defined”/placeholder language. Explicit demonstration labeling and no-assessment recovery remain. |
| Assessment | Clear question focus, selection and opt-in shortcuts; result copy describes the saved profile instead of a database report. Reassessment, save/import failure alerts and share-code privacy remain. |
| Personal OS, direction review, practice direction, saved context review, practice context | Response labels use ordinary language. Preserved unknown/N-A/defer choices, conflict checks and source provenance. Error descriptions, duplicate IDs, collapsed-error visibility and navigation ownership repaired. |
| Practice recommendation, setup, setup-form partial, sprint | “Practice” consistently names the user activity. Removed duplicated timing wording. Historical scoring language explains retained rules; active status pill cannot collapse into a narrow circle. |
| Practice check-in, submitted detail, review, completion | Permanent records, explicit final-review credit and earlier scoring rules explained plainly. Error/help associations repaired; detailed evidence calculations remain under Technical audit details. Completion remains separate from mastery. |
| Practice guide and instructional-link partial | Reviewed navigation/keyboard/reflow integration. Their source and authored content remain frozen. Existing teaching/check separation and readable table overflow retained. |
| Weekly execution, plan detail, replan, transition; proof/next-step/direction partials | Preserved explicit planning and pause/stop confirmations. Added missing replan help targets and HTML conflict recovery. Original proof dates/cutoffs and no planning credit remain explicit. |
| History, period, plan, reuse | Retained owner-only reading, original provenance, optional unchecked reuse and exact confirmation. Invalid selections join shared error recovery. Earlier evidence/credit never moves periods. |
| Profile | Completion credit and coverage labels simplified; allocation details remain available in a disclosure. Saved assessment, personal applicability, earlier records and mastery boundaries retained. |
| Evidence ledger, audit error | Plain explanation of earlier records and a minimized export label. Existing event-level audit details and recovery remain available; successful export contract unchanged. |
| Account/data | Privacy and destructive-action consequences preserved. Backend policy IDs moved to a secondary disclosure; concurrent consent/withdrawal and optional cleanup forms have distinct IDs. No new data operation. |
| Feedback | Timing/privacy statement now applies specifically to the feedback form, avoiding a false application-wide claim (the assessment already records item timing). Back to account now opens Account data. Submitted-record semantics retained. |

## Verification boundary and guidance

The browser audit checks 23 route entries at 320, 390 and 1280 CSS pixels,
visible field labels/descriptions, unique IDs, one main heading, current navigation,
200% text sizing, reduced motion, keyboard interaction and non-JavaScript recovery.
Conditional forms and existing end-to-end journeys supplement the ordinary-page
matrix. A setup URL reached with an active practice correctly returns to that
practice; the existing lifecycle journey exercises actual setup steps.

Shared palette inspection gives these contrast ratios: body text/paper 14.13:1,
secondary text/paper 5.82:1, accent/surface 7.36:1, control border/surface 3.73:1,
and error text/surface 8.16:1. This samples shared styles, not every possible state.

The checks draw on W3C guidance, retrieved 29 September 2026:
[reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html),
[form error notification](https://www.w3.org/WAI/tutorials/forms/notifications/),
and [character shortcuts](https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts).
320 CSS pixels tests the narrow reflow equivalent described by W3C; increased text
size is checked separately. These are software/browser checks and visual review,
not a WCAG conformance certificate or actual screen-reader, switch, speech-input,
low-vision participant, cross-browser or specialist acceptance. Real assistive
technology and participant evidence belongs in Batch 08.

Rollback removes these additive presentation helpers/assets and restores the
previous templates, forms' presentation attributes and error routing. No records
need deletion, migration or restoration. Exact results and limitations are in the
[Batch 6 evidence](evidence/M6L-06-APPLICATION-CONSISTENCY-20260929.md).
