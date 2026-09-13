# 09.06 — Probabilistic and scenario thinking

## What you will produce

Three forecasts recorded before resolution, a base-rate calculation, a scenario and sensitivity comparison, and a later review that distinguishes probability accuracy from calibration. Allow 20 minutes for preparation and 20 minutes for review. The fictional outcomes are in a separate file. A live route needs actual later observations; they cannot be replaced by invented results.

**Canonical scope:** Use ranges, likelihoods, base rates, scenarios, sensitivity, and expected value instead of binary predictions.

Use paper, a calculator, or a text editor. All arithmetic and source records are supplied. This is low-stakes forecasting education, not betting, investing, medical prognosis, or safety-critical planning. A forecast score is an exercise diagnostic, not a score of personal worth or a new application scoring rule. Background references S4 and S5 are in SOURCES.md.

## The reference you will need

A probability describes uncertainty about a defined event: 0.8 means eight in ten comparable instances as a frequency interpretation, not a guarantee about the next one. A **base rate** is an observed event proportion in a relevant reference set. Its denominator and relevance matter. Ten selected cases do not reveal a precise universal probability.

A **probability range**, such as 0.6–0.9, expresses uncertainty about your probability judgment here; it is not automatically a statistical confidence interval. A range of **outcome values**, such as 0–12 minutes of delay, is a different object. Label what a range describes. Do not choose or narrow either after seeing the outcome and present it as a prior forecast.

A **scenario** asks what follows under specified assumptions. It is not necessarily a prediction or equally likely to other scenarios. **Sensitivity** asks whether a decision changes when an uncertain input changes. **Expected value** averages consequences weighted by their probabilities under a model; it is neither a promised result nor a command that overrides duties, access, or severe consequences.

For a binary event, probability accuracy can be summarized with the mean of `(p - y)^2`, where `p` is the recorded probability and `y` is 1 when the event occurred and 0 when it did not. This is the binary **Brier score** used here; smaller is better on the evaluated set. It is not calibration by itself. Calibration compares predicted probabilities with observed event frequencies over many suitably comparable forecasts. Sample size, dependence, and changes in context still matter.

## Different worked example — a rehearsal handout

Suppose a fictional workshop has a 0.25 probability of needing extra handouts. Printing a spare packet always takes 2 minutes and avoids 12 minutes of disruption only if the need occurs. Under those assumptions, expected avoided disruption is 0.25 × 12 = 3 minutes, minus 2 minutes of preparation: net expected saving 1 minute. In a single workshop, the net is either 10 minutes saved or 2 minutes spent without use, not necessarily 1 minute.

The break-even probability is 2/12 = 1/6. Paper use, limited supplies, and access requirements are omitted. A duty to provide an accessible handout could settle the action independently of this time-only comparison. This is a model, not a recommendation to gamble with another person's access.

## Complete initial packet — meeting starts

All meetings below are fictional ordinary club meetings. The event is **the chair begins the first agenda item no later than five minutes after the advertised start**. Use the chair's recorded opening time, not attendance or your arrival. For this packet the clock and record are stipulated accurate.

Ten earlier meetings at the same club and usual room have these recorded delays in minutes:

`H1=0, H2=2, H3=1, H4=4, H5=5, H6=0, H7=3, H8=2, H9=9, H10=12.`

The packet includes every meeting in that stated ten-meeting period. It supplies no earlier periods or claim that conditions remain unchanged forever. Three upcoming meetings, F1, F2, and F3, use the same advertised time and usual room. No additional differences are supplied. Absence of a reported difference is not proof of identical future conditions.

**Resolution rule:** Resolve each at advertised start plus 30 minutes from the chair's opening record. A start after five minutes, or a verified failure to start by 30 minutes for a meeting that was not cancelled, is `y=0`. A start by five minutes is `y=1`. A cancelled meeting is **void**, and a missing or conflicting opening record is **unresolved**; retain those entries and reasons but do not silently score them as late. This rule is set before the outcomes.

Do not open `outcomes.md` yet. Record any accidental prior exposure rather than claiming a prospective forecast afterward.

### Action 1 — Set the reference rate and preserve three forecasts

Count the successes in H1–H10 and show the fraction. Describe the reference set, threshold, denominator, and one reason the future probability could differ. The observed delay range is descriptive history, not a guaranteed prediction interval.

For each of F1–F3, write:

`Forecast ID | record order/time | exact event | reference set | base rate | point probability p | optional probability range and meaning | context adjustment and reason | resolution rule | outcome not yet viewed`

