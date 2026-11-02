# Owner UX Test Feedback — 2026-10-07

Canonical backlog from the owner's staged hands-on test of Grounded Growth.

## Test stages and product rule

- **Pass 0 — before assessment:** no completed assessment.
- **Pass 1 — assessed, no practice started:** results exist but no practice has begun.
- **Pass 2 — active practice:** a practice is in progress.
- **Pass 3 — completed one practice:** a full practice/review loop is complete and the user needs the next one.

**Do not expose partial capability between stages.** A route, control, summary, or CTA should appear only when the user can meaningfully use it. Prefer hiding unavailable capability over debug-like placeholders, empty cards, or dead ends.

## Global UX/copy rules

- Write for an ordinary user with no knowledge of the assessment model, educational research, product internals, or psychometric terms.
- Major de-stilting pass across headers, subheaders, dropdowns, field labels, helper copy, empty states, and status text.
- Do not expose response-quality metrics, technical audit state, scoring metadata, calibration internals, raw priority percentages, or other backend terms unless needed for an end-user decision.
- Prefer concrete language: practice, action, review, why recommended, what to do next, what you completed.
- Make heading hierarchy obvious.
- Remove decorative yellow warning/info boxes unless actually actionable or safety-critical.
- OSS/self-hosting is the privacy model. The installer/admin owns hosting and data handling. Do not repeat privacy reassurance throughout normal UI.
- Put OSS/self-hosting/privacy/limitations on a dedicated **Disclaimer / Data Policy** page and repository docs; link it where relevant.
- Hover/focus help for non-obvious concepts must be keyboard accessible.
- Remove repetitive footer caveats from normal product pages and consolidate them on the disclaimer/data-policy surface.
- If a page has one obvious next action, make it dominant.
- Home should feel like a command center, not a documentation page.
- Login needs **Create account**.
- Before anything else, guide the user to one new action and keep focus on completing the current stage.
- Eliminate the unexplained 10-day practice window. Prefer **7 days** for the weekly loop; if a longer standard is needed, use **15 days**.

## Pass 0 — entry, home, login

### Entry / quick start / home

- Remove “demo”.
- Before assessment, show essentially one product intro: what Grounded is, how it works at a high level, then directly feed the assessment.
- Do not offer unrelated options before assessment.
- Move the four explanatory blocks from the top of Profile to the getting-started/pre-assessment page.
- “How it works” belongs on quick start/info, not normal Home.
- Update onboarding steps from actual progress and cross out completed steps.
- After one full loop, remove “Find a starting point”.
- Make the source of “Recommended next” understandable: assessment, direction, active/completed practice, history, and omit/reroll state as applicable.
- Combine redundant suggestion areas.
- If a suggestion can be rejected, give a plain reroll/omit action instead of “check their fit”.
- After first completion, Home should represent Personal OS/season when it affects planning/recommendations.

### Login

- Add **Create account** to the login GUI.

## Pass 1 — assessment

### Assessment taking

- Shortcut mode: pressing a valid 1–5 answer should submit/advance without Enter/Next.
- Major plain-language rewrite of assessment questions. Current copy is acceptable for a graduate-level technical user but QA users struggled.
- Rewrite the 1–5 answer labels/descriptions the same way.
- Preserve question meaning and scoring contract.
- Clarifiers are automatic/hidden product mechanics: 50 general questions then the required 8 clarifiers when applicable. Do not expose clarifier mode as a user choice.
- Hide assessment mode as an end-user setting. Keep compatibility internally; if a future version requires retake, say so directly.
- “Before you begin” expands only before a new assessment, not permanently after completion.
- If already taken: simple **Assessment complete**, **See results**, **Retake** state.
- Retake opens a popup/confirmation; do not keep a large blue retake section visible.
- Import is a button that expands options.
- Redo assessment header/footer in plain language.

### Assessment results / Profile

