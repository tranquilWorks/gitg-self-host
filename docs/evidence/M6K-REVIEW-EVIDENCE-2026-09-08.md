# M6K-01-02 — current-revision review enforcement

Base: merged PR #67, `1a5ca67364a5a3025d32d17a0ebffb58688f4875`.

Implemented strict source-only ledger, receipt/evidence and scope-plan schemas;
per-entry canonical/scope/instruction/material/renderer/runtime fingerprints;
ordered, hash-linked receipt history with pinned Git base checks; and a current
383-row report with independent review dimensions. Actual runtime compiler
selection remains 91 tailored / 292 rewrite-pending. All seven formal review
counts remain zero and the production receipt ledger is empty.

Negative fixtures exercise QA-01 missing materials/examples, QA-02 answer leakage,
QA-05 maintainer syntax, duplicate IDs, stale artifacts, invalid dependencies,
blanket pass records, unresolved blockers, misleading live claims, unexecuted
verification, falsely full-scope defaults, self-reviewed cold starts, hidden
rationale, stale downstream integration and rewritten receipt history.
The tests create only synthetic records in temporary repositories.

Executed at the initial publication checkpoint:

- First review-enforcement test run: 41 passed in 47.64 seconds. Additional
  execution-state and downstream invalidation cases were then added; the final
  expanded test run is tracked separately below.
- `reviews.py check --base 1a5ca67364a5a3025d32d17a0ebffb58688f4875
  --output docs/authoring/quality/current-report.json`: exit 0, including exact
  protected recovery baseline verification.
- Ruff formatting/lint and the repository contract phase: passed, including
  environment, MANIFEST, Django checks and zero migration drift.
- Expanded focused tests, the full 521-test non-browser suite, isolated
  pilot/curriculum/competency-evidence readiness and catalog checks are running
  at this checkpoint. They are not yet claimed passed.

Local browser installation failed with Playwright's browser-directory lock
update error. No local browser execution or screenshot review is claimed.
Docker is unavailable, so Compose is not locally verified. PR #67's final
instructional workflow was still reported in progress by the connector when
checked; its merge does not supply missing screenshot evidence.

No canonical content, source exercise, activation, scored action, score logic,
model, migration, dependency or CI workflow was changed. No actual learner,
qualified reviewer or owner decision was created. Automated checks cannot
certify semantic depth, completeness of a declared facet inventory, independent
private knowledge, human identity or intervention effectiveness. Source-only
implementation is distinct from final hosted verification and milestone acceptance.
M6K-01-03 and formal repair/A/B/C work remain subsequent actions.
