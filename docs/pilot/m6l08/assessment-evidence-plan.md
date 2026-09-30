# Eight-axis assessment evidence plan

All eight axes in Decision 055 remain `data_collection_required`. This plan
organizes collection and review; it neither changes the assessment nor claims
that a small product study validates it. Freeze the hypotheses, population,
measures, exclusions, missingness handling and analysis version before examining
outcomes. Log later deviations with reasons; distinguish exploratory results.

## Available workflow

The existing M6I-04 export includes only completed, participant-created runs with
current explicit per-run consent. It excludes the seeded demo. Participants can
inspect their contribution and withdraw it from future exports. The pseudonym
links included retakes; it is not anonymous. Do not join it to the observation
study's independent reference. Ordinary product use and observation consent do
not authorize calibration export.

For an authorized operator on an approved study instance, after reviewing consent,
private storage and retention:

```bash
docker compose exec app python manage.py export_assessment_calibration_dataset \
  --output /data/private-study/calibration-01.json --confirm-sensitive-export
docker compose exec app python manage.py analyze_assessment_calibration_dataset \
  --input /data/private-study/calibration-01.json \
  --output /data/private-study/calibration-summary-01.json --confirm-sensitive-input
```

The private directory must already exist with access restricted to the operator.
Keep paths under the persistent volume; protect any external copies separately.
Both commands refuse overwrite. The analyzer validates the reviewed export and
reads no database. Do not hand-edit its hashed input or use the observation JSON
as calibration input. Record source hashes and candidate revision in the private
review packet; inspect minimized outputs before sharing with named reviewers.

The existing thresholds of 30 participants and 30 linked retest participants
permit only a candidate analysis packet, not a sufficiency or validity claim.
Small cells are suppressed; the result remains sensitive. Its completed-axis
count stays zero regardless of sample size.

## Prespecified review questions

| Exact axis | Available input / missing input | Analysis to agree before collection | Responsible expertise and evidence needed |
| --- | --- | --- | --- |
| `item_response_distribution` | Consented completed-run item responses; no representative sample guaranteed | Describe item category frequencies, floor/ceiling patterns and uncertainty within the sampled population; preserve sparse categories and excluded-run reasons | Measurement/statistical reviewer: cohort definition, consent/provenance, reproducible distributions and limitations |
| `item_missingness_and_not_applicable` | Completed-run response/clarifier information; abandoned browser-local attempts absent; product-context N/A is a different construct | Audit what the instrument permits to be missing/N/A, distinguish structural absence from nonresponse, report denominators per item; do not infer absent values or map context N/A onto assessment items | Measurement reviewer: field semantics, missingness table, selection bias and limits of completed-run sampling |
| `test_retest_reliability` | Consented linked retakes and whole-day intervals | Prespecify interval windows and expected stable conditions; justify sample size and agreement/reliability method for the data type, with uncertainty and sensitivity to interval; report practice/intervention exposure as a design limitation unless separately consented | Psychometric reviewer: stable-population rationale, linked-sample attrition, method assumptions and signed interpretation; exploratory item agreement alone is insufficient |
| `convergent_and_discriminant_validity` | External reference measures are absent | Select appropriate licensed/accessible comparator measures, hypothesize relations, agree timing and multiplicity handling before collection; obtain a new reviewed consent/data contract | Measurement/domain specialist: construct definitions, comparator rationale, actual matched data and limits; no inferred external measures |
| `differential_item_functioning_and_fairness` | Consented population-group variables are absent | Justify necessary groups, privacy safeguards and adequate per-group sample/precision; prespecify a suitable method and response to sparse groups before collecting sensitive variables | Psychometric/fairness and privacy reviewers: group necessity, sampling adequacy, actual data, uncertainty and cultural interpretation; device type is not a fairness proxy |
| `completion_burden_and_abandonment` | Completed-run timing only; observer can see offered tasks and explicit stops, not all abandoned attempts | Report observed task outcomes and missing opportunities separately; design a separately consented attempt denominator and stopping definition before estimating abandonment; retain access/break effects | UX/accessibility researcher: recruitment/attempt flow, voluntary stop/unknown distinctions and missingness; no rate inferred from completed exports |
| `recommendation_fit` | New study captures unlinked broad participant judgments; calibration export has no fit judgment or context linkage | Describe observed product fit; a linked calibration question needs its own necessity/consent/schema review, prespecified outcome and assessment/context separation | UX/measurement reviewer: actual fit observations, sample/context limits and conflicting cases; no join by timestamp, identity, or guessed token |
| `longitudinal_outcome_association` | No consented external outcome measure or linked exposure history | Choose an independent meaningful outcome and follow-up period, consented linkage, sample/attrition plan and confounding strategy; prespecify association rather than causation unless the design supports causation | Longitudinal/statistical and domain reviewers: actual repeated data, design/attrition receipts and signed limits; weekly completion credit cannot validate itself |

The new observation fields support formative product evaluation only. They do
not silently extend calibration consent or export allowlists. Missing comparator,
group, attempt-denominator, linked-fit and longitudinal data each require a
separately reviewed follow-up collection contract. Prepare that work with the
reviewer; do not invent values to fill an analysis pipeline.

## Axis closeout requirements

For each axis retain the protocol/version, consent basis, population and sample
flow, exclusions and missingness, protected input digest, exact analysis code
revision, outputs, uncertainty, contradictions, adverse findings and limitations.
A named qualified reviewer records competence, conflicts, method, result
(`supported_with_limits`, `inconclusive`, `not_supported` or `not_assessed`),
permitted claim, date and receipt. A result is not a universal validation claim.
Any proposed status/algorithm change becomes a separately authorized versioned
batch, preserving frozen assessment history and replay. Neither this tool nor
a completed checklist rewrites the existing axis registry.
