# 09.15 — Causal inference and intervention logic

## The skill and its boundary

Explain why an observed association may differ from the effect of changing something. Specify the intervention and comparison you actually mean, then identify what evidence and assumptions could connect them.

**Canonical scope:** Distinguish association from cause and examine mechanisms, counterfactuals, selection effects, and unintended consequences.

**Deliverable:** An association record, a causal hypothesis map in words or arrows, a counterfactual statement, and an ethically bounded intervention proposal. Two fresh checks test whether the same observed outcomes can support different hidden causal stories. Allow two short sessions and use a calculator if useful. Everything is fictional; no institutional intervention or experiment on people is authorized.

[R8](../SOURCES.md) supplies the limited background distinction between an observed statistical quantity and a causal quantity defined by an intervention. The finite examples below demonstrate that distinction with original arithmetic rather than claiming identification from a citation.

## Begin with the exact question

An **association** compares observed outcomes across groups. A **causal question** compares what would happen under specified alternatives for a target population. “People who attended did better” is different from “offering access improves outcomes,” “attending improves outcomes,” and “requiring attendance improves outcomes.” Each changes something different and may affect different people.

A **mechanism** is a proposed route from an action to an effect, such as access leading to practice and practice to completion. A plausible route is not proof that it operated. A **counterfactual** describes the outcome under an alternative condition not actually experienced in the same instance. In real data, a person contributes the outcome under the condition they experienced, not both potential outcomes at once.

**Selection** matters when the people who take up, remain in, or are measured under an option differ from the comparison group. Statistical adjustment for measured differences cannot prove that all unmeasured differences disappeared. Random assignment can improve the comparison for the assigned intervention under its assumptions, but uptake, missing outcomes, spillovers, measurement, and generalization still need attention.

## A different worked example: the umbrellas do not establish the cause

A fictional log shows more wet shoes among people carrying umbrellas than among people without umbrellas. Rain could increase both umbrella use and wet shoes. Removing umbrellas would not necessarily improve the outcome just because umbrella carriers looked worse in that log. Conversely, an umbrella might have a genuine protective effect that the crude comparison conceals.

Specify time order: rain was present before the umbrella choice; wet shoes were measured afterward. A post-outcome explanation cannot simply be relabeled a pre-choice cause. To distinguish the stories, inspect relevant conditions or a justified comparison. A slogan about correlation is insufficient without identifying a plausible common cause and the intervention of interest.

## Complete study-support packet

All counts below are invented and complete for their stated cells. People voluntarily chose whether to attend optional study support. Preparedness was measured **before** attendance. Completion is a binary indicator for a harmless practice exercise. No assignment was randomized, and the packet does not measure all motivation, time, or support differences.

| Prior group | Attended: completed / total | Did not attend: completed / total |
| --- | --- | --- |
| Prepared | 18 / 20 | 72 / 90 |
| Beginner | 27 / 90 | 4 / 20 |

A commentator says: **“Attendance lowers completion; we should remove the support.”** Another says: **“Within both groups attendance is better, so compulsory attendance will raise everyone's completion.”** Neither policy is established just by accepting its preferred table view.

The program is optional. Some people have caregiving, work, or access constraints; no personal records are provided. Compulsory attendance could displace other useful activity. A voluntary offer at a usable time, actually attending, and a mandate are different interventions.

### Action 1 — Compute the observations and inspect selection

Calculate each cell's completion fraction, each column's overall fraction, and the observed attendance-minus-nonattendance difference within each prior group. Preserve every denominator. Then calculate a descriptive standardized comparison giving the two prior groups equal weight in each attendance condition.

The equal weights define a particular target composition for the arithmetic; they do not demonstrate that this is the actual intended population or that adjustment identifies causation. Explain why the crude and within-group patterns differ. Do not average percentages without stating their weights.

Write the association without causal verbs. For example, “In this selected sample, the crude attendance group had…” is an observed description, not a claim about what would happen if a given person were forced to attend.

### Action 2 — Map the mechanism, common causes, and missing counterfactual

Use these variable cards, whose arrows are hypotheses except for the stipulated time order and observed membership:

`P: prior preparedness. R: available time/access before the offer. T: attendance. M: practice with feedback after attendance. Y: completion. S: whether the final outcome is observed.`

