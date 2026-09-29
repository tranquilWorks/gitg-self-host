# Browser context selection policy 2.0

`GG-BROWSER-CONTEXT-SELECTION-2.0` is the M6L-02 presentation policy. It changes
which candidates appear in the browser, not assessment, scoring or context
priority mathematics. Owner request: implement the next planned batch after
M6L-01. Scope is the five actions in the M6L register.

- With no reviewed context, preserve the existing assessment/completion-based
  shortlist of at most three. Do not manufacture current-fit inputs.
- Verify current-owner/current-assessment context revisions before selection.
  If verification fails, show no personalized suggestions and explain recovery.
- Remove any latest explicit practice N/A or deferral from the fallback shortlist,
  including when capacity is unknown or no reviewed candidate is eligible. Do
  not automatically fill vacancies with unreviewed catalog entries. A later
  explicit saved revision may reconsider a choice.
- When complete eligible context exists, keep `GG-CONTEXT-PRIORITY-1.0` ranking
  and its three-result limit exactly. Distinct alternatives come only from that
  reviewed cohort. If none exists, offer deliberate catalog exploration and
  another context review, clearly separate from personalized recommendations.
- A partial browser save uses existing `GG-CONTEXT-1.0` snapshots. Only submitted
  numbers become provided values; blanks stay unknown, and explicit zero stays
  zero. Nothing is inferred from private prose. Existing all-six, N/A and defer
  modes remain supported. Browser groups fit/importance, timing, and resources/
  burden progressively; every change requires an explicit save.
- The private review page shows latest revisions for the current assessment,
  twelve per page, with explicit deferred/N/A/all filters. Review dates derive
  from the saved timestamp plus the chosen horizon. They never expire, change
  disposition, create evidence or award/withhold completion credit. Old
  assessments and other owners never enter the current review list.

Previous snapshots, contract versions, hashes and algorithms remain immutable.
The policy version is attached to the browser presentation, not retroactively
written into context or scoring snapshots. Search still includes available
practices deliberately excluded from suggestions; its label explains that it
is browsing. No migration, canonical content change or automatic state update
is needed. Revert presentation/forms/templates to roll back; partial snapshots
remain valid under the existing context contract.
