# 09.16 — Models, simulations, and abstraction limits

## Purpose and a useful finish

Use a model to answer a specific question, then identify where its assumptions stop supporting the answer. A formula can be calculated correctly and still misrepresent the situation. A more detailed model can also be less useful when its additional parameters are unsupported.

**Canonical scope:** Use models as purposeful simplifications while tracking assumptions, sensitivity, validation, and domains of failure.

Your deliverable is a model card, predictions saved before opening a later data packet, a sensitivity table, and a versioned decision about permitted use. Allow two 15-minute sessions and a short review. Use paper, a calculator, speech-to-text, or an accessible text editor. All required data are supplied; no physical experiment, coding, or timing of another person is required. The numerical task is fictional. Actual model validation requires observations of the real intended process.

## Reference: six questions that keep a model honest

**Purpose:** Which decision will the output inform? “Estimate an ordinary batch's completion time” is narrower than “measure whether a person works hard enough.” An answer useful for rough planning may be inadequate for a safety decision.

**Representation:** What are the inputs, outputs, units, boundaries, and rules? A conceptual model is your account of the process; a spreadsheet or program implements it; a simulation is a particular run. Do not confuse a neat display with a complete account of reality.

**Assumptions:** Which conditions are treated as fixed or omitted? An assumption can be reasonable without being a universal fact. Give each important assumption a possible failure signal.

**Verification:** Does the calculation implement the stated model? Check units, hand-worked cases, and boundary inputs. A program that evaluates your formula correctly has passed this particular implementation check, not every possible test.

**Calibration and validation:** Adjusting parameters to match fitting data is calibration. Comparing frozen predictions with relevant, independently obtained observations addresses validation for a specified use. Reusing the same fitting observations does not provide an independent validation set. NASA's modeling terminology provides background for this distinction; this exercise is not NASA qualification. See [source notes](../SOURCES.md).

**Sensitivity and use limits:** How far does the result move when uncertain inputs change? A sensitivity interval is not automatically a statistical confidence interval. Identify the inputs or conditions that would reverse the decision, and define what you will do when the model is outside its evidence base.

## Different worked example: a walking-time estimate

A toy route model assumes constant speed: time equals distance divided by speed. For 600 metres at an assumed 60 metres per minute, it gives 10 minutes. The units reduce to minutes. A correctly written calculator can reproduce that arithmetic while ignoring crossings, access requirements, stops, terrain, and changes in pace. This is a fictional arithmetic example, not a recommended walking speed or a physical capability assessment.

Adding a fixed crossing delay could improve this route's fit but would require evidence for that delay. Doubling the distance does not establish that the same speed remains appropriate. Keep the original model and record why a revised version needs another check.

## Complete practice packet: ordinary sorting batches

A fictional operator sorts lightweight paper cards. A “batch complete” observation includes preparation and placement of the final card. The following two records were used to fit a model; both concern ordinary cards, one operator, one station, and uninterrupted work.

| Record | Number of cards | Observed total time |
| --- | --- | --- |
| F1 | 2 | 11 minutes |
| F2 | 4 | 17 minutes |

The candidate model for a positive whole-number batch is `T(n) = s + p*n`, where `s` is preparation time in minutes and `p` is minutes per card. For no batch, define `T(0) = 0`; no preparation is performed. Negative, fractional, missing, or non-finite card counts are invalid inputs, not valid negative or partial batches.

The original fitted version is **M1: s = 5, p = 3**. These parameters match F1 and F2. They are toy estimates from two records, not constants of human performance. A decision-maker asks whether an ordinary six-card batch can be promised within **25 minutes**. The candidate may inform planning, but a promise requires considering uncertainty and consequences separately.

For this exercise, plausible sensitivity assumptions are `s` from 3 to 7 and `p` from 2 to 4. No probabilities or distributions over those values are supplied. Assume independent variation is allowed for the endpoint calculation; that is a modeling choice, not a measured independence claim.

### Action 1 — Write the model card and verify its implementation

Copy this form and fill it before looking at the later packet:

