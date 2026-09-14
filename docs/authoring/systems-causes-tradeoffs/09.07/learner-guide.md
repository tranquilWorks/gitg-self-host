# 09.07 — Systems and causal reasoning

## What you are practicing

Explain how a process produces a pattern over time, including work that crosses your first boundary. Then predict what a small change will do, test that prediction in a complete fictional system, and revise the explanation when an apparently good metric hides a cost.

**Canonical scope:** Map components, interfaces, feedback loops, delays, incentives, unintended effects, and second-order consequences.

**Deliverable:** A labeled system map, a three-day comparison of three policies, and a decision that includes the delayed and displaced work. Allow about 40 minutes, split into shorter sessions as needed. Paper, a calculator, a text editor, or spoken records are enough. No software installation or actual organization is required.

This source is educational and unscored. A successful simulation is not evidence that an actual service improved or that its workers behave like the model. The course background in SOURCES.md supports studying feedback and delayed consequences; the desk, rules, and numbers below are original fictional constructions.

## A reference for drawing a useful map

A **component** performs a role: receiving requests, processing them, or checking the result. An **interface** transfers something between roles. Label what moves, when it moves, and who may accept or reject it. An arrow labeled only “affects” conceals the mechanism.

A **stock** is an accumulation at an instant, such as unfinished requests. A **flow** changes that accumulation over an interval, such as requests received per day. Ten unfinished requests and ten requests per day are different quantities. Adding them requires choosing an interval and converting the flow to an amount.

A **feedback loop** returns a consequence to something that influenced it. A reinforcing loop amplifies a change; a balancing loop counteracts it. Those words describe direction, not whether the consequences are good or bad. A chain that never returns is not a feedback loop. A balancing process may be unable to keep up when its capacity is limited.

A **delay** separates a cause or decision from a later effect. Work can be absent from today's queue but already committed to tomorrow's. An **incentive** rewards a behavior or metric; it is not automatically proof of anyone's motives. Write a possible response as a hypothesis unless it is given by the exercise or supported by a real record.

A **boundary** says what the analysis includes. A shorter visible queue can coexist with more unfinished work outside it. Inspect the purpose, not just the easiest number to improve. Include the people who bear added work, the needs you must preserve, and any consequences your model omits.

## A different worked example: dishes waiting to be put away

Four clean plates wait on a counter. Three more arrive during an hour and two are put away. The ending accumulation is 4 + 3 - 2 = 5 plates. Putting three plates in an uncounted cupboard makes the counter look better without establishing that the agreed storage task is complete.

A possible balancing response is that seeing more waiting plates prompts more put-away effort. That causal arrow is a hypothesis about behavior, not something proved by the arithmetic. If cupboard space is full, extra effort may not increase the outflow. This separates an accounting identity, a behavioral assumption, and a capacity limit.

## Complete practice packet: the request desk

Every request below is an interchangeable unit of harmless administrative work. There are no emergencies, private records, or actual participants. We stipulate the rules so you can check the logic; do not treat their rates as measured facts about real workers.

The desk's purpose is to settle legitimate requests without losing them or creating unacknowledged work. The daily dashboard displays the ready queue and today's processing count. It omits requests due to reopen tomorrow and requests refused at intake. A fictional manager rewards a high processing count and a low ready queue. Whether a real person would game such a metric is unknown.

At the start of Day 1, **2 requests are ready**, **0 reopenings are due**, and **0 requests have been hidden**. **4 new legitimate requests arrive each day.** Processing capacity is normally **4 attempts per day**. Reprocessing consumes capacity too. All three policies begin from this same state; never feed one policy's ending queue into another policy's start.

Within each day, do these operations in this order:

1. Add the ready queue, admitted new requests, and reopenings due from the preceding day. Call the result **D**, available work today.
2. Process **C = the smaller of capacity and D**. Never process nonexistent requests or create a negative queue.
3. The next ready queue is **B_next = D - C**.
4. Calculate **R_next**, requests that will reopen at the start of the next day. They are not available for another processing attempt today.
5. Add any refused new requests to a separate hidden stock **H**. Nothing in this packet resolves that stock.

At each day's end, count all unfinished work as **B_next + R_next + H**. Also retain the processing count and capacity; a single total cannot explain every mechanism. A processing attempt is not necessarily a permanently settled original request.

### The three policies

| Policy | New requests admitted each day | Capacity | Tomorrow's reopenings | Hidden work |
| --- | --- | --- | --- | --- |
| Baseline | 4 | 4 every day | 1 when D is greater than 4 and C is positive; otherwise 0 | None |
| Clarify before processing | 4 | 3 on Day 1; 4 afterward | 0, stipulated for this toy policy | None |
| Hide one at intake | 3 | 4 every day | Same rule as baseline | Add 1 legitimate request each day |

