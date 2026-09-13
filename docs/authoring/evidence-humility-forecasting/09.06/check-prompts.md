# 09.06 — Fresh checks

Save your calculations and explanations before opening the answer file. These are complete synthetic cases, not live forecasts.

## Check A — A low-probability success and two excluded records

Use the guide's definition of on-time and its predeclared cancellation/missing-record rules. Four forecasts were preserved before these records appeared:

| ID | Original probability | Later record |
| --- | --- | --- |
| G1 | 0.75 | First agenda item begins 3 minutes after the advertised start. |
| G2 | 0.25 | First agenda item begins 5 minutes after the advertised start. |
| G3 | 0.80 | Opening record is missing; the organizer cannot confirm a time. |
| G4 | 0.80 | The meeting was cancelled. |

Classify every record as scored, unresolved, or void. For the scored records, assign binary outcomes, compute each squared error, and compute the mean with the correct denominator. Retain reasons for exclusions. Does G2 occurring prove the original 0.25 probability was impossible? Would replacing G2's probability with 0.9 after viewing the result improve the original forecast?

For a separate toy action costing 4 minutes and avoiding 10 minutes only if an event occurs, compute its break-even probability and net expected saving at probabilities 0.2 and 0.7. Explain why the sign of an expected value is not a guarantee about the realized result.

## Check B — Actually inspect calibration

An audit packet contains twenty synthetic forecasts issued in two predeclared exact-probability groups. Every outcome is resolved. Within the first group, all probabilities were 0.2 and outcomes were:

`1, 0, 0, 0, 0, 1, 0, 0, 0, 0`.

Within the second group, all probabilities were 0.8 and outcomes were:

`1, 1, 1, 1, 0, 1, 1, 1, 1, 0`.

For each group, report the number of forecasts, mean predicted probability, observed event frequency, and mean squared probability error. Compute the whole-set mean squared error. Explain what the group comparison shows descriptively and why it does not prove perfect population calibration or independence.

Now compare a second complete synthetic set: one hundred forecasts all assign probability 0.01, and none of the events occur. Calculate its mean squared error. Does a lower Brier score on this different set prove a better forecaster or perfect calibration? Identify why event frequency, comparability, uncertainty, and a suitable reference forecast matter. Do not infer a true event probability merely from these finite outcomes.
