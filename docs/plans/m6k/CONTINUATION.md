# Governed one-action continuation

`continuation.py preview` computes progress from validated evidence and selects the
first unresolved, dependency-ready agent action. `queue.py` remains advisory.

```sh
.venv/bin/python docs/plans/m6k/continuation.py preview
.venv/bin/python docs/plans/m6k/continuation.py status
```

Execution belongs to the paired Portfolio Control command, run from its checkout:

```sh
python3 scripts/continue_gitg_m6k.py preview
python3 scripts/continue_gitg_m6k.py run
```

The latter creates or resumes one draft contract PR, then one target draft PR
after human contract merge. Both use the existing runner's review path, checks,
scope audit and stable branch/PR lookup. Repeat after review to continue. Read
`products/gitg-self-host/M6K_CONTINUATION.md` in Portfolio Control for prerequisites
and recovery. Installing the code neither starts a worker nor creates acceptance.

## Progress sources

`program-receipts.json` follows `continuation-receipts.schema.json`. Program passes
need exact task hashes, artifact anchors, all required criterion verdicts, executed
work and exact prerequisite proof hashes. The initial two records bind retained
M6K-00 recovery/invariant evidence. No instructional/browser or workflow-completion
pass has been invented. Each selected action may update only its own disposition;
other records remain exact, with history retained in Git.

`reviews.report` validates A/B/C and domain integration using the actual quality
ledger and current field-specific hashes. A later edit invalidates relevant review
dependencies. Shared domain file edits do not reopen a neighbor whose own artifact
is unchanged. Mechanical success is not professional or empirical acceptance.
Human actions require actual decision references and the separate per-competency
human dimensions; the runner never dispatches a human gate to an agent.

Invalid or explicitly blocked records block their dependency chain. Independent
ready work may proceed. Missing completion evidence leaves an otherwise ready
action eligible to perform; it never clears that action. No commit title,
navigation checkbox, PR phase or checkpoint substitutes for evidence.

## Bounded packets and verification

The provider uses a pinned snapshot of the existing Portfolio Control schemas and
product definition, retained under `portfolio/` with exact Git blob provenance.
Generated IDs combine task ID and relevant source/dependency/schema hashes. A
checkpoint preserves the original baseline and packet on repeated preparation,
so unrelated main commits cannot create a duplicate PR identity.

Content scopes name the selected domain source, exact non-frozen runtime package,
review directory, targeted tests and necessary shared reports. C scopes do not
permit rewriting the learner source. The post-action verifier also compares each
neighbor's artifact hash, since a path allowlist alone cannot isolate one entry in
a shared domain YAML. Protected files, protocol/action inventory, credit/evidence
semantics and frozen packages remain exact. Receipt history is append-only, new
quality receipts must belong to the selected action, and the selected action must
have valid current completion evidence before verification succeeds.

## Operational state

One exclusive SQLite lease covers the repository, including linked Git worktrees,
at the common Git directory's `m6k-continuation/state.sqlite3`. This intentionally
serializes shared source/report writes. Only the token holder can prepare, verify
and release its action. Normal interruption releases the lease; killed processes
require explicit recovery with the prior token and proof of a dead local owner.
There is no automatic live-lease timeout or remote-host takeover. This cooperative
lock does not prevent unrelated external tools from ignoring the workflow.

Persistent checkpoint phases are `prepared`, `awaiting_contract_review`,
`awaiting_target_review` and `interrupted`. None means content accepted or task
completed. Do not edit/delete state to manufacture approval. Preserve dirty work
and use the existing runner's diagnostics to reconcile an interrupted branch.

## Rollout evidence

See `docs/evidence/M6K-CONTINUATION-2026-09-08.md`. Deterministic fixtures exercise
real schema generation, stale/missing receipts, dependency isolation, human gates,
process contention, linked-worktree state, explicit recovery and PR resume. Current
preview selects M6K-01-01. All 383 original drafts remain retained; runtime stays
91 tailored / 292 pending; every formal competency review dimension stays pending.