Draw or describe possible links P→T and P→Y; R→T and R→Y; T→M→Y. State what evidence would be needed to support each. The table establishes group counts, not every arrow. A person's motivation could be another unmeasured common cause.

Distinguish **practice before attendance**, which might contribute to selection, from **practice produced after attendance**, which might mediate an effect. Blindly adjusting for both as if they played the same role can change the causal question. Holding post-attendance practice fixed would not generally estimate the entire effect operating through practice.

For a target learner, write: “Compare completion if offered this accessible support with completion if not offered it, over this defined period.” Then explain why a mandated-attendance question is different. You cannot observe both outcomes for the same person in the same instance; a later retake also changes time and experience.

If only completers are surveyed, inspect who is excluded and why. Selection into observation after the intervention can create a misleading comparison. Do not treat an improved percentage among the remaining observed people as proof that the total population improved.

### Action 3 — Propose a comparison and an intervention boundary

For the fictional organization, propose an **accessible voluntary offer**, not a mandate inferred from a correlation. Define the target, offer content, comparison condition, period, and completion measurement. A suitably governed randomized offer could compare outcomes by original offer assignment, with all assigned people accounted for; this is a design proposal, not an experiment performed here.

List what would remain uncertain: adherence, spillovers, missing outcomes, measurement validity, different access needs, or whether results generalize. An observational comparison with measured preparedness may be informative under explicit assumptions, but those assumptions must not be hidden behind the word adjusted.

Name at least two possible unintended effects and a safeguard: displaced independent study, burdensome scheduling, loss of access, unwanted pressure, or diversion of staff attention. Expansion should require more than an improved convenient metric. Include participant burden, consent, missing outcomes, and any deterioration in another important outcome. Only the appropriate owner can authorize an actual study or service change.

Save a bounded recommendation with three parts: what is observed, what causal claim remains unestablished, and what additional comparison could justify a next decision. Complete both fresh checks before opening their separate key.

## Counterfactuals as a test of what the data can identify

For a binary outcome, label the potential results **Y0** without attendance and **Y1** with attendance. For any one person in the fresh exercise, only one is observed. An individual effect Y1−Y0 can be −1, 0, or +1; an average effect compares the same target people under both conditions, not arbitrary selected groups.

The fresh four-person packet lets you fill the unobserved values in different ways while preserving every observed fact. When two such worlds give opposite average causal effects, the observed data alone cannot choose between them. This does not mean causal knowledge is impossible; it identifies the additional assumptions or design information needed.

The hidden-value exercise is a mathematical demonstration. It does not infer anyone's private characteristics or license filling in missing real outcomes as facts.

## Offer effects, attendance effects, and unintended changes

If an offer is randomly assigned and outcomes are observed appropriately, comparing original assignment groups concerns the **offer**. Restricting to those who attended creates a selected comparison. Dividing an offer-group difference by an uptake difference to announce an attendance effect requires further assumptions; do not do it automatically.

Likewise, a policy may change the mechanism itself. Mandatory attendance may reduce autonomy or displace learning time in ways absent from voluntary support. The people whose behavior changes under a mandate may not resemble voluntary attendees. A causal story should describe these pathways, not merely move an observed percentage into a policy recommendation.

## Accessibility, progression, and transfer

Use arrow cards, plain sentences, or a narrated table. A helper may calculate fractions; the interpretation of the intervention and limits remains yours. No software or personal dataset is required. Keep distinct labels for observed facts, stipulated fictional facts, and hypotheses.

For a harder route, distinguish pre-intervention selection from post-intervention selection into measurement. Explain why adding more covariates is not automatically a repair: their timing and causal roles matter. Specify a causal question before selecting an adjustment set.

For later transfer, analyze an ordinary published policy claim with its real methods. Missing methodological information stays missing. Consequential services and research on people need appropriate expertise, authority, consent, and oversight beyond this exercise.

## Interpret the result

**Supportive:** The denominators, intervention, counterfactual, mechanism, and selection limits are explicit; the proposal considers affected people. **Mixed:** A mechanism is plausible but treated as demonstrated, or measured adjustment is overstated. **Contradictory:** A crude association justifies coercion or inconvenient missing outcomes are discarded. **Inconclusive:** Only “correlation is not causation” is repeated, with no candidate cause or improved comparison.

**Final review:** Which different causal worlds remain compatible with the observations, and what would distinguish an effective intervention from a merely favorable association?
