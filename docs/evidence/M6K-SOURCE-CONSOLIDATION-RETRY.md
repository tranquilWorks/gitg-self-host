# Approved quality checkout and runner repair — 13 September 2026 UTC

The owner approved the bounded checkout and test-runner patch after reviewing
its local results. Quality stays at **180 minutes**. Only the quality checkout
gets `fetch-depth: 0`; its existing test step gets
`PYTEST_ADDOPTS="-n 4 --dist=load --maxschedchunk=1"`. Development requirements
add `pytest-xdist>=3.8,<4`. Every test, assertion, migration, readiness command,
browser/Compose step and aggregate success requirement is preserved. The active
contract records this precise exception. No runtime dependency changes.

Run [34779233842](https://github.com/tranquilWorks/gitg-self-host/actions/runs/34779233842)
tested head `7724250afd495374b372719490aac76806ab0930`, tree
`63183b2eb1e99a58678c8f58c11c2dd8c75e4f55`, through test merge
`62b81d8a4faa567cae5048127be606e4571bd00e`. Quality finished pytest with
**938 passed, one failed and 34 deselected in 9,871.45 seconds**. The unchanged
21.03 regression could not read its pinned ancestor
`6173b1e15596ac883fd08f9c4c1f4967f3450c6a` from the shallow checkout. This was
not a timeout: quality failed after 165 minutes 9 seconds, and its seventeen
subsequent readiness steps were skipped. The aggregate gate failed.

A separate depth-one clone reproduced the exact missing-path error: eight tests
passed and that comparison failed. Fetching full history made all nine tests
in the unchanged module pass in 0.26 seconds. The pinned revision is an ancestor
of the candidate and main. The repair supplies its original input; it does not
replace the comparison or change the baseline. The
[checkout action](https://github.com/actions/checkout/tree/v6) documents the
full-history option.

The local execution evidence for this follow-up is:

| Check | Actual result and provenance |
| --- | --- |
| Complete non-browser pytest with the proposed four-worker configuration | All 939 passed, no errors/skips; exact original test IDs each executed once; 2,971.65 seconds; separate clean checkout of `7724250` |
| Earlier two-worker experiment | All 939 passed in 5,932.19 seconds; retained as a separate experiment |
| Seventeen readiness commands | All exit 0 on `7724250`, verbatim from unchanged `contracts/verification.commands`; 19:56:56–21:53:04 UTC, individual receipts retained |
| Current-head hosted browser | 34 passed / 939 deselected in 355.23 seconds; four retained images have the same verified hashes as the four previously visually inspected views |
| Current-head hosted Compose | Passed job `103783106048` in 107 minutes 41 seconds, including backup, recreation/persistence, restore, restored-state replay/readiness and clean shutdown |
| Local Compose | Exit 0, completed 18:45:49 UTC; complete isolated recovery drill; synthetic containers and volume confirmed removed |

The worker experiment used Python 3.13.14, pytest 8.4.2 and Django 6.0.8, with
every original resolved dependency version retained and only pytest-xdist 3.8.0
and execnet 2.1.2 added in a separate environment. Requirements remain bounded
ranges, not a lockfile. Hosted Python was 3.13.15. Local timing is not a guarantee
of hosted timing. Worker databases remain separate; no test or migration is
disabled. The smaller scheduling chunk distributes the long independent cases
without keeping an entire slow file on one worker.

These separate passes do not relabel the original failed full-harness run below
as successful. On the approved candidate, all 283 source checks passed in 0.050
seconds and all 13 deployment/history checks passed in 0.26 seconds. The
repository contract passed at 22:59:35 UTC: manifest, Ruff formatting/lint,
Django system checks and migration-drift checks. The schema and 107-path scope
audit passed; all twenty-one source folders' contents and five repaired test
modules remain identical to `d373f9f`. Runtime, canonical, compiler and historical
comparison paths remain identical to main. The repository environment helper
retained every old dependency version and installed the same two additions as
the passing experiment. Final documentation gets a regenerated manifest and
another contract check before publication. Fresh full hosted CI is still required.
Exact final commit/tree and CI/merge receipts belong in PR #80 and
the successor evidence. Browser results cover unchanged runtime, not these
unselected authoring guides. Recovery drills are synthetic, not deployment.
Runtime coverage remains 108 tailored / 275 pending / 383 protocols / 1,151
actions; independent, learner, specialist and owner content acceptance remain
separate from the explicit merge authorization.

Detailed logs, JUnit test-ID receipts, dependency versions, shallow-checkout
reproduction and the original failed runs remain in
`/home/kbianco/gg-source-delivery-evidence/`. The older checkpoints below retain
their original dates, failures and limitations.

# Dependent budget-assertion repair — 13 September 2026 UTC

The first local full harness completed pytest with **938 passed, one failed and
34 deselected in 11,088.13 seconds**. It then stopped before the seventeen
readiness commands. The failing deployment-contract assertion still expected
Compose's old 60-minute allowance after the approved workflow change to 180.
The failure log remains retained; this run is not a full-harness pass.

The dependent repair changes only that existing assertion's expected value to
180, preserving its exact quality expectation of 180 and every other deployment
criterion. The active batch records this necessary test path for the approved
Compose setting. No workflow command, runtime file, canonical package or repaired
source-test criterion changes. The owner declined increasing quality's budget;
it remains 180 minutes in both workflow and test.

Rerun the complete deployment-contract module, all 283 source checks, manifest
and repository contract. Execute the previously unreached readiness commands
verbatim from `contracts/verification.commands`, retaining individual exit receipts.
Fresh exact-head hosted CI must rerun the entire pytest suite and every readiness,
browser and Compose gate. Do not relabel the earlier failed local harness as passed
or substitute the focused repair for that required hosted full-suite result.

The first long local run began on the manifest-repaired inputs later committed as
`6212e2f`; while it ran, documentation and the approved workflow budget were
updated. Its deployment test read the new 180-minute workflow against the still-old
60-minute assertion. All other tests passed, including all 283 source checks.
The evidence below retains the preceding snapshots and their original limitations.

# Approved Compose time-budget repair — 13 September 2026 UTC

After inspecting the concrete patch, the owner instructed: “Apply the bounded
timeout patch.” This authorizes only increasing the Compose job allowance from
60 to 180 minutes, its explanatory comment, and the corresponding active-batch
scope exception. All workflow commands, assertions, dependencies and required
success results remain unchanged. The removed temporary workflow stays absent.

Current-head run [34770876994](https://github.com/tranquilWorks/gitg-self-host/actions/runs/34770876994)
verified `c3a773f6f609ba0963f5e41ad8b80713740d7495` through test merge
`8c15e335ddd3fe0e242359989662c59114da54ec`. Browser passed all 34 checks;
Compose job `103760172473` was cancelled before backup restoration. Its check-run
annotations explicitly report that the job exceeded the one-hour execution limit.
The earlier cancelled Compose job in run `34742998545` has the same explicit
limit annotation. Neither is a passed recovery drill. Full job logs and annotations
are retained outside the checkout in the local evidence directory below.

The local full harness and isolated recovery drill remain running at this capture.
The local drill has restored the verified backup and reached post-restore readiness;
it is not yet claimed complete. Preserve both healthy processes and their final
exit receipts. The new candidate needs fresh manifest, source and contract checks,
a structural comparison proving the sole workflow-value change, and all required
hosted gates. Final results belong in PR #80 and the successor evidence record.

This is an execution allowance change, not acceptance of a failing check or any
runtime, deployment, participant-data, specialist or learner-review change. The
following earlier checkpoints remain historical evidence with their original dates
and limitations.

# Current local recovery checkpoint — 13 September 2026 UTC

The owner's current instruction explicitly authorizes repairing/verifying/merging
PR #80, then delivering and merging 11.05–11.10. It does not accept formal human
reviews, waive failing gates, authorize deployment or change participant data.
The earlier retry account below is retained historical evidence, not current status.

## Recovered source and manifest repair

A full authenticated clone at `/home/kbianco/gitg-self-host` resumed live head
`d373f9f84dcc707b37eeb401c8f772eac63a1652`; main was
`d93532696d3ea9d04e50f47350b90fa255208511`. Older managed local checkouts were
left untouched. The next-six remote branch still pointed to the same source head;
no newer six-batch PR or complete local draft was found. All five repaired test
files from `d72798ff3b58feeb4b2ad5b3961cfeb9d38516a7` remain byte-identical.

The unchanged manifest verifier reproduced exit 1 with exactly the stale
`.github/workflows/source-repair-capture.yml` entry. The workflow was absent and
remains removed. Regeneration removed exactly that entry and the next verifier
passed with 1,323 entries. Repair commit:
`6212e2f721b9c766b62ee179afc80dcda8f91506`; tree:
`461dc38488fc598aeb0639fbad00fb5872941d64`.

## Current executed evidence and pending gates

Environment: Debian 12, Python 3.13.14, repository-created `.venv`; resolved
Django 6.0.8, pytest 8.4.2, Ruff 0.16.7, Playwright 1.62.0 and Chromium
151.0.7922.34 (build 1234). Requirements are bounded ranges, not a lockfile.
Full resolved dependencies are retained locally in `pr80-pip-freeze.txt`.

| Check | Actual result at this checkpoint |
| --- | --- |
| `python scripts/verify-manifest.py`, initial head | Exit 1, reproduced stale workflow entry |
| `python scripts/verify-manifest.py --write`, then verifier | Exit 0; exact one-entry repair; 1,323 entries |
| `python -m unittest discover -s tests -p '*sources.py' -v` | Exit 0; all 283 passed in 0.046 seconds, none skipped |
| Full harness contract stage | Manifest, Ruff format/lint, Django system and migration-drift checks passed |
| `python scripts/author_full_competency_frontier.py --check` | Exit 0; deterministic/current, 108 tailored / 275 pending |
| `make e2e PYTHON=.venv/bin/python` | Exit 0; 34 passed, 939 deselected in 357.53 seconds |
| `./scripts/agent-verify.sh full` | Running at documentation capture; 939 selected non-browser tests; no full pass claimed yet |
| `make compose-smoke` | Running at documentation capture in isolated `ggsmokelocal03979759`; no completed drill pass claimed yet |
| Protected-path diff against main and `git diff --check` | Exit 0; no canonical/runtime/compiler/dependency/deployment/formal-review change |

The source, full, compiler and Compose runs began with the manifest-repaired
working tree later committed as `6212e2f`; the full harness header still names
parent `d373f9f` because the commit was created after it started. The browser run
started on `6212e2f`. The only subsequent changes in this checkpoint are evidence,
status documentation and their manifest sizes; no tested source/runtime file is
changed. Final contract/source checks and hosted CI must verify that final commit.

Local logs, exit receipts and screenshots are retained outside the checkout in
`/home/kbianco/gg-source-delivery-evidence/`; the harness additionally retains its
ignored `docs/evidence/local/verify-full-*.log`. Browser artifacts were generated
under `test-results/pilot-walkthrough/`. The agent visually inspected
`desktop-profile.png`, `mobile-weekly-plan.png`, `m6k-10.12-prompt-390.png` and
`m6k-10.12-check-1280.png`: readable content, bounded layout, visible controls and
separate prompt/key state in the sampled views. This is agent inspection of
existing application regression artifacts, not actual learner or specialist review
and not runtime validation of these 21 unselected sources.

Hosted run [34769656775](https://github.com/tranquilWorks/gitg-self-host/actions/runs/34769656775)
checks repair head `6212e2f`; browser passed while quality/Compose were still
running at capture. This documentation commit supersedes that head and requires
its own final hosted run. Do not transfer a green status between commits. Final
local results and the exact final CI/merge receipt must be recorded in PR #80 and
the successor batch evidence; an enabled auto-merge or test merge is not a merge.

## Failed historical evidence remains visible

[Run 34742998545](https://github.com/tranquilWorks/gitg-self-host/actions/runs/34742998545)
failed quality on the stale manifest before later quality steps ran; browser
passed, Compose was cancelled and the aggregate failed. Its test-merge checkout
was `9df5fd32f2687da9e451849a00c151f4f9ccba8a`, not an actual main merge.
[Repair diagnostics 34742788628](https://github.com/tranquilWorks/gitg-self-host/actions/runs/34742788628)
succeeded and produced the preserved test repair. Its success is separate from
the freshly executed local 283-test pass. The older 266-pass/17-unrun statement
below is superseded as a current limitation, not deleted from history.

## Next executable action and claim boundary

Finish the healthy full harness and isolated Compose drill, retain their exit
statuses, verify this documentation candidate's manifest/contract/source suite,
and require all final hosted quality/browser/Compose/aggregate checks. Update
PR #80 with exact local results, final head/tree and CI provenance; mark ready
and merge normally under the owner's existing authorization only after gates pass.
Fetch main and verify the actual merge receipt and source identities. Check #78/#79
for unique later changes before treating them as superseded; do not merge them over
the consolidation. Then reconcile the existing next-six branch with merged main
without resetting or force-pushing and deliver all 11.05–11.10 together.

Runtime remains **108 tailored / 275 pending / 383 protocols / 1,151 actions**.
The 21 sources are authored and source-verified, published on the branch, and
not yet merged at this documentation checkpoint. Compiler selection/application
verification of these guides and independent/learner/qualified/owner content
acceptance remain pending. Source integration needs its own compatible scope.
No production deployment, participant-data mutation or runtime/scoring rewrite
is part of these deliveries.

---

# Source consolidation retry evidence

Base: d93532696d3ea9d04e50f47350b90fa255208511.
Branch: codex/m6k-six-more-source-consolidation.
First published consolidation commit: a3a0e68fd456cce08f910c442f47014fcceee134.
Owner request: retry the interrupted six-more-and-push operation.

## Delivered scope

The six new source packages are 09.16, 09.17, and 11.01-11.04. They contain individual guides, complete materials, twelve fresh checks, separate corrective keys, five later packets, adaptations, progression, and explicit claim limits. The preceding fifteen source candidates and their four test modules are consolidated alongside them. Publication does not merge draft PRs #78 or #79 or make any source compiler-selected.

The four retained source subtrees were reconstructed from the uploaded checkpoint and verified against their actual Git object identities:

- reasoning-foundations: cb235527e2fd8996a12b159187b64f183b02d218
- evidence-humility-forecasting: 957a17dd87487b94a2d1261123d12269762d1f4e
- systems-causes-tradeoffs: cc9ef1c32b143392c076a8c73cc8b44bfe28b13c
- risk-judgment-inference: f6a7161d1fdc42fd16b84e302115176a09e1c80a

The new models-information-execution subtree is eaa49d4e68b4932f6318ec5a258b31d7c9725ec8. Its current README explicitly distinguishes defined tests from current execution. All six instructional child trees remain as authored in the interrupted task.

## Tests actually executed on this retry

The preceding uploaded checkpoint was extracted into an isolated directory and its four original source suites were rerun with unittest: **199 tests passed**. Their files and content subtrees match the published Git identities, rather than merely matching a displayed coverage count.

The new module was recovered byte-for-byte: blob 104b51f577c6bf3c098eb6329517c9c196eff331, 26,506 bytes. Its cohort and fixture files also match the published blobs, 87ac13fd1dbacdf8e1f4995426167ec6ca5c9b0e and eef9e77d6a9323231d200371d12daa79ed2e3645. **67 new fixture/metadata tests passed** without edits to the module, mocked source readers, or fabricated Markdown files. They cover the model domain and arithmetic, provenance graph, time accounting, 54 priority combinations, 64 find/return patterns, consent combinations, and dependency/resource calculations.

Thus this retry executed **266 passing tests**, not all 283 defined tests. Seventeen new source-text checks were not executed because the corresponding Markdown files were available through GitHub but not mounted locally. Their subjects are actual packet/table alignment; complete guide, key and later-packet structure; scope traceability; privacy wording; source-chain and non-attribution wording; and the supplied story/branch content. Source-tree inspection is not substituted for their execution. All original tests remain in the branch and should be run together on a complete checkout:

```sh
python -m unittest discover -s tests -p '*sources.py' -v
```

No full-application, canonical compiler, production-browser, historical-replay, or actual-learner pass is claimed by these standalone tests. Earlier checkpoint browser and test reports are historical evidence only, not rerun results for this publication.

## Manifest reconstruction and source boundaries

The complete baseline MANIFEST.tsv was recovered and hash-verified: 1,221 entries, 79,046 bytes, Git blob 81c90dd48f84ba206a7f4a0f33b5f160ab6ed7ab. The final manifest preserves every baseline path and byte length except the intentionally changed active-batch file. It adds the 102 actual new source, test, index, and evidence paths, yielding **1,323 entries**, excluding MANIFEST.tsv itself under the existing verifier's rule.

Retained-source byte lengths come from the hash-matched local subtrees. New-source lengths come from the complete GitHub tree inventory, including all 28 files in models-information-execution. Test, contract, index, and evidence lengths use exact UTF-8 bytes. Sorted output, unique paths, baseline preservation, changed-path scope, and the final manifest blob are checked independently. This is a deterministic manifest reconstruction from verified baseline and Git metadata, not a claim that the full checkout-based contract command ran. The verifier itself is unchanged.

The GitHub commit comparison shows only the allowed source directories, five source test modules, the consolidation index/evidence, active-batch contract, and final manifest. Canonical data, application code, templates, dependencies, workflows, deployment files, original compiler inputs, recovery archives, and formal review records remain unchanged.

## Unverified work and next action

Local GitHub and package-index access attempts failed on DNS resolution. Python and Playwright are present; Django and Ruff are not. Authenticated connector reads and writes work. Full source-text checks, Ruff, the repository contract, canonical integration, readiness, actual application/browser journeys, Compose recovery, and hosted CI remain unverified. No actual learner, qualified specialist, or owner acceptance is fabricated.

On a complete checkout, run all 283 source tests, the unchanged manifest verifier, Ruff, and the required repository gates. Integrate the 21 source candidates through the existing authoring compiler in bounded batches, retaining original package hashes, IDs, active/paused instructions, and 09.12's typed-evidence privacy. Generate canonical packages, current/recovery projections and reports, then verify actual application and replay behavior. Human review requirements remain separate.

## Claim boundary

Runtime remains **108 tailored / 275 pending / 383 protocols / 1,151 actions**. The 21 additional source candidates are published, not runtime-complete or formally accepted. The user's push request authorizes this branch publication; no merge, deployment, live action, or historical evidence mutation occurs. The PR remains a draft pending its unresolved gates.
