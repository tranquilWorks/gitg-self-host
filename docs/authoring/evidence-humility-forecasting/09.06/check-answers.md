# 09.06 — Answer guidance and repairs

Open after saving forecasts, resolutions, and check responses. Calculations evaluate the stated synthetic packets only. They create no production scoring, real meeting evidence, or calibration certification.

## Main practice

Eight of ten historical delays are at most five minutes, so the observed base rate is 8/10 = 0.8. H5 is included at exactly five minutes. The observed historical delay range is 0–12 minutes; it is not a promised future interval. The reference set is small and may not represent changed conditions.

F1, F2, F3 resolve to 1, 0, 1. With three prospectively chosen probabilities of 0.8, errors are 0.04, 0.64, and 0.04, and their mean is 0.72/3 = 0.24. Use your actual preserved probabilities if they differed; do not replace them with these example probabilities. There are three scored cases and no excluded cases in the main packet.

Two successes in three trials is about 66.67%, not proof that the true probability is exactly two thirds or that an 80% forecast was inherently wrong. The realized count is not a calibration study. Do not claim that widening a range after seeing the outcomes repairs the earlier forecasts.

For the early-arrival toy model, net expected saving is `15p - 5`. At 0.3 it is -0.5 minutes; at 0.8 it is 7 minutes; at 0.9 it is 8.5 minutes. Break-even is p = 1/3. Across p = 0.6–0.9, net expected saving ranges from 4 to 8.5 minutes, all positive under the stated assumptions. These scenarios are sensitivity inputs, not equally weighted possibilities.

The realized net is 10 minutes saved when the event occurs or 5 minutes spent without that benefit when it does not. It is not always the expected saving. Other costs, obligations, and access requirements can change the action. Sensitivity should also inspect the cost and avoided-disruption assumptions, not only probability.

**Repair:** Count the threshold case correctly. Preserve the actual point probabilities. Do not score a probability range by selecting its best point afterward. Label the observed outcome range, probability range, and missing-data treatment separately.

## Check A

G1 and G2 are both scored with outcome 1, including G2 at exactly five minutes. G3 is unresolved, not a failure; G4 is void under the predeclared rule. Preserve both exclusions and reasons.

G1's error is (0.75 - 1)^2 = 0.0625. G2's error is (0.25 - 1)^2 = 0.5625. The mean across the two scored cases is 0.625/2 = 0.3125. Dividing by four would silently count missing/cancelled cases as zero error and is incorrect. A probability of 0.25 allows the event to occur. One such outcome does not prove that the forecast was impossible or well-calibrated.

Changing G2 to 0.9 afterward rewrites the record; it is not an improvement of the original forecast. A new model may be recorded prospectively for new events.

For the separate action, net expected saving is `10p - 4`, with break-even p = 0.4. At 0.2 the net is -2 minutes; at 0.7 it is 3 minutes. In a single case the realized net is either 6 minutes saved or 4 minutes spent without the modeled benefit. The expectation is not a guaranteed realized outcome.

## Check B

The 0.2 group has ten forecasts and two successes; its observed frequency is 0.2. Its total squared error is 2 × 0.64 + 8 × 0.04 = 1.6, for a mean of 0.16. The 0.8 group has ten forecasts and eight successes; its observed frequency is 0.8. Its total error is 8 × 0.04 + 2 × 0.64 = 1.6, again mean 0.16. The combined mean is 3.2/20 = 0.16.

Predicted and observed frequencies match in these two supplied groups. That is exact descriptive agreement in a constructed finite dataset, not proof of perfect calibration in a population, independence of events, or future performance. Do not extrapolate from these two groups to unobserved probability levels.

The hundred 0.01 forecasts with no events have mean squared error 0.0001. That lower number on a different event set does not establish a more skillful or perfectly calibrated forecaster. The observed frequency in that set is 0, not exactly 0.01, but finite observations do not by themselves determine the true event probability. Predicting 0 for every event would have zero error in this particular set; choosing that reference retrospectively does not establish a valid prospective baseline.

Compare candidate forecasters on the same relevant events and against a reference specified without outcome leakage. Inspect probability-versus-frequency groups with their counts and uncertainty. Brier score concerns overall probability accuracy and is not a substitute for that calibration review.

**Repair:** If you equated a low score with perfect calibration, add the actual group-frequency comparison and its sample boundary. If you compared unlike event sets as a ranking of people, specify a common evaluation set and prospective reference before drawing that conclusion.
