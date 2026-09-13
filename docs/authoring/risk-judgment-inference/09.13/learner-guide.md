# 09.13 — Statistical literacy

## The skill and its boundary

Read a numerical claim without losing its units, denominator, distribution, or sampling limits. Then distinguish a description of the observed data from a prediction or causal explanation.

**Canonical scope:** Understand distributions, sampling, uncertainty, correlation, effect size, regression, base rates, and misleading presentation.

**Deliverable:** A distribution/effect record, a small sampling exercise, a fitted-line interpretation, and a base-rate table, followed by two fresh checks. Use paper, a calculator, counters, or an accessible spreadsheet. No private data or specialist software is required. Plan two sessions rather than rushing the arithmetic. Every dataset below is invented; the methods do not authorize consequential statistical decisions.

The background distinctions about location, fitted lines, and sampling variability are supported in [R4–R6](../SOURCES.md). All numerical packets, answer calculations, and counterexamples here are original instructional work.

## A usable numerical reference

Write the unit of observation first: a person, a session, an item, or a repeated reading from the same item. Ten observations from one person are not ten independently sampled people.

The **mean** is the sum divided by the number of observations. The **median** is the middle ordered value, or the mean of the two middle values for an even count. A distribution is the pattern of values, not just either center. Report the minimum and maximum; the numerical **range** is maximum minus minimum. Listing the values can reveal overlap and outliers that an average conceals.

An **absolute effect** keeps the original unit: a two-minute difference. A **relative change** divides that difference by an explicitly chosen reference. A change in percentages can be expressed in **percentage points** without being the same as a percent relative change. A group difference does not establish an improvement for every individual.

**Sampling uncertainty** concerns what another sample could show. It differs from measurement error, missing data, and systematic selection. A larger sample may reduce random variation without repairing biased recruitment or a poor measurement. Do not invent a confidence interval simply because you have computed a mean.

**Correlation** describes an association. A regression line summarizes a fitted relationship under a chosen model; its slope is not automatically an intervention effect. **Regression toward the mean** is a different idea: selecting extreme noisy measurements can be followed by more ordinary measurements even without treatment. Neither term licenses erasing inconvenient observations.

## A different worked example: average is not typical for everyone

Three fictional waits are 2, 3, and 7 minutes. Their mean is 4, median is 3, minimum–maximum is 2–7, and range is 5. No one waited exactly the mean. If a second set has mean 3, the first-to-second mean reduction is 1 minute, or 25% of the first mean; that does not identify paired changes for the same individuals.

A bar chart starting at 2.9 could make bars at 3 and 4 look dramatically different. A labeled close-up can be useful, but it should not be presented as proportional bar lengths from zero. State the baseline, axis, units, and spread instead of treating a drawing as extra data. A scatter plot is often better for a relationship than bars that conceal pairing.

## Complete practice packets

### Packet D — Two selected groups

Two groups volunteered for different sorting methods; nobody was randomly assigned. The packet supplies no prior-experience measurements. All ten values are complete observed durations in minutes for the same nominal task, but the participants are different people.

| Group | Times in minutes |
| --- | --- |
| A | 8, 9, 10, 11, 12 |
| B | 6, 7, 8, 9, 10 |

Headline: **“The new method makes everyone 20 percent faster.”** There is no within-person before/after pairing and no experimental assignment. “Same nominal task” does not establish equal skill, motivation, or environment.

### Packet S — Sampling from a fully known toy population

Four distinct cards have values **2, 4, 6, 8**. Choose two different cards without replacement, with all six unordered pairs equally likely. This is a mathematical sampling model, not an actual population survey. Enumerate the six pairs and their means. Compare the mean of those six means with the mean of all four cards. One sample's variation is visible even though this toy population is completely known.

### Packet R — An observed relationship and a fitted line

Four fictional batches record label count x and completion time y in minutes:

| Batch | x | y |
| --- | --- | --- |
| R1 | 1 | 3 |
| R2 | 2 | 5 |
| R3 | 3 | 4 |
| R4 | 4 | 8 |

Fit y-hat = a + b x using:

`b = sum[(x − mean x)(y − mean y)] / sum[(x − mean x)^2]`

`a = mean y − b × mean x`

