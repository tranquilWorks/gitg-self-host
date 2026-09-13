# 09.08 — Root-cause problem solving

## What you are practicing

Turn a recurring failure into an observable question, compare explanations that predict different results, and verify a correction on fresh cases. A plausible explanation is a starting point; a fix that looks successful is not automatically evidence of a unique root cause.

**Canonical scope:** Define the problem, distinguish symptoms from causes, gather evidence, test hypotheses, and verify improvement.

**Deliverable:** A problem definition, competing-hypothesis table, four-condition paper test, fresh verification record, and maintenance decision. Allow about 40 minutes. Use paper cards, a text editor, a calculator, or dictation. You need no electrical equipment, live service, other participant, or private data.

The default is a deterministic simulation. It can establish what the specified routing rules do, but not that an actual person's routine improved. The canonical progress indicator concerning a recurring real problem remains untested until a suitable real process is observed. This material is unscored educational source, not a new production evidence contract.

## A reference for causal investigation

A **symptom** is the observed failure: a form reaches the wrong tray. A **cause hypothesis** proposes a mechanism: the instruction uses the wrong digit. “People are careless” is neither a measured mechanism nor a discriminating explanation. A process may have several interacting contributors rather than one privileged cause.

A **baseline** records outcomes before the proposed correction using a fixed definition and denominator. Preserve missing cases. A **containment** limits immediate consequences without necessarily removing the cause; holding an unreadable form is containment. A **corrective action** changes the proposed mechanism. **Verification** asks whether the correction works on suitable new opportunities and whether it creates another problem.

A **discriminating test** produces different expected observations under competing explanations. Changing one variable while holding others fixed can make a comparison clearer. It is not a universal rule that every investigation must change only one factor forever: a planned set of combinations can expose interacting conditions. NIST's experimental-design references in SOURCES.md distinguish design choice, factors, and run order. Our four-condition exercise is a stipulated model, not a randomized human trial.

Separate observation, hypothesis, intervention, and conclusion in your record. Keep your initial explanation even when it loses support. Repeating a successful test on the same cases is useful regression checking; fresh cases check something additional. Neither replaces the other.

## A different worked example: an unreadable address

A postcard lacks its final address line. Holding it for clarification prevents a guessed delivery, but does not supply the missing address. Reporting “zero wrong deliveries” while every postcard remains on hold would hide a service failure. A complete correction needs the right information and a process that uses it correctly.

This example separates safe containment from effective completion. It also explains why a denominator needs categories beyond success/failure: correctly completed, incorrectly handled, held, and unobserved can mean different things.

## Complete practice packet: the paper-routing desk

A fictional club routes paper slips. A valid code has **exactly two ASCII digits**, such as 12 or 77. Its **last digit** determines the destination: odd goes **L**, even goes **R**. If either digit is missing or the code is malformed, the correct action is **H**, hold for clarification. “1?” therefore belongs in H, not a guessed tray.

This is the authoritative task requirement, called **Spec S2**. It applies regardless of what a posted instruction card says. A lucky destination guess is still an incorrect handling decision when the visible information requires H.

The posted old card, **Card V1**, instructs the clerk to use the **first digit** and ignores whether the second digit is visible. The proposed new card, **Card V2**, instructs the clerk to validate the two-digit code, hold any invalid code, and otherwise route using the last digit. In this simulation the clerk follows the selected card exactly. This assumption removes attention, memory, and practice effects; it cannot tell us how real people respond to either card.

### Input deck and feed conditions

The complete baseline deck is:

`12, 21, 34, 43, 11, 22, 33, 44`

**Full feed** shows both digits. **Masked feed** replaces the second digit with a question mark, retaining order:

`1?, 2?, 3?, 4?, 1?, 2?, 3?, 4?`

These are two representations of eight corresponding records, not sixteen independent sampled people. The hidden original digits are provided for author checking only; a clerk receiving the masked feed must not use them to guess. No records are dropped because they are inconvenient.

For each attempted record, log these fields:

`Record number | original code | visible code | card version | required handling from visible code | chosen handling | compliant? | completed L/R or held H`

A valid full code correctly sent to L/R is completed. H is appropriate containment for unreadable input, but is not completed delivery. Count **total attempts, compliant decisions, violations, correctly completed, wrongly routed or guessed, and held**. These are related categories, not numbers to add indiscriminately: compliant decisions include both correct completion and appropriate holds.

### Action 1 — Define the problem and make competing predictions

State the problem without a character judgment: “The desk does not consistently complete slips according to Spec S2.” Name the outcomes you will measure and preserve the eight-record denominator for every condition. Distinguish incorrect handling from noncompletion.

Write at least these three candidate explanations and their predictions:

- **H1: The posted digit-selection rule is wrong.** Changing V1 to V2 should remove full-feed misrouting without changing the input deck.
- **H2: The feed loses information needed for completion.** Even a correct card should be unable to complete masked records without clarification.
- **H3: The problem is only attention or insufficient effort.** A simulated clerk following explicit instructions exactly can help test whether the written process itself already contains a defect. It cannot rule out attention effects in a different real setting.

