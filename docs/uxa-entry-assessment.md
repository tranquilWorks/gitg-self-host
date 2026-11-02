# UXA-02 + UXA-03 — entry, Home and assessment

The owner requested two UXA issues per implementation PR to reduce expensive
hosted-CI iterations. This batch covers #116 and #117 together, starting from
merged main `bc55fe6ef9a8f4b94b26052096a9e320b0791e0c`. It does not authorize
merging this new PR, starting #118–124, changing CI gates, or deploying.

## Entry and Home

An account without an assessment sees one introductory surface and an assessment
start. Navigation hides Profile, Practices, Personal OS, Weekly, History and
Evidence until an assessment exists; direct GET/HEAD requests to those entry
pages redirect to Assessment. Record-specific routes retain their existing
ownership checks and 404 behavior. Account, sign-out, policy and quick-start help remain
available. POST handling retains CSRF validation and existing service guards.
An operator-provisioned example assessment remains usable, clearly labelled as
example results rather than the user's own answers. Ordinary registration never
creates one. No “demo” entry copy is used.

Home derives progress from actual assessment, direction, practice and submitted
closeout records. Assessed users get suggestions; active/paused users get their
current practice and a concrete next action; a completed loop gets its review
and the next choice, without restarting onboarding. The four explanatory blocks
move from Profile to the pre-assessment introduction and `/quick-start/`.
Normal Home no longer carries the long model explanation.

Current, verified, owner-only twelve-month direction, season and named capacity
appear when provided. Home is non-cacheable. Mission, audit responses and the
private priority stack do not move onto Home. Direction text remains a planning
reminder: it is never analyzed, scored or substituted for a structured ranking
factor. Reassessment does not leak direction from an earlier assessment.

“Skip for now” is a CSRF-protected, explicit user-choice deferral through the
existing append-only context service. It defers readiness, retains other saved
factors and preserves unknown versus zero. It is not N/A, evidence, completion
or a score change. The route checks the current assessment, suggestion and
context revision, rejects an active practice, and fails closed on stale or
unverifiable state. Skipped choices stay excluded until explicitly revised in
the existing saved-choices screen; there is no timer or automatic expiry.
This is an omit shortcut, not a random reranking algorithm: the existing bounded
suggestion order and context selection contract remain unchanged. If all current
suggestions are excluded, the user can deliberately explore the existing browser.

## Assessment

`growth/assessment_copy.py` contains exactly 93 display prompts, keyed to the
50 core, 37 capability-follow-up and six orientation-follow-up IDs, and three
five-value display scales. It is separate from the frozen canonical JSON sent
to the unchanged scorer. Numeric answers, N/A, item types, polarity, mappings,
weights, display order, source versions, existing share codes and golden
fixtures stay exact. The display rewrite preserves comparison and scale anchors;
plain-language usability and semantic equivalence still need owner/human review,
not a claim of psychometric validation from unchanged mathematics.

The 50 core questions flow straight into the scorer-selected follow-ups.
The frozen contract selects eight capability follow-ups and, when applicable,
up to two orientation follow-ups. The issue's shorthand “8 clarifiers” does not
override that existing contract. There is no exposed clarifier or assessment-mode
choice. Back works across the core/follow-up boundary; editing core answers
reselects from core responses/timing and drops stale, unselected follow-ups.
Legacy saved drafts and imported assessments retain their existing compatibility.

With answer shortcuts enabled, one valid 1–5 or N key answers and advances;
shortcuts are otherwise off. Modifier keys, held-key repeats and typing outside
the focused question cannot consume answers. Ordinary answer buttons still use
Next. Progress remains local until the completed assessment is explicitly saved
by the existing application flow; save failures retain answers and expose Retry.

Completed state is a concise “Assessment complete / See results / Retake”.
Import and share controls are collapsed. Retake uses a native modal with a
label, focus containment, cancel/Escape and focus return; confirmation clears
only the local draft, never previous saved results. The before-you-begin surface
is only shown for a new/resumed attempt, not after completion. Existing active
practice and reassessment-history consequences remain in the confirmation.

## Verification boundary

See [actual checkpoint](evidence/UXA-02-03.md). Node DOM simulation exercises the
real client and frozen scorer but is not Playwright or a visual review. Required
hosted full quality/readiness, all browser journeys, retained desktop/mobile
artifact inspection, Compose backup/restore and aggregate Pilot readiness are
still required before review/merge. No gate is removed to reduce cost.
