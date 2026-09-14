# 09.08 — Supplied model results

Open after recording predictions and running the four conditions. These are deterministic fictional outputs, not collected participant observations.

| Condition | Attempted | Violations | Correctly completed | Held |
| --- | --- | --- | --- | --- |
| V1/full | 8 | 4 | 4 | 0 |
| V2/full | 8 | 0 | 8 | 0 |
| V1/masked | 8 | 8 | 0 | 0 |
| V2/masked | 8 | 0 | 0 | 8 |

For V1/full, 12, 21, 34, and 43 are misrouted; 11, 22, 33, and 44 happen to be routed correctly. V1's first-digit rule is therefore defective even when followed without an attention lapse.

For masked inputs, Spec S2 requires H. A V1 guess that happens to match the hidden original destination is not compliant completion from the available information. V2/masked prevents that violation but cannot complete the records. The model supports both a wrong-rule contributor and an upstream information-loss contributor.

The fresh V2/full deck routes **R, L, R, L, R, L, R, L**, giving 8 compliant completions, no violations, and no holds. The separate four malformed or incomplete codes all produce H. Keep those two tests and their denominators separate.

Among all 100 full two-digit ASCII codes, V1 disagrees with the correct routing on 50 and V2 disagrees on none. This exhausts only the stated finite domain. It does not test reading errors, behavior, or a physical feed.
