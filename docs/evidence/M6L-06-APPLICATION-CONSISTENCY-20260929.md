# M6L-06 — Application consistency

Owner request: “nexst batch” after M6L-05. Baseline:
`a51b1214f91e5dc4756aebc1e57aca99e48503b4`. Branch:
`codex/m6l-06-application-consistency`. Implementation, verification and stacked
draft PR only; no merge, publication or live-data action.

## Acceptance and implementation

- **06-01 copy audit:** ordinary copy now describes practices, permanent records,
  final-review credit and earlier scoring rules. Secondary policy/calculation
  diagnostics remain available. Feedback timing/privacy claims are properly
  scoped. [Screen inventory and behavior](../application-consistency.md).
- **06-02 navigation/recovery:** six primary destinations and native More
  disclosure; correct current section; shared private HTML recovery preserving
  status, JSON assessment errors and successful download contracts. No exception
  details, private POST data or mutation links on recovery screens.
- **06-03 accessibility/layout:** server-rendered linked errors, help/error IDs,
  distinct form IDs, expanded invalid sections, focus handling, assessment pressed
  state and scoped opt-in shortcuts, stronger control boundaries, reduced motion,
  narrow reflow and text resizing. No scoring or lifecycle service changes.

## Verification in progress

- Focused regression: 43 passed (`/tmp/m6l06-focused.xml`, 176.03 seconds).
- Initial new browser coverage: five passed (`/tmp/m6l06-browser.xml`, 82.59 seconds):
  23 route entries at each of 320/390/1280px, text resizing/reduced motion,
  keyboard assessment/form recovery and non-JavaScript navigation/password errors.
- The conditional-form test initially failed on an exact label selector that
  omitted Django's trailing colon; repaired the selector. Its page exposed both
  expected consent controls. An additional expected weekly heading was corrected
  before rerun; neither required a product behavior change.
- The first complete-browser attempt stopped after eight passes at an old Personal
  OS label selector; updated it to the new label. The next attempt exposed a text
  locator that did not match the visible `<noscript>` message. An explicit element
  selector passed in the dedicated no-JavaScript rerun (`/tmp/m6l06-noscript.xml`,
  one passed). These selector corrections preserve the intended journey checks.
- Draft [PR #110](https://github.com/tranquilWorks/gitg-self-host/pull/110) is stacked
  on #109. Implementation commit `dc2e9e2`; hosted CI is in progress.
- The initial full regression stopped at one obsolete plaintext export-error
  assertion after 112 passes (`/tmp/m6l06-full-initial.xml`). Updated the evidence
  and feedback export assertions for HTML recovery, keeping privacy/status checks
  and adding safe-link/no-cache/no-attachment checks; both focused cases passed
  (`/tmp/m6l06-error-contract.xml`). Updated the profile-copy expectation while
  preserving all scoring/baseline invariants. The complete profile is rerunning.
- Final full browser suite and nonbrowser/full readiness profile are pending.
  `make compose-smoke` passed (`/tmp/m6l06-compose.log`, exit zero), including
  fresh isolated deployment, mapped-port health/authentication, idempotent seed,
  saved synthetic context, recreation, backup/restore, all applicable replay and
  readiness contracts, and clean shutdown. Image construction preceded the final
  no-JavaScript notice copy; the final notice is covered by browser verification.
  Browser regression also found two prior assumptions affected
  by shared summaries: immediate invalid-field focus, and a globally unique error
  message. Updated the context journey to follow the summary link, and the account
  deletion journey to select the exact inline error and verify summary focus. Its
  wrong-confirmation account-preservation assertion remains in place; keyboard
  entry is checked on a fresh GET. Receipts: `/tmp/m6l06-all-browser-focus.xml`
  (eight passes, one failure), `/tmp/m6l06-all-browser-deletion.xml` (ten passes,
  one failure). Full browser coverage is rerunning.
- A subsequent full regression stopped after 216 passes at a feedback assertion
  that counted four error messages across the whole document. Shared summaries
  intentionally duplicate inline messages. The replacement checks the exact four
  form errors, their inline IDs and summary links, preserving rejection/no-write
  and valid-submission assertions. An existing practice browser selector similarly
  now targets its inline action-attempt error. Receipts:
  `/tmp/m6l06-full-summary.xml`, `/tmp/m6l06-all-browser-attempt.xml` (12 passes,
  one failure). Both complete suites rerun without first-failure interruption.
- Inspected final narrow Home, conflict recovery, conditional consent, linked
  form-error and 200% text screenshots, alongside the initial desktop assessment
  screenshot. The active badge, navigation, recovery links and form content remain
  readable. Screenshots are retained under `test-results/pilot-walkthrough/`
  with the `consistency-` prefix (synthetic data only).

Shared-form inspection also repaired duplicate hidden/context and optional
withdrawal/cleanup IDs, missing replan help targets and the closed invalid audit
section without JavaScript. New assets keep protected renderer inputs intact.

## Invariants and limits

No migration, model, canonical content, scoring mathematics, historical service,
consent or lifecycle semantics change. 383 practices / 1,151 actions remain intact.
Content hash `ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`;
legacy projection `9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.
No fingerprints or required gates are weakened.

Browser semantics, layout and keyboard checks do not establish actual
assistive-technology usability, universal accessibility or WCAG certification.
No participant evidence, specialist acceptance or empirical axis is closed.
After Batch 6, **two batches / seven actions** remain: 07 operator convenience
(three actions), and 08 empirical product validation (four actions).