A **residual** is observed y minus fitted y-hat. The denominator must be nonzero; a dataset with no x variation cannot identify this slope. Use fractions or decimals. Calculate the slope, intercept, predictions for x = 2 and x = 5, and one residual. Notice that 5 is outside the observed x range. A straight-line extension is a model calculation, not a demonstrated completion time or a causal effect of adding a label.

### Packet B — Review flags and different denominators

In a fictional set of **100 items**, **10 truly need review**. The tool flags **8 of those 10** and also flags **10 of the 90 that do not need review**. All items have an independently stipulated true label in this teaching packet.

Create a two-by-two table: needs review / does not need review versus flagged / not flagged. Calculate the underlying review-case fraction, the fraction of true cases detected, and the fraction of flags that are true cases. State each as a count first, then an optional percentage. An 80% detection claim does not answer the question “How likely is a flagged item to be a true case?” unless the denominators are connected correctly.

### Action 1 — Describe what was observed before interpreting it

For D, list the values in order and calculate mean, median, minimum, maximum, range, absolute mean difference B minus A, and reduction relative to A. Describe overlap. Rewrite the headline in terms of this selected sample, retaining both the effect size and the missing causal comparison.

Do not settle the conclusion just by saying the sample is small. Identify the specific claim that fails: every individual improves, the method caused the difference, or the pattern generalizes to a target population. These are different claims requiring different evidence.

### Action 2 — Examine sampling, regression, and uncertainty

Work S and R independently. For S, show every possible pair, rather than selecting the one whose mean is most convenient. For R, show the two sums used for the slope and at least one observed-versus-fitted comparison. Explain why a small residual in one batch does not verify the model everywhere.

Now consider this separate noise model. An object's underlying value is always 10. Each measurement independently adds noise −2, 0, or +2 with equal probability. You select an object only after observing 12 on the first measurement. List its three possible second measurements and their mean. No treatment occurs. Explain how a later value below 12 could be mistaken for a treatment improvement. The result follows the stipulated independence model, not a claim that every extreme observation must move toward a mean.

For real data, uncertainty can come from unknown selection, changing conditions, imprecise measurement, or a weak model. Do not replace those limitations with a precise interval calculated under unstated assumptions.

### Action 3 — Keep the base rate and the practical claim separate

Complete B, then write a four-sentence interpretation covering: the detected fraction of actual cases; the true-case fraction among flags; the false positives and missed cases; and why a flag is evidence for review rather than certainty about the item.

Explain what changing the true-case base rate could do even if sensitivity and false-positive rate remained numerically the same. The fresh checks provide a second complete batch. These are harmless item-classification exercises, not diagnostic tests for people.

Before opening the separate answer key, save all four packet records and your revised headline. A correct final number without a visible denominator or contextual limit is incomplete statistical interpretation.

## Optional depth without extra prerequisites

For R, sketch the four coordinates on equally labeled axes and draw the fitted line. You do not need an artistic chart. The linear correlation can be calculated from the same centered sums, but correlation strength still does not distinguish a common cause, selection, or an intervention mechanism. A narrow prediction interval, if properly computed for another dataset, would concern prediction under its assumptions rather than settle causation.

Consider a bar display of the group means with no spread and the legend “20% improvement for all users.” Repair both the visual framing and the words. Conversely, do not claim that overlapping samples prove there is no population difference; overlap and uncertainty are not equivalent to proof of equality.

## Accessibility and progression

Use frequencies, counters, a spoken table, or a calculator. Keep labels, units, and denominators visible. Arithmetic assistance can be recorded separately from your interpretation. Do not make rapid mental computation the target skill.

For a harder route, choose two reasonable summaries that disagree because they answer different questions, such as mean and median under an outlier. State which question matters before choosing a favored summary. For later transfer, inspect an ordinary public claim, locate the actual denominator and sample definition, and report missing information without inventing it. Do not use the lesson to self-interpret consequential health, financial, or safety evidence.

## Interpret the result

**Supportive:** Centers, spread, denominator, model, and selection limits are visible; the headline narrows without discarding the observed difference. **Mixed:** Arithmetic is correct but regression is described as causation or flags are confused with true cases. **Contradictory:** An outlier is removed merely to favor a result, or a group mean becomes an individual guarantee. **Inconclusive:** Only the headline's percentage is repeated.

**Final review:** Which denominator, comparison, or modeling assumption most changes what you may responsibly conclude?
