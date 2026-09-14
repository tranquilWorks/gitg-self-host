# 09.16 — Fresh checks

Save your attempts before opening the answer file. A calculator is allowed.

## Check A — Correct code, wrong representation?

A fictional packing process uses four minutes of setup whenever a positive batch is started, then packs three cards per minute. Its stated conceptual model is `T(n) = 4 + n/3` for positive whole-number `n`, and zero when `n = 0`. A program instead computes only `n/3` and produces four minutes for twelve cards.

Identify the implementation discrepancy and compute the conceptual model's twelve-card result. A repaired program matches that formula exactly; does this prove the assumed rate and setup accurately predict a new operator or an interrupted batch? State the separate evidence needed. Explain why a zero batch is not a four-minute job under the stated boundary rule, and why negative counts should not be quietly clipped to zero.

## Check B — Two equally good fits, different extrapolations

Two models both match F1 and F2 and make the same prediction at three ordinary cards. For positive whole-number batches they are:

`M1(n) = 5 + 3*n`

`M2(n) = 5 + 3*n + max(0, n-6)`

For zero cards both return zero. No large-batch observation is supplied. Calculate each prediction at 4, 6, and 10 cards. Can fit to F1/F2 determine which model is more credible at 10? Identify the new process assumption in M2 and a useful comparison case that could distinguish the models. Would choosing the smaller prediction because it fits a desired deadline validate that model?
