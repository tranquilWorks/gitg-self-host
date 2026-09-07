# M6K review and acceptance evidence

This is the required contract for the production evidence implementation in
M6K-01-02, not a claim that the planning navigator already enforces it.
Store minimized repository-safe records under `docs/authoring/quality/<ID>/`.
Never put private participant histories, reviewer personal details or credentials in
public Git. An actual human decision may be referenced through an authorized private
record and a minimized public disposition.

## Each competency's record

Record the exact canonical ID/name, canonical definition hash, selected source origin,
source content fingerprint, associated material IDs/hashes and runtime disposition.
Keep independent states for scope, instructional, cold-start, integration, actual
learner, qualified and owner review. Allowed states are pending, in_progress, pass,
revise, blocked and justified_not_applicable. “Not applicable” cannot excuse missing
canonical teaching or a missing review; use it only for a genuinely irrelevant external
review requirement or a legitimate optional learner pathway, with reasons.

For each stage retain:

- Actor type and stable run/reviewer reference; start/finish revision; inputs actually
  supplied; concrete output artifacts and reproducible observations.
- Each criterion ID from `program.json`, verdict, specific reasoning and exact
  evidence anchors. No blanket domain pass, prefilled approval, textual similarity
  threshold, word-count threshold or “all checks passed” substitute for reasoning.
- Findings with ID, affected facet/artifact, severity, blocking status, repair action,
  closure evidence and revision. Unresolved blockers prohibit a pass.
- Local/hosted command, version/environment, exact result, retained log/artifact and
  claim limit. A collected test is not an executed test; a screenshot is not reviewed
  merely because it exists.
- Source claim classification, locator, retrieval date and scope limits; required
  qualified-review questions and disposition. A source title is not proof of support.

## Scope and level trace

For every meaningful canonical facet state whether it is jointly required,
role-conditional or a legitimate alternative pathway. Map it to teaching, practice,
evidence and next development route, with exact anchors. Explain any bounded deferral
without pretending a mention or exclusion supplies the missing capability.

Record the intended starting ability, prerequisites and why the default is a fitting
challenge. Supply alternate routes where relevant, not rote tiers. Preserve role
choice, cultural/faith alternatives, disability access, resources, consent and safety.
An adapted route must explain what it does and does not exercise. No universal demand
to maximize every competency or choose an absent life role is introduced.

## Materials and assessment integrity

Inventory every promised brief, dataset, example, script, worksheet, model, answer key
and rubric; all essential references must resolve. A private live context can vary,
but an advertised supplied default must actually be supplied.

Separate concept teaching, worked example, learner practice and evaluation. For a
self-guided check, reveal answers only after the prompt/attempt stage and label them.
This is instructional integrity, not secure proctoring. Provide realistic qualitative
rubrics when no single correct answer exists. Recompute calculations independently.
Use one competent, one partial and one plausible incorrect/adverse example to check
whether the criteria discriminate; do not reward a polished incorrect product.

Distinguish observation, artifact, self-report, planning, rehearsal, live performance
and longitudinal evidence. Record what the exercise actually permits concluding. Extra
unscored teaching cannot silently change action units, minimum/full credit or evidence
semantics. A genuine attempt with an adverse outcome is not the same as no attempt.

## Independent cold-start procedure

The coordinator creates a learner-only input bundle with an exact hash. A separate
review run receives that bundle and stated prerequisites, not the author conversation,
hidden rationale, claimed expected success or initial answer key. The coordinator's
`queue.py show` output includes canonical scope for planning and must not be blindly
pasted into this first-stage reviewer context.

Retain the attempt, produced synthetic artifact/calculations and all points requiring
invention or outside context. Reveal the key at the checking stage. Then supply the
canonical definition for the scope audit. Check an appropriate adaptation and a person
already beyond the default where relevant. Inspect neighboring tasks for semantic
interchangeability. A separate agent is not an independent human participant, nor a
qualified professional by role-play.

Do not claim physical training, another person's consent/response, medical results,
long-term follow-through or any real activity the agent did not perform. Desk-test
what can be desk-tested and explicitly retain the live/qualified gap. The agent may
accept the instructions editorially while live evidence remains untested; that gap
must still constrain final product claims.

## Revisions, dependencies and claims

Use per-competency and material/contract fingerprints, not only whole-domain YAML
hashes. A change to another entry must not unnecessarily invalidate this entry.
A changed scope reopens A and dependent B/C; changed instruction/material/key reopens
B/C as appropriate; changed rendering or evidence semantics reopens the impacted
runtime review. Material changes require re-review, not changing old receipt hashes
to the latest values. Preserve the old evidence and append the new disposition.

A scope planning artifact can remain valid through B's implementation when its scope
and pathways remain unchanged. Link B to that exact scope record. C must review the
actual final learner artifact and associated materials. Domain/final reports derive
only from current valid receipts, without filling missing states as pass.

The report must state separately how many entries are authored, scope-reviewed,
instructionally complete, independently agent-reviewed, runtime-integrated,
actual-learner-reviewed, qualified-reviewed and owner-accepted. A companion does not
count as a rewritten frozen runtime. Required expert or owner approval must come from
actual authorized people; the agent cannot self-clear it. No completeness percentage
may silently mix these different meanings.