Use `hypothesis | expected contrast | observation that would count against it | what this simulation cannot test`. Do not frame H1 and H2 as mutually exclusive merely to force one winner. A symptom can have both an incorrect rule and unusable input upstream.

Before revealing any result, predict how each of the four conditions should differ. In particular, state whether “fewer wrong routes” will necessarily mean “more correct completions.”

### Action 2 — Run the four conditions and retain every record

Apply V1/full, V2/full, V1/masked, and V2/masked separately to the same baseline deck. Reset the deck between conditions. Follow each written card literally; do not silently improve V1 because you know the correct specification.

For V1, use the first visible digit: odd L, even R. For V2, first require exactly two ASCII digits; otherwise H. Then use the last digit: odd L, even R. You can move cards, speak their destinations, or write them. Log assistance and any actual departure from the simulated rule.

Make a summary:

`Condition | attempted | violations | correctly completed | held | what mechanism this contrast supports`

Compare V1/full with V2/full to isolate the instruction difference in this stipulated process. Compare V2/full with V2/masked to isolate information availability under the corrected instruction. An observational “before” with full inputs and an “after” with masked inputs would mix factors and obscure the interpretation.

Keep the test safe and synthetic. A real counterbalanced or randomized run can help with order and learning effects when appropriate, but a fixed sequence on yourself would not become an independent trial simply because it has four rows. Do not claim a p-value or human causal effect from the model's stipulated behavior.

After saving the predictions and all records, open **test-results.md**. Treat any mismatch as a reason to inspect the exact rule, visible input, or your recording before declaring the answer wrong.

### Action 3 — Verify on fresh inputs and define what is actually fixed

For the candidate corrected process, use V2 and full inputs on this fresh deck:

`58, 85, 66, 77, 92, 29, 24, 35`

The acceptance target is **8 correctly completed, 0 violations, and 0 holds**. Keep the same definitions as baseline. This tests new code combinations, not durability across time or contexts.

Then deliberately challenge the paper rule with `8?`, `?2`, `123`, and `A2`. Each should be H. This is a separate invalid-input test with **4 appropriate holds**, not an extension of the completed-delivery denominator. Never count these four safe holds as four completed slips. No real record or service is modified for the challenge.

Write the correction as a two-part process requirement: maintain the correct card and deliver complete usable codes. The masking test shows why updating the card alone cannot restore completion when the upstream feed still clips information. Do not quietly assume the real upstream problem has been fixed because the synthetic full deck works.

Create a maintenance record:

`Spec version | exact card version | tested feed conditions | baseline and verification decks | acceptance result | unresolved failure | owner/authority | recheck trigger | reversible fallback`

A suitable recheck trigger is any instruction or input-format change. The fallback for ambiguous input is clarification or H, not reinstating a known wrong rule. In an actual low-stakes process, retain unedited observations, record context changes, and inspect whether completion stays improved without burden being moved elsewhere. Missing opportunities remain missing.

## Fresh checks, Accessibility, and progression

Complete both checks in **check-prompts.md** before reading **check-answers.md**. One tests a confounded explanation; the other tests an improvement claim that hides held work. Their evidence limits differ from deterministic code routing.

For Accessibility, use large code cards, audio digits, or a reader who states exactly the visible code. Keep the missing marker explicit; a helper must not fill in a hidden digit. Use the same outcome categories even when speaking the record. There is no speed criterion.

For a more demanding route, enumerate every two-digit code from 00 to 99 under full inputs. Record how many V1 routes differ from Spec S2 and whether V2 matches every one. That is exhaustive verification for this finite two-digit rule, not proof about arbitrary strings, ambiguous printing, or actual clerks. Extend a domain only after defining its validation requirements.

For live transfer, choose a harmless process you control and a fixed opportunity window. Preserve at least two competing explanations, a baseline, a discriminating change, and verification using the same outcome definition. Avoid experiments involving electricity, machinery, essential care, confidential records, or another person's belongings. Seek appropriate expertise for consequential failures.

## How to interpret your result

**Supportive:** The problem and denominator are fixed; the four conditions separate rule error from missing information; fresh tests distinguish completion from appropriate containment; the remaining upstream issue is acknowledged.

**Mixed:** V2/full works, but the learner calls every H a success or generalizes the result to human attention without evidence.

**Contradictory:** The clerk guesses masked codes, inconvenient records disappear, or a corrected card is declared a complete fix while the feed remains unreadable.

**Inconclusive:** A preferred solution is announced without preserved baseline, competing predictions, record-level checks, or fresh verification. The real-world progress indicator remains open after simulation alone.

**Final review:** Which contrast discriminated between explanations, which mechanism remains unresolved, and what evidence would justify calling the process improved rather than merely contained?
