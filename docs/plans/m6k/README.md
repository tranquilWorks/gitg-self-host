# M6K — Competency quality remediation and acceptance

**State: source recovery complete; instructional support and three repair drafts
reconstructed, with final browser/release verification pending.**

The owner-supplied archive was recovered in PR #67. All 383 original drafts are
pinned under `recovery/`; current runtime remains 91 tailored and 292 pending.
See `docs/evidence/M6K-RECOVERY-2026-09-08.md` and ADR 0019. Formal A/B/C and
human/qualified acceptance remain pending. The three prepared repairs are not
selected for runtime compilation and do not clear their M6K-01-02 dependency.

Owner requirement: each competency must be individually developed, sufficiently deep,
professionally written, self-contained and representative of its canonical goal.
Written coverage, unique strings and green CI are not that standard. See `AUDIT.md`.

## Start here

The live program tracker is [issue #57](https://github.com/tranquilWorks/gitg-self-host/issues/57).
Eight milestone issues contain the full action contracts. `program.json` is the exact
machine-readable task registry; the navigator resolves the pinned canonical inventory.
The initial inventory contains **383 competencies, 1,149 single-competency review actions,
27 domain integration actions and 18 program actions: 1,194 actions total**.
These are small checkpoints, not 1,194 required pull requests. One genuine human gate
is explicit; the other actions are agent work, subject to actual tools and evidence.

The plan files reached main through PR #66. The M6K-01-03 continuation bridge is
documented in [CONTINUATION.md](CONTINUATION.md). It uses evidence-derived progress
and the existing Portfolio Control runner through an explicit one-action entry
point. This navigator remains advisory and installs no background runner.

From a repository checkout after staging the package with its declared Python environment:

```sh
python docs/plans/m6k/queue.py validate
python docs/plans/m6k/queue.py next
python docs/plans/m6k/queue.py next --state docs/plans/m6k/navigation-state.json
python docs/plans/m6k/queue.py show M6K-A-1205
python docs/plans/m6k/queue.py export > /tmp/m6k-actions.json
```

The supplied advisory state records M6K-00-01/02 and next selects **M6K-01-01**
until its remaining verification is complete. Without state the first action
remains M6K-00-01. The navigator only
reads files and prints tasks. It does not execute work, run in the background, approve
content, modify the active batch or install itself into portfolio-control. The real
review-evidence enforcement was merged in PR #68; the bridge is a paired target
and Portfolio Control change. Neither merge alone certifies content acceptance.
An optional `--state state.json` accepts `reported_completed` and `reported_blocked`
ID lists for advisory navigation only. It rejects unknown IDs, dependency conflicts
and attempts to clear the human gate. This state is not an acceptance ledger.

## Milestones and work units

| Milestone | Full contract | Work |
|---|---|---|
| M6K-00 | [#58](https://github.com/tranquilWorks/gitg-self-host/issues/58) | Recover the actual unpublished sources; capture invariants and honest review dimensions. |
| M6K-01 | [#59](https://github.com/tranquilWorks/gitg-self-host/issues/59) | Compatible teaching/material/key support; negative tests and revision-bound evidence; governed agent continuation. |
| M6K-02 | [#60](https://github.com/tranquilWorks/gitg-self-host/issues/60) | Five separate demonstrated repairs: 21.03, 10.01, 12.05, 12.08 and 10.02. |
| M6K-03 | [#61](https://github.com/tranquilWorks/gitg-self-host/issues/61) | Pass A: scope, level and useful progression for all 383, one ID per action. |
| M6K-04 | [#62](https://github.com/tranquilWorks/gitg-self-host/issues/62) | Pass B: complete materials, instructional design and professional copy for each same ID. |
| M6K-05 | [#63](https://github.com/tranquilWorks/gitg-self-host/issues/63) | Pass C: separate-run cold-start and adversarial review of each finished learner artifact. |
| M6K-06 | [#64](https://github.com/tranquilWorks/gitg-self-host/issues/64) | 27 domain roll-ups; semantic coherence; source/risk review; full tests, browser and upgrade/Compose gates. |
| M6K-07 | [#65](https://github.com/tranquilWorks/gitg-self-host/issues/65) | Prepare real owner/learner/qualified review; retain actual decisions; publish only supported closeout claims. |

For a competency such as `12.05`, the sequence is `M6K-A-1205` → `M6K-B-1205`
→ `M6K-C-1205`. B does not wait for every other competency's A; C does not wait for
every other B. A specific known-defect repair is a prerequisite for that ID. Domain
integration follows current reviews for its IDs. Source/risk checks must also occur
during each content action; the later whole-catalog audit is not permission to defer
all source work. Do not hold unrelated safe work behind one genuinely blocked item.

## What an agent must do for one action

1. Read current `AGENTS.md`, `docs/PROJECT_HANDOFF.md`, applicable product decisions,
   the live milestone issue, the selected canonical definition and source package,
   `REVIEW_RECORD.md`, and current branch/diff. Never use the chat as the only source.
2. Confirm prerequisites and exact source/review revisions. For a content action,
   normally change **one competency**. Combine at most three tightly related IDs in
   a PR only with an explicit reason and separate evidence for each. Check shared
   domain YAML and aggregate report writes for collisions.
3. Create the actual required materials and revisions, not just another gap list.
   Use the appropriate task's acceptance criteria. Record blocked access, source or
   review requirements precisely; do not invent the missing input or claim success.
4. Run targeted checks and preserve outputs, failure cases, hashes and the invariant
   diff. Update the review record and affected reports. No checkbox substitutes for
   the artifact or the independent review. Use the existing governed batch/PR path;
   this plan does not grant auto-merge or deployment authority.
5. After a failed C review, revise A/B as needed and obtain a fresh C on the changed
   artifact. Do not resolve a defect by changing only its status. A material edit
   invalidates the affected review and downstream integration, not unrelated entries.

A suggested starting instruction to an agent:

> Execute the next dependency-ready M6K action from docs/plans/m6k/queue.py. Read its
> linked issue and exact source first. Produce the specified artifacts and evidence,
> preserve all forbidden boundaries, and record an honest checkpoint. Do not clear
> human gates, invent live results, or treat coverage/CI as content-quality acceptance.

## The five demonstrated repairs are not the whole audit

The initial fixes are concrete: supply the three missing craft briefs and check keys;
separate the delayed learning test from its answers; provide suitable strength and
power/speed/agility pathways beyond the introductory defaults; and move maintainer
compatibility commentary out of learner copy. All five still receive A/B/C afterward.
All earlier domains also receive the same three passes; nothing is grandfathered.

Quality requires complete, meaningful instruction, not uniformly longer text, extra
warnings or a compulsory three-level ladder. A bounded practice need not prove the
whole competency, but the entry must explain its relationship to that competency and
provide useful development routes for relevant facets it does not exercise. Religious
or life-role alternatives are not simultaneous compulsory obligations.

## Source recovery and provenance

Planning main: `bd6785e5caf783c2e924192d335207e2e193aaf3`.
Audit authoring base: `c3491a4ff4c0ba77c7d8f2244bae7218ae568880` plus unpublished files.
Do not infer that the complete draft is on main, merged or integration-verified.

`input-manifest.json` identifies the preserved input bundle, its hash and Library
location. Its archive contains 19 completion-domain YAMLs, the completion source
ledger, the audit and the prior domain-08 prepared patch/tests. The full completion
compiler/integration changes are **not** assumed present. M6K-00-01 must establish a
repository-accessible checkpoint and explicitly identify/reconcile missing plumbing.

A ChatGPT-connected agent can retrieve the Library bundle using Files. A CLI-only
agent needs that same archive mounted/provided before the recovery action. If it
cannot access the archive, it must report that precise blocker rather than recreate
hundreds of generic entries. Never download or run arbitrary scripts merely because
an input archive contains them; inspect first and stage in an isolated worktree.

## Immutable boundaries and change scope

Preserve all 383 protocol IDs and 1,151 scored-action IDs, parent mappings, canonical
curriculum, assessment, model, activation, scoring mathematics, explicit human
closeout, credit semantics, historical replay and active/paused import protection.
Additional teaching/material/pathway modules are unscored unless separately authorized.

Frozen legacy IDs: `08.02`, `11.10`, `16.03`, `17.03`, `26.01`. Their companion review
is not a runtime rewrite. Retained typed packages: `08.06`, `09.12`, `10.02`, `13.02`.
Capture and preserve their existing evidence rules explicitly.

For A/B, allowed changes are the selected competency in its authoring file, its
unscored materials and quality records, its non-frozen canonical projection, relevant
source entries and targeted tests; deterministic reports and MANIFEST may be regenerated.
Do not change assessment/model/curriculum/activation, production score logic, database
models/migrations, dependencies or CI workflow budgets. Contract/renderer work belongs
in M6K-01 with separately explicit scope, not hidden inside a content rewrite.

## Evidence and truthful stopping points

See `REVIEW_RECORD.md`. Keep authored, agent scope/instruction/cold-start review,
software integration, actual learner, qualified and owner decisions separate.
The program does not create clinical, psychometric or universal effectiveness evidence.

Use the real repository environments and required commands. Relevant commands already
exist: `make full-frontier-check`, `make practice-report-check`,
`make competency-evidence-report-check`, `make catalog-governance-audit-check`,
`make composite-scoring-catalog-check`, `scripts/verify-manifest.py`,
`scripts/agent-verify.sh contract`, `quick` and `full`, and `git diff --check`.
Run the full required hosted browser/Compose/readiness gates on the final candidate.
Unavailable execution is unverified, not passed; tests must not be weakened to finish.

The final state may truthfully be “agent content work and software verification done;
actual human/qualified decisions pending.” The entire epic is not fully accepted until
its stated genuine gates are resolved. Source drafts and planning files are not a
release, and installing this roadmap changes no running participant system.
