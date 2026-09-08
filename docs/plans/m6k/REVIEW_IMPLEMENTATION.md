# M6K-01-02 revision-bound evidence

`reviews.py` validates source-only records. It does not modify runtime content,
activate a practice, award credit, authenticate reviewers, or dispatch agents.
The advisory navigator remains separate. M6K-01-03 must consume valid records
and program prerequisites when it builds governed batches; it cannot substitute
`navigation-state.json` for this evidence.

## Commands

Use the repository virtual environment:

```sh
.venv/bin/python docs/plans/m6k/reviews.py snapshot --competency 10.01
.venv/bin/python docs/plans/m6k/reviews.py report --output docs/authoring/quality/current-report.json
.venv/bin/python docs/plans/m6k/reviews.py check --base 1a5ca67364a5a3025d32d17a0ebffb58688f4875 --output docs/authoring/quality/current-report.json
```

For later PRs, replace `--base` with the actual pinned PR base, so the history
check sees all previously published receipts. Do not reuse this initial base
forever. A nonexistent revision fails. The first introduction permits an absent
ledger only when the pinned tree also contains no historical receipts.

`report` derives current dispositions and explains invalid receipts without
accepting them. `check` exits unsuccessfully for stale report bytes, an invalid
current receipt, rewritten history (when `--base` is supplied), or a changed
protected recovery baseline. The baseline restriction is deliberate for this
software-only batch; a future runtime-content batch must explicitly reconcile
its authorized invariant boundary rather than silently rebaseline it.

Mechanical findings on unrevised drafts are displayed without pretending those
drafts pass. An instructional/cold-start/integration pass cannot survive those
findings. No raw occurrence count, string uniqueness or keyword rule can establish
instructional quality. Explicit key fields, unresolved references, exact copied
key bodies and known maintainer syntax can be detected; paraphrased leakage,
unlisted promises, missing canonical facets and superficial reasoning still
require actual A/B/C review. A1 and B1 must justify the completeness of the facet
and promised-material inventories, including information promised in prose.

## Records and anchors

The JSON schemas in `schemas/` describe the ledger, individual receipts with
embedded evidence records, and scope plans. Store one scope plan at
`docs/authoring/quality/<ID>/scope-plan.json`; store immutable receipts under
`<ID>/receipts/`. The ledger orders their IDs, paths and exact byte hashes.
Each new disposition links the previous receipt hash for that same ID/dimension.
Keep prior receipts and append a new disposition; never update old hashes to
pretend a historical review saw new content. The pinned-base check protects this
history even if someone recomputes both receipt and index hashes.

An anchor has `path`, `pointer` and `sha256`. With an empty pointer it hashes exact
file bytes. Otherwise it selects an RFC 6901 JSON pointer from JSON/YAML and hashes
canonical JSON for that value. For a shared domain file use
`/exercises/10.01`, or a narrower field such as `/exercises/10.01/goal`.
Do not hash the whole domain merely to reference a single competency.
`make_anchor(root, path, pointer)` constructs an anchor for tooling; it does not
create evidence. Absolute/escaping paths, missing files/pointers, stale hashes,
duplicate JSON/YAML keys and duplicate receipt IDs are rejected.

Scope plans declare canonical hash, starting ability, prerequisites, individual
facets and relationships, exact teaching/practice/evidence/next-route anchors,
and promised material/example section IDs. A bounded default may route another
facet to later practice; a declared full-scope default cannot contain unexercised
facets. The checker cannot know that an author omitted a facet entirely: A1's
canonical audit remains necessary. Keep scope-planning anchors on the actual scope
and pathways, so a later instructional implementation need not invalidate A.

Receipts retain actor kind and run reference, starting and final revisions,
inputs, outputs, criterion-specific verdicts/reasons/anchors, findings with
repair and closure evidence, commands/methods, environment, execution status,
results and claim limits. A/B/C require exactly the criterion IDs from
`program.json`; a blanket `ALL` pass is invalid. Integration requires:

- **I1:** final runtime/companion projection, applicable IDs, and import protection;
- **I2:** executed learner rendering/reveal/access paths and inspected artifacts;
- **I3:** identity, retained rules, historical replay and scoring invariants.

Human dimensions require **H1** (actual authorized decision and scope) and **H2**
(observed evidence, outstanding limits and disposition). Their actor must be a
human, with an authorized minimized decision reference and matching actual
learner/qualified/owner evidence. Never publish personal details or credentials.
The validator rejects an agent/simulation relabeled as human evidence; it cannot
prove that a person behind a purported reference exists or made that decision.
Reviewers must verify the private authoritative record. An N/A disposition is
allowed only for learner/qualified review with a real reasoned human decision;
it is never counted as a pass or used to excuse canonical/owner review.

## Freshness and dependency behavior

| Change | Reviews reopened |
|---|---|
| Canonical scope, declared scope/pathways or scope plan | A, B, C and dependent integration/human dispositions |
| Instructions or guide/material/key content | B, C and dependent integration/human dispositions |
| Instructional renderer, guide template, styles or route | C, integration and dependent human dispositions |
| Canonical runtime package/evidence rules | Integration and dependent human dispositions; immutable baseline check also fails in this batch |
| Another competency in the same domain file | None solely because of the shared file |
| Review contract/schema/criteria | All impacted records; conservative whole-contract binding in v1 |
| Referenced evidence artifact | That receipt and downstream dependent records |
| Latest earlier-stage disposition becomes revise/blocked | Dependent passes cannot use the superseded pass |

B names an exact valid A receipt; C names B; integration names C. Human decisions
name integration and any additional required current receipts. Unknown, stale,
foreign, forward or invalid dependencies fail. Only the latest disposition for
a dimension can support current acceptance. A receipt cannot start on one
relevant revision and finish on another. Old invalidated evidence remains in
the ledger; only invalid *current* dispositions fail the current report check.

A C receipt must identify a separate agent run and retain a learner-only JSON
bundle, actual synthetic attempt artifact, checking keys and subsequent scope
audit. Its declared initial inputs are exactly that bundle. The bundle contains
only `projection`, `attempt_id`, and reviewed `prerequisites`; the projection must
match the final server-side learner projection, and checking keys must equal the
actual guide keys. The retained phase order is learner-only, attempt, key reveal,
scope audit. These controls verify supplied records, not a secret/proctored exam
or proof of what an agent privately knew. Execution and independence claims still
need inspection of the real run evidence. No production cold-start receipt is
created by this implementation or its synthetic tests.

## Current boundary

The ledger starts empty. Prepared repairs remain drafts and are not automatically
upgraded to accepted work. Recovery evidence remains immutable and all seven
formal review dimensions stay pending for all 383 entries. Human, specialist,
live learner, final hosted/browser/Compose and M6K-01-03 workflow work are not
completed by adding this checker.
