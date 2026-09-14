# 09.13 — Corrective guidance

## Main practice

D: A's mean and median are 10; B's are 8. A's minimum–maximum is 8–12 and B's is 6–10; each numerical range is 4. B minus A is −2 minutes, a 20% reduction relative to A's mean. The values overlap from 8 to 10. The data show a selected-group difference, not an individual change or a demonstrated treatment effect. A defensible headline is: “In these two five-person volunteer samples, B's observed mean duration was two minutes lower; selection and other differences remain unresolved.”

S: pairs (2,4), (2,6), (2,8), (4,6), (4,8), (6,8) give means 3, 4, 5, 5, 6, 7. Their average is 5, the full toy-population mean. A single two-card sample could still have mean 3 or 7. These six exact possibilities describe the specified sampling procedure; they are not a general uncertainty interval for D.

R: mean x = 2.5 and mean y = 5. The centered cross-product sum is 7 and the x-squared-deviation sum is 5. Thus b = 1.4 and a = 1.5. At x = 2 the fitted time is 4.3 and its residual is 5 − 4.3 = 0.7. At x = 5 the fitted value is 8.5, an extrapolation beyond 1–4. All four residuals are 0.1, 0.7, −1.7, 0.9; their squared sum is 4.2. None of this identifies an intervention effect. A constant-x dataset would leave the slope denominator zero and must not silently produce a fitted slope.

Noise model: after selecting the first reading of 12, independent second readings remain 8, 10, and 12 with mean 10. Some second readings equal 12; the model does not guarantee improvement for every selected object. The expected decline relative to the selected initial reading needs no treatment in this toy world.

B: flagged true cases = 8, missed cases = 2, falsely flagged noncases = 10, correctly unflagged noncases = 80. The base rate is 10/100 = 10%; sensitivity is 8/10 = 80%; the fraction of flags that are true is 8/18 = 4/9, about 44.4%. The false-positive rate is 10/90, about 11.1%, not 10/100. Each denominator answers a different question.

## Check A

P has mean 8, median 4, range 20. Q has mean and median 5, range 0. Q is lower by mean but higher by median. That is not a contradiction: the summaries answer different questions, and P's long wait matters to the mean. The absolute mean difference Q minus P is −3, while the median difference is +1. If the goal concerns long waits or fairness to every user, neither single center is enough.

Inspect whether 24 was a transcription or unit error using actual source records; do not presume it was. If legitimate, retain it. If a justified correction is made, record both the reason and the effect rather than silently deleting it. Convenience samples do not establish a population or causal effect.

The toy pair means are 2, 4.5, and 5.5; their mean is 4, matching (1+3+8)/3. This is a different known population with a stated random sampling mechanism, not a model of the selected wait data. Regression toward the mean can explain a later less-extreme value when selection used a noisy extreme and subsequent noise is not perfectly tied to that selection. It is a candidate explanation, not proof of the cause of a particular real change.

## Check B

mean x = 1.5, mean y = 2.5; the centered cross-product sum is 6 and the squared-x sum is 5. The slope is 1.2 and intercept 0.7. Prediction at x = 2 is 3.1. x = 6 is extrapolation beyond 0–3. The model describes an observed relationship; increasing x by intervention need not reproduce its slope because the packet does not establish the causal structure.

The 1,000-item table has 16 true positives, 4 false negatives, 98 false positives, and 882 true negatives. Base rate = 2%, sensitivity = 80%, false-positive rate = 10%, and true fraction among flags = 16/114 = 8/57, about 14.0%. The guide's first table had a different false-positive rate, 10/90; do not attribute every numerical difference between those tables solely to base rate.

The matched-rate comparison uses 8 true positives and 9 false positives in the 100-item batch: 8/17, about 47.1%, versus 16/114, about 14.0%. Both now have 80% sensitivity and 10% false-positive rate. The lower true-case base rate yields a smaller true-case fraction among flags under these specified rates. This numerical demonstration is not a guarantee that a real tool's rates remain constant when its population changes.

Repair: write numerator and denominator in words before turning them into percentages. If you reported “80% of flags are correct,” replace it with the appropriate positive-predictive fraction and retain the missed and falsely flagged cases.