- Replace the current main Profile headline/copy.
- Remove/rewrite “neither…” subtext.
- Orientation/archetype cards: accessible hover/focus popup with roughly 2–8 sentences per result.
- Make card headers visually distinct from traits/sub-bullets.
- Move archetype/model caveats out of the footer to Disclaimer/Data Policy.
- “Signal / balancing work” gets a plain-language hover/focus explanation; remove confusing footer text.
- Move the four intro blocks to pre-assessment getting started.
- Hide response quality.
- Replace persistent share details with a **Share** button + popup.
- “Your week” belongs on Home/Status. Profile should be stable/global information.
- Remove yellow footer/status treatment.
- Do not show practice closeout content before a closeout exists.
- After completion: remove “final cut”; simplify completion cards.
- Reword “mapped completion coverage”.
- Remove/replace unexplained “remaining priority %”.

### History

- Make /history human-readable, not debug/application inspection.
- Remove or make unclickable demo/application/internal labels.
- Rewrite headings/subtext.
- Explain “periods” and their purpose; remove them if not important to user decisions.
- Fold /history/reuse into /history.
- Remove history/reuse entry points from Profile.

### Account / data

- Rewrite header/footer.
- Explain or remove “optional assessment calibration research”.
- Explain or remove unclear retention language.
- Add enumerated data policy linking to the OSS/self-hosting disclaimer page.
- Calibration implementation details appear only after explicit opt-in.

### Account / installation

- Assume container runner/admin is technically capable.
- Admin: concise instance/admin info.
- Non-admin: very cursory page, like mature self-hosted apps separate ordinary users from admin operations.
- Do not make the app a deployment tutorial.

### Account / pilot feedback

- Make feedback collection practical for a self-hosted OSS app.
- Preferred path: create/export/copy feedback into GitHub Issues.
- Do not imply feedback is centrally collected when it is not.

## Personal OS

### Route structure

- Do not show broad reuse unless reusable prior content actually exists.
- When reusable content exists, opening /personal-os may offer a simple import/reuse prompt. Otherwise hide database/reuse mechanics.
- Rewrite header/footer.
- Evaluate /personal-os/direction. If it duplicates a section of /personal-os, remove the redundant route and redirect compatibly.

### Form design

- Remove the green local/private/self-hosted reassurance box; move the sentiment to Disclaimer/Data Policy.
- De-stilt season/capacity. Show named, understandable choices rather than opaque scales.
- Internal numeric values may remain, but users should see meaning rather than unexplained 1 vs 4.
- First fillout/revision vs summary must be distinct.
- Fillout: one section at a time, auto-advance/hide prior sections where appropriate.
- Summary: concise fields, not the whole form repeated.
- Make “Identity directions” and other major sections visually stand out.
- For every prompt, make why it matters to the app understandable.
- Purpose: add examples and explain how it affects recommendations/planning; do not make it feel like generic journaling.
- Clarify “choose 1–5 principles”: 1–5 from what list?
- Apply the same rewrite to Truth/Autopilot and other abstract prompts.

### Personal OS practices

- Merge /personal-os/practices into /practices with redirect/backward compatibility.
- Remove “review a shortlist”.

## Practice selection / browser

- Make the browser more helpful, filterable, and intuitive.
- Suggested practices get a small context indicator + concise rationale.
- Clearly mark the current/in-progress practice.
- Fix “Review practice” pointing to a different version than the active work page.
- If omit/reroll is allowed, make it explicit.
- “Recommended next” must visibly update after start/completion.
- Remove “Open guide” from the main card if secondary; keep it where useful after selection.
- Remove compact check-ins unless clearly non-overlapping with normal check-ins.
- Hide backend copy such as “recommended priority is recalculated”.

## Practice guide

- Remove recursive/duplicated “teaching and materials”.
- Merge duplicate packet/sources areas into one clear resources/materials area.
- Do not show irrelevant sources for the selected practice.
- Rewrite guided-setup green-box copy.
- Remove “Not right now” when it creates a dead-end/partial state.
- Clean action cards that read like label: wall-of-text, label: wall-of-text.
- Do not use “intervention” in normal UI.
- Give observation checks and similar concepts one consistent, explicit treatment across practices.
- Remove vague phrases such as “self-aware” and “keep the lesson proportionate”.
- Consider moving introspection from Action 3 into a separate explicit **Reflection** step after substantive actions.

## Practice sprints / check-ins

### Sprint concept

- Define “practice sprint” in user language or stop exposing it as a special concept.
- Normalize compact vs normal check-in; remove one unless jobs are clearly different.
- Align sprint duration to weekly loop: 7 days preferred, optional 15-day standard if needed, not 10.

