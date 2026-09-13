# 09.16 — Corrective guidance

## Main practice

M1 predicts 0, 11, 14, 17, and 23 minutes for 0, 2, 3, 4, and 6 cards respectively. Positive counts include setup exactly once. Fitting F1 and F2 is not independent validation, and the zero rule is part of the conceptual model rather than an arbitrary after-the-fact correction.

For six cards, the endpoint combinations are `3 + 2*6 = 15`, `3 + 4*6 = 27`, `7 + 2*6 = 19`, and `7 + 4*6 = 31`. The sensitivity range is **15–31 minutes**. Setup's specified spread contributes four minutes; per-card time's spread contributes twelve at this batch size. A nominal 23-minute estimate is below the 25-minute deadline, but the promise is not robust to all supplied assumptions. This is not a probabilistic interval or evidence of a particular chance of finishing late.

H1 has signed error `15 - 14 = +1` minute. H2 has signed error `31 - 23 = +8` minutes. H2 exceeds the greater-than-five-minute trigger and changes handling category. Retain the observation and suspend ordinary-model use for that category. H1 is one encouraging ordinary comparison, not proof of every ordinary case or of an ordinary six-card deadline.

A sensible M2 proposal separates extra handling from ordinary sorting, with new data to estimate and test that term. H2 alone does not show whether its eight-minute discrepancy is wholly a per-card check, a fixed delay, an interruption, or some combination. Do not divide by six and declare a universal handling time without stating and checking that additional assumption.

Repair a weak answer by writing the intended use, units, original version, prediction, discrepancy, and resulting restriction in one traceable record. More decimal places cannot replace missing evidence.

## Check A — Correct code, wrong representation?

The program omitted the stated setup term. For twelve cards, the conceptual model gives `4 + 12/3 = 8` minutes; the faulty program gives four. This mismatch is a verification defect relative to the stated model.

After repair, agreement with hand calculations supports that implementation for the checked inputs. It does not independently validate the assumed setup or rate. Relevant observations of the proposed operator and conditions are needed, with predictions frozen beforehand and interruptions retained rather than silently excluded.

Zero returns zero because no preparation is performed. Negative counts are outside the domain and should produce an explicit invalid-input result. Treating a malformed count as a valid empty batch hides an input problem and can produce a misleading completion estimate.

## Check B — Two equally good fits, different extrapolations

At four cards both give 17 minutes. At six both give 23. At ten M1 gives 35 and M2 gives 39. Agreement on small batches cannot identify which extrapolation is appropriate.

M2 assumes additional per-card effort beyond six cards. That might represent a real capacity or handling change, but the packet supplies no evidence for it. A withheld ordinary ten-card batch under the defined conditions would discriminate between the numerical predictions; repeated relevant cases and uncertainty analysis would still matter. An alternative process investigation could test whether such a threshold actually exists.

A deadline preference is not evidence for the smaller model. State “both fit the current small-batch data; their large-batch predictions differ; appropriate large-batch evidence is missing.” That is more informative than inventing certainty or claiming all models are equally useful for all purposes.
