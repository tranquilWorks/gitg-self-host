# M6K-01-03 governed continuation — 2026-09-08

Target baseline: `f03e73db4748b192bfe6fae18ac0f540874700cd` (merged PR #68).
Portfolio Control source: `38a7c91d8c3fe7a663a57d0353a3e60773ded20d`.
Scope: one-action workflow tooling and its paired Portfolio Control registration.

## Implemented behavior

The provider reads the current program and validated quality receipts. Program
records bind task definitions, executed criterion evidence and exact prerequisite
proofs. A/B/C and integration derive from the existing field-specific review
validator. No navigator state, commit title or checkpoint phase confers acceptance.
An invalid dependency blocks its chain while independent ready work remains usable.
The human action is never dispatched, and human decisions remain separately required.

Generated contracts validate against the existing pinned batch schema and name
specific action scope, dependencies, baseline, verification, evidence and rollback.
Exact source schemas/product definition and their original Git blob IDs are under
`docs/plans/m6k/portfolio/`. Shared domain writes receive a per-entry neighbor hash
check in addition to path restrictions. Frozen files, protocol/action IDs and
completion/evidence semantics remain exact. Post-action verification requires a
valid receipt for the selected action, preserves old receipts, and rejects added
quality dispositions for another action.

An exclusive repository lease and durable checkpoints live in the common Git
directory outside the application database. Tests cover live process contention,
linked worktrees, wrong tokens, explicit dead-local-owner recovery, corrupt binding,
one action per lease, restart identity and phases that cannot claim completion.
The paired Portfolio Control entry point retains the historical schedule and
registers M6K explicitly. It invokes the existing contract and implementation runner
with `pr-only` / `review-only`; prepared contracts cannot be broadened on resume.

## Executed checks

| Command or check | Result |
|---|---|
| `.venv/bin/python -m pytest tests/test_m6k_continuation.py tests/test_m6k_review_evidence.py tests/test_m6k_recovery.py tests/test_m6k_repair_drafts.py tests/test_instructional_content.py -q` | 101 passed. |
| `.venv/bin/python -m pytest tests/test_m6k_continuation.py -q` after making clean-start fixtures independent of the live frontier | 30 passed. |
| Portfolio `PYTHONPATH=scripts python -m unittest discover -s tests -v` in the reference checkout | 45 passed: 15 M6K tests and 30 existing autopilot regression tests. Other Portfolio test modules were not present locally. |
| `./scripts/agent-verify.sh contract` | Passed environment, manifest, repository-wide Ruff, Django system check and migration-drift check. |
| Current provider preview and sample contract generation | Selects `M6K-01-01`; only M6K-00-01/02 have valid program completion proofs; no dispatch or lease created. |
| Pinned schema/product Git blob check | All four upstream reference blobs match exactly. |
| `git diff --check` and new Portfolio module Ruff / existing runner `py_compile` | Passed. |

Transcripts, preview, sample batch and source hashes are retained in
`docs/evidence/m6k-continuation-2026-09-08/`. The sample is a reviewable simulation
artifact, not an active batch or executed content acceptance.

Earlier in this continuation, independent `make pilot-check`, `make curriculum-check`
and `make competency-evidence-check` completed successfully. Full-frontier tests
(3), catalog-governance and composite-scoring catalog checks also passed on the
merged baseline. No runtime/catalog code changed in this workflow slice. The full
non-browser suite was started, but remained incomplete after more than 50 minutes;
it is not reported as passed. Local Chromium installation failed on an installation
lock; Docker is unavailable. Browser, Compose and aggregate hosted CI remain open
until actually executed on the published candidate. No required gate was weakened.

## Current frontier and limits

All 383 recovered drafts remain retained. Runtime remains 91 tailored / 292 pending.
The quality ledger still has no per-competency review receipts: all seven dimensions
remain pending. M6K-01-01 must finish browser/release verification before the queue
advances its dependent actions. The presence of PR #68's validator or this bridge
does not manufacture a program completion record. No owner, learner, specialist,
release, deployment or mastery acceptance has been claimed.

The lease is cooperative and serializes participating workers; external tools that
ignore it can still edit files. Interrupted dirty branches stop for preservation and
reconciliation through existing runner diagnostics. There is no timeout takeover,
automatic approval, automatic merge, deploy or background worker. Source/runtime
changes in later content actions must satisfy all existing tests; this bridge does
not waive the historical recovery invariants or any later verification gate.

Rollback: revert the two isolated tooling/registration changes. Preserve retained
review and recovery evidence and any interrupted work. This slice performs no
runtime import, database mutation or migration.