### Check-in copy/fields

- Rewrite direction/context wording.
- Remove excess privacy/withheld/absent-check wording from user screens; retain backend audit semantics only.
- Rewrite dropdowns as normal answers to the actual question.
- Submitted evidence hides technical-audit metadata.
- Do not render stacks of empty evidence labels.
- If only “action observable” is useful, show only that.
- De-stilt all possible fields.
- Remove nonsense such as “complete, return to what matters, and keep the lesson proportionate”.

## Weekly loop

### /weekly

- Define week boundary clearly. Investigate why a user starting 2026-10-06 saw a start of 2026-10-05.
- Remove warning-style subtext with no action.
- Empty direction: **No direction yet** + **Set direction**.
- Remove assessment-order/internal footer text from Context fit.
- If review requires a weekly plan, say **Create a weekly plan** and link directly.
- Remove yellow blocks.
- Move **Review direction** into the direction card; show summary + Review or Add direction if absent.
- Change “upcoming action — selection ok” to normal copy such as **Selected**.
- After completion, Current practice must stop presenting the completed practice as active.

### /weekly/plan

- Rewrite bold/helper copy.
- De-stilt dropdowns.
- Omit persistent “No submitted proof” when nothing exists yet.
- Remove yellow box.

### Proof-based review / completed state

- Give reviewed task/practice a clear header.
- Remove “return to what matters and keep lesson proportionate”.
- Replace raw label/value presentation such as “word: x, word: y”.
- “Act on your review” must not land on “No submitted proof for this plan”.
- Replace raw “Outcome: x” style labels with readable content.
- Provide an obvious next step after review.

## Evidence

- Rewrite subheader.
- Remove/rework yellow box.
- Remove vacuous evidence-reading items.
- Show direction as a plain selector where user choice is relevant.
- Cards need title + useful short summary/content, not placeholder label/value stacks.
- Move calibration export behind an explicit account/data button/popup.
- Rewrite categories such as “submitted evals” and “supported program”.

## Review / closeout

### /review / close

- Rewrite header/footer.
- De-stilt completion-evidence bubbles.
- Remove the always-visible closeout-credit explanation box.
- Prefer a conditional gate on the prior screen: greyed close button until requirements are met; hover/focus says what remains; enable when satisfied.
- Completion is not mastery.

### /review/complete

- Reword “experiment closed”.
- Remove yellow box.
- Give a clear next action.

## Pass 3 — post-completion

- Remove “Find a starting point” from Home.
- Weekly Current practice says/selects the need for a new practice.
- Completed review shows a readable summary then next practice/direction action.
- Profile completion record: no “final cut”, raw coverage jargon, or unexplained percentages.
- Recommended next visibly updates after completion.

## Acceptance matrix

Each implementation issue should add/adjust browser coverage for the relevant stage.

1. **Pass 0 fresh account**
   - login/create account
   - one clear onboarding path
   - assessment is the only substantive next action
   - no profile/practice/weekly partial states

2. **Pass 1 assessment complete**
   - results readable without internal terminology
   - orientation/archetype help works with mouse and keyboard
   - share/import/retake are collapsed actions
   - no closeout or empty weekly proof machinery

3. **Pass 2 active practice**
   - current practice is consistent everywhere
   - guide/actions/check-ins/weekly/evidence refer to the same practice/version
   - no dead ends or duplicate practice state
   - no technical-audit language in user UI

4. **Pass 3 completed practice**
   - readable completion summary
   - prior practice no longer current
   - home/weekly prompt the next practice
   - no “Find a starting point”
   - recommendations reflect completed work/direction state

5. **Copy/accessibility**
   - keyboard/focus access for popovers
   - no required info only on hover
   - clear heading hierarchy
   - no raw backend/debug labels in ordinary routes
   - assessment meaning/scoring preserved after copy rewrite

## Non-goals / invariants

This feedback does **not** authorize changes to assessment scoring mathematics, canonical IDs, evidence/replay semantics, completion-credit mathematics, recommendation algorithms except stale/incorrect UI state, Personal OS storage contracts except compatible presentation fixes, or specialist/validation claims.

This work is primarily UX copy, route consolidation, progressive disclosure, state gating, and browser acceptance.