The clarification policy spends one processing slot on initial setup, then changes the stipulated rework mechanism. Its zero-reopening rule is an assumption to test elsewhere, not a guaranteed real improvement. The hiding policy is included for diagnosis, not as an acceptable intervention. Rejected legitimate work does not cease to matter because the dashboard omits it.

### Action 1 — Draw the structure and expose its assumptions

Use boxes or a spoken sequence for intake, ready work, processing, quality feedback, and requests outside intake. Label the request count crossing each interface, its daily timing, and the processing authority. Keep an explicit place for tomorrow's reopenings.

Distinguish three kinds of statement: **given fictional rule**, **arithmetic identity**, and **hypothesis requiring real evidence**. Map the overload mechanism: more available work above the threshold can create reopening, reopening adds to next day's load, and that load can keep the threshold exceeded. This is a reinforcing route with a one-day delay. It is a threshold mechanism, not a continuously proportional effect.

Also map the balancing route: available work can increase processing attempts, which remove ready work, but attempts cannot exceed capacity. Describe what happens once that limit is reached. Add the incentive concern as a hypothesis: a dashboard rewarding visible reduction may encourage refusal rather than settlement. Include the affected requester even when the request is outside intake.

Use this map record:

`From | To | what is transferred or influenced | direction | delay | given rule, identity, or hypothesis | evidence needed outside the simulation`

Do not present all arrows as independently established causal relationships. Name at least one omitted influence, such as unequal request complexity or the burden of clarification on requesters.

### Action 2 — Predict first, then run each policy for three days

Before calculating, record which policy you expect to leave the least unfinished work after Day 3, which might look worse initially, and which dashboard number could mislead. Explain your predictions using an arrow or delay rather than a guess about worker character.

Make three copies of this row and use one table per policy:

`Day | B at start | reopenings due | admitted new | D | capacity | C | B_next | R_next | H | all unfinished`

Calculate Days 1–3 in order. Carry B_next and R_next forward separately. Keep Day 3's R_next in the ending total even though it would enter the ready queue on Day 4. This avoids ending the study just before a cost becomes visible.

Check conservation after each day. Initial requests plus all new legitimate arrivals must equal permanently settled requests plus all unfinished requests. In this simplified model, today's net permanently settled count is **C - R_next**; add those daily counts across the run. Hidden work remains on the unfinished side of the identity. No request is counted as both permanently settled and pending.

Only after saving your tables, inspect the main-practice key in **check-answers.md**. The rules make the results derivable; the separate key is corrective guidance, not a secure examination barrier.

### Action 3 — Explain the difference and revise the decision

Compare the ready queue, all unfinished work, processing attempts, and setup cost. Describe why a policy can look worse on the first day yet avoid a later accumulation. Check whether the apparent improvement reduces the total or merely moves it outside the dashboard.

Write a decision with four parts: the modeled mechanism, the preferred provisional policy, the most important assumption to test, and a stop or revision condition. Do not claim that a stable queue has been eliminated. If incoming work equals long-run capacity and no extra capacity is available, an existing queue can remain even after rework is removed.

A real follow-up would need authority, requesters' access needs, actual reopen counts and delays, and a measure of burden outside the desk. Protect urgent and essential routes rather than refusing them for an experiment. A reasonable stop condition is any lost legitimate request or an unacceptable new access barrier. Do not test by secretly manipulating another person's work.

## Fresh checks, adaptation, and progression

Complete both cases in **check-prompts.md**, save your responses, then open their keys. One checks accumulation and delayed rework; the other checks ordering with a delivery delay. You need to trace a mechanism, not merely reuse the desk's winning policy.

For **Accessibility**, use one card per stock and move counters while another person records at your direction. Name delayed and hidden cards aloud. Use larger print, dictation, or a calculator. Assistance may change the representation, but the learner still chooses the boundaries and explains the accounting.

For a more demanding route, test zero arrivals, a capacity above available work, or a longer reopening delay. State every new rule before running it. Compare the result with your prediction, and mark any changed conclusion as model-dependent. Increasing realism does not automatically make an unvalidated model accurate.

For later transfer, map one ordinary process you are authorized to observe, such as your own reading backlog. Record both completed work and abandoned work. An actual observation can challenge a proposed loop, but a few days do not prove a universal mechanism.

## How to interpret your result

**Supportive:** The map labels mechanisms and delays; the tables conserve requests; the decision includes hidden and delayed work and states the assumptions behind the improvement.

**Mixed:** The arithmetic is right but the conclusion calls a stable queue “cleared,” or neglects the effort needed to clarify requests.

**Contradictory:** Refusing legitimate requests is counted as settlement, a processing count is treated as unique completed work, or speculation about motives is presented as measured fact.

**Inconclusive:** Boxes are drawn without a returning loop, time sequence, prediction, or comparison. Simulation results alone cannot establish a real service improvement.

**Final review:** Did the change reduce the problem, postpone it, move it, or reveal that the boundary was too narrow?