`Version | intended decision | inputs and units | output and units | formula | fitting records | included process | omitted factors | proposed use limits | failure signal | next action if it fails`

Calculate the predictions for 0, 2, 3, 4, and 6 cards. Show the substitution for at least one positive count and explain the zero-batch rule. Check whether the model would silently accept half a card or confuse minutes per card with cards per minute. These are implementation issues, not excuses to remove inconvenient observations.

List at least three omitted factors, such as interruptions, different card handling, learning or fatigue, and station changes. Tie each to the intended sorting-time use. Specify a review trigger in advance: **an absolute prediction error greater than five minutes, or a changed handling category, suspends use of M1 for that condition**. Five minutes is an authored toy threshold, not an industry standard.

### Action 2 — Freeze predictions and test decision sensitivity

Save M1's prediction for three ordinary cards and for six cards marked “special handling.” Predict numerically even though the latter is outside the ordinary fitting conditions; label that second prediction **extrapolation across a changed condition**, not supported ordinary use.

For the six-card planning question, calculate all four combinations of the low/high setup and per-card values. State which parameter's full specified range contributes more variation at six cards. Decide whether the 25-minute promise is robust across these assumptions. Do not convert the proportion of endpoint cases below 25 into a probability: the packet supplies no likelihood for those cases.

Record the predictions, the sensitivity range, and your promise decision before opening **later-packet.md**. Merely reading a hidden result and then writing “I predicted it” defeats this part of the exercise. Disclose prior exposure if you have already seen the packet; use the fresh checks for another attempt instead.

### Action 3 — Compare held-out observations and restrict the claim

Open the later packet. For each record, calculate `observed minus predicted`, its absolute value, and whether it triggers the prespecified rule. Keep category differences visible. A large error is information about model adequacy; it is not automatically an error in the observation.

Choose to retain M1 for a narrower planning use, collect more relevant observations, or propose a revised M2. Do not announce M2 as validated on the data used to invent it. Write what additional ordinary and special-handling cases would challenge the revised representation, which assumptions need measurement, and what decision remains unsupported.

Your conclusion must distinguish three things: correct arithmetic, agreement with a particular held-out example, and credibility for the contemplated use. One ordinary holdout does not establish every batch size, deadline, operator, or environment. The supplied records are fictional held-out exercise material, not a real-world validation experiment.

## Fresh checks and corrective guidance

Attempt both checks in **check-prompts.md** before opening **check-answers.md**. The first separates verification from validity of the representation. The second shows why identical fit within one range can coexist with very different extrapolations. The main-practice key is also separate so the worked example does not give away your practice verdict.

## Adaptations, progression, and an honest completion boundary

Use a calculator, prewritten substitution lines, spoken arithmetic, or a reader who transcribes your choices. Keep units and missing-data distinctions even when simplifying the form. No speed criterion applies. Record help that selects an answer rather than merely presenting information.

For a more demanding route, vary batch size as well as both parameters, plot or tabulate the outputs, and identify where decision robustness changes. To investigate multiple workers, write a new process model; do not assume that every component of total time halves. Preparation or a shared station may remain a bottleneck.

For later live transfer, select a harmless process you control, obtain observations with permission, freeze the model before collecting comparison cases, and retain failures. Do not collect another person's work-rate data or infer diligence, disability, or worth. Defer safety-critical, clinical, legal, or regulated uses to appropriate expertise.

**Supportive:** Predictions were recorded before reveal, the failure threshold was applied consistently, and the use statement narrowed after a category-dependent error.

**Mixed:** The arithmetic is right, but a changed condition is accepted as routine without explaining why the assumptions still hold.

**Contradictory:** The failed case is deleted, a refit is called independent validation, or a planning model becomes an unsupported judgment about a person.

**Inconclusive:** A formula is written and fitted, but no held-out prediction, sensitivity calculation, or use boundary is produced.

**Final review:** What does the model deliberately leave out, which result makes that omission consequential, and what can you responsibly do before obtaining stronger evidence?
