# M6L-06 — Application consistency

Owner request: “nexst batch” after M6L-05. Baseline:
`a51b1214f91e5dc4756aebc1e57aca99e48503b4`. Branch:
`codex/m6l-06-application-consistency`. Implementation, verification and stacked
[draft PR #110](https://github.com/tranquilWorks/gitg-self-host/pull/110) only;
no merge, publication or live-data action.

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

Shared-form inspection repaired duplicate hidden/context and optional
withdrawal/cleanup IDs, missing replan help targets and the closed invalid audit
section without JavaScript. New assets keep protected renderer inputs intact.

## Verification

| Check | Actual result |
| --- | --- |
| Nonbrowser regression | All 1,986 cases have passing coverage: 1,985 passed in the complete run (1,195.39 seconds), one corrected assertion passed in its exact-case rerun (12.88 seconds). |
| Complete browser suite | All 52 cases have passing coverage: 51 passed in the complete run (651.23 seconds), one corrected assessment-counter assertion passed in its complete assessment/save journey rerun (23.23 seconds). |
| Full readiness commands | All 17 exact commands from `contracts/verification.commands` passed in contract order, exit zero, including pilot/curriculum/evidence, scoring, calibration, context, weekly and operations readiness. |
| Docker Compose | `make compose-smoke` passed, exit zero: isolated deployment, mapped-port health/authentication, idempotent seed, synthetic saved context, recreation, backup/restore, all applicable replay/readiness contracts and clean shutdown. |
| Contract and scope | Contract schema and all 61 changed paths passed; no forbidden paths. Manifest has 3,467 entries. Ruff formatting/lint, Django check, no-migration check and whitespace check passed. Final code contract log: `docs/evidence/local/verify-contract-20260929T232258Z.log`; documentation-only refresh rechecked manifest/schema/scope. |
| Visual inspection | Narrow Home, conflict recovery, conditional consent, linked form errors, 200% text and desktop assessment screenshots inspected. Badge, navigation, recovery links and form content remain readable. |

The required cumulative command was:
`PYTEST_ADDOPTS='-n 4 --dist=load --maxschedchunk=1 --output=/tmp/m6l06-full-artifacts --junitxml=/tmp/m6l06-full.xml' ./scripts/agent-verify.sh full`.
Its nonzero exit records the obsolete assertion; it is not represented as a clean
full-harness pass. The exact 17 remaining `scope:full` commands were replayed in
contract order by `/tmp/m6l06-readiness.py`. No gate is removed or weakened.

Browser command:
`PLAYWRIGHT_BROWSERS_PATH="$PWD/.playwright-browsers" .venv/bin/pytest tests/e2e -q --output=/tmp/m6l06-all-browser-artifacts --junitxml=/tmp/m6l06-all-browser.xml`.
Coverage includes 23 route entries at each of 320/390/1280px, enlarged text and
reduced motion, keyboard assessment/form recovery, no-JavaScript navigation and
validation, conditional consent/reuse, conflict recovery, and all existing journeys.
The actual setup sequence and complete assessment/clarifier/canonical-save journey
remain exercised. XML node identities were compared: each failed broad-run case
matches its passing rerun exactly; neither broad suite skipped cases.

Receipts: `/tmp/m6l06-full.xml`, `/tmp/m6l06-feedback-summary-fixed.xml`,
`/tmp/m6l06-all-browser.xml`, `/tmp/m6l06-assessment-browser.xml`,
`/tmp/m6l06-readiness.log`, `/tmp/m6l06-compose.log`. Focused regression also
passed 43 cases (`/tmp/m6l06-focused.xml`) and two export-error contract cases
(`/tmp/m6l06-error-contract.xml`). Screenshots remain under
`test-results/pilot-walkthrough/consistency-*.png`, with synthetic data only.
Docker image construction preceded the final no-JavaScript notice copy; the final
notice passed dedicated and complete browser coverage.

## Verification corrections

Earlier attempts exposed old Personal OS labels, the assessment counter label,
a `<noscript>` text locator, exact labels missing Django's colon, immediate-field
focus assumptions, and message uniqueness assumptions invalidated by the new
summary. Tests now select the exact field/inline error and verify summary-to-field
focus. Wrong-confirmation account preservation, attempted-action rejection,
feedback no-write/valid-submission behavior and canonical assessment outputs remain
checked. The feedback assertion was additionally corrected to include the full
existing two-sentence validation message. No product validation rule changed.

Export-error assertions now expect HTML recovery while retaining status/privacy
checks and adding safe GET links, no-cache and no-attachment checks. Profile-copy
assertions changed without removing scoring/baseline invariants. Initial interrupted
receipts are retained as `/tmp/m6l06-full-initial.xml`,
`/tmp/m6l06-full-summary.xml`, and `/tmp/m6l06-all-browser-*.xml`.

## Invariants and limits

No migration, model, canonical content, scoring mathematics, historical service,
consent or lifecycle semantics change. 383 practices / 1,151 actions remain intact.
Content hash `ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a`;
legacy projection `9eff5558607936aab20ec2adcdf4912510e9f8816cc291ae6b77918bf6711672`.
No fingerprints or required gates are weakened.

Browser semantics, layout and keyboard checks do not establish actual
assistive-technology usability, universal accessibility or WCAG certification.
No participant evidence, specialist acceptance or empirical axis is closed.
Final head `7078f9723d500d3f18eac78fcfc9df5163a21180` passed hosted quality,
browser, Compose and aggregate Pilot readiness in
[run 36646170643](https://github.com/tranquilWorks/gitg-self-host/actions/runs/36646170643).
Publication was skipped; PR #110 remains draft, stacked on #109, unmerged/unpublished.
After Batch 6, **two batches / seven actions** remain: 07 operator convenience
(three actions), and 08 empirical product validation (four actions).