Use the historical rate as a starting point. Keeping it unchanged is allowed when there is no justified adjustment. Do not invent different contexts merely to make the three probabilities look individualized. A defensible uncertainty range is a judgment to explain, not an answer the key will declare objectively correct.

Choose the point probability before resolution if you intend to compute the Brier score. A range alone does not define one score; do not pick the most favorable point afterward. You may instead retain a range-only record and state that a single-point score was not specified.

### Action 2 — Compare scenarios and locate the decision threshold

Use this **time-only toy model** for an optional preparation action. Arriving early incurs 5 minutes every time. It avoids 15 minutes of disruption if the meeting starts by the defined threshold and avoids nothing otherwise. The early action does not itself affect when the meeting starts. These are stipulated model inputs, not measured facts about real meetings.

Complete the table without opening the answers:

| Scenario probability p | Expected avoided disruption | Certain time cost | Net expected time saving |
| --- | --- | --- | --- |
| 0.3 | Calculate 15 × p | 5 minutes | Calculate 15 × p - 5 |
| 0.8 | Calculate 15 × p | 5 minutes | Calculate 15 × p - 5 |
| 0.9 | Calculate 15 × p | 5 minutes | Calculate 15 × p - 5 |

Solve `15 × p = 5` for the break-even probability. Under a probability range 0.6–0.9, calculate the corresponding net-saving range. State whether that range crosses the threshold. Do not assign equal probabilities to the three scenarios merely because there are three rows.

Write at least two model limits: the cost may not be exactly 5, the avoided disruption may not be 15, or obligations and access requirements may override a time comparison. Compare both realized possibilities as well as the expected value. Choose an action only within the toy assumptions, not as a rule for every appointment.

### Action 3 — Resolve, score, and review without editing history

Save all forecasts and scenario calculations. Open `outcomes.md`, apply the rule to each record, and append the result beside the original probability. Keep the fictional route labeled **simulation**. For a live route, use actual records and preserve void/unresolved cases with reasons.

Calculate each squared probability error and their mean for the scored cases. State the number excluded and why. A likely event can fail to occur without proving its earlier probability was irrational. Conversely, a fortunate outcome does not justify an unsupported confident forecast.

Use this review form:

`Original forecasts retained | resolved outcomes and sources | scored / void / unresolved counts | accuracy calculation | reference-set limitation | possible explanation of errors | what cannot be inferred | next recording or model improvement`

Do not choose a winning model or declare broad calibration from three forecasts. A missed outcome could reflect chance, a poorly chosen reference set, or an unjustified adjustment; this tiny record may not discriminate among them. Choose a concrete improvement such as recording all comparable meetings or documenting a material context change. Do not assert which explanation caused the error without evidence.

## Fresh checks: resolution and calibration are different tasks

Complete both checks in `check-prompts.md` before opening `check-answers.md`. Check A includes a genuine probability error plus void and unresolved records. Check B supplies a larger, explicitly synthetic audit set so you can actually compare probabilities with frequencies. Its numbers do not certify a real forecaster.

## Accessibility and live progression

Use frequencies, a calculator, or a reader who records your chosen probabilities without suggesting outcomes. There is no mental-arithmetic or speed requirement. Keep point forecasts distinguishable from ranges and assistance distinguishable from independent judgment.

For a live continuation, choose ordinary meetings you are authorized to observe; define the event, reference set, and missing/cancelled rule beforehand. Record forecasts prospectively and return when they resolve. Use no private information about other attendees. More forecasts can improve the basis for review, but no arbitrary count automatically proves calibration.

For a more demanding analysis, define probability groups before examining outcomes and report each group's count, mean forecast, and observed frequency. Inspect whether forecasts come from comparable conditions and whether multiple entries share the same event. Small groups remain uncertain, and repeatedly changing bins to look well-calibrated is not evidence of improvement. A new model or scoring convention should begin a labeled version, not rewrite earlier predictions.

## Interpreting the result

**Supportive:** The base-rate denominator, prospective forecasts, threshold calculation, resolution rules, and later accuracy/calibration distinctions are visible and correct.

**Mixed:** Forecasts were preserved, but a probability range was treated as a confidence interval without a method, or unresolved cases disappeared from the review.

**Contradictory:** Forecasts were edited after the results, a high probability was presented as certainty, or expected value was used to override an important access or safety duty.

**Inconclusive:** There is only a retrospective success rate, without recorded probabilities, an event definition, or a resolution rule. A simulated audit is not demonstrated real-world calibration.

**Final review:** Which part of your forecast was supported by a reference set, which part was judgment, and what additional record would help distinguish poor modeling from ordinary uncertainty?
