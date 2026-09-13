# M6K — Evidence, humility, and forecasting source cohort

This next grouping individually authors **09.04 Source and evidence evaluation**, **09.05 Epistemic humility**, and **09.06 Probabilistic and scenario thinking**.

## Status

Authoring baseline: `tranquilWorks/gitg-self-host/main` at `d93532696d3ea9d04e50f47350b90fa255208511`, after PR #77. Its runtime coverage remains **108 tailored / 275 pending / 383 total** with **1,151 actions**.

This cohort is a source-only candidate, not compiler-selected runtime content. Prior PR #78 separately contains 09.01–09.03 source candidates and is still draft. This group does not silently integrate, merge, or count that earlier work. There are now two authored source groupings awaiting runtime integration; neither advances the 108 runtime count. Formal review and actual learner evidence are separate.

## Use the material

Each competency directory contains a complete learner guide, two fresh checks, and a separate corrective key. 09.05 also has a later evidence packet; 09.06 has separately stored forecast outcomes. Preserve initial records before opening those files. This is an instructional reveal convention, not cryptographic sealing or assessment security.

09.04 supplies complete response counts, missingness bounds, source-dependence tracing, and a contrast with independently collected stronger evidence. 09.05 supplies a versioned belief record, context-sensitive update, and a case where resisting unsupported pressure is appropriate. 09.06 supplies historical records, prospective forecast forms, decision thresholds, a fixed resolution policy, actual calibration-group arithmetic, and a rare-event example showing why a low Brier score is not calibration by itself.

`SCOPE-MAP.md` traces every canonical element individually. `SOURCES.md` bounds the external background support. `fixtures.json` contains test data, including answers: it is for source verification, not a learner-facing pre-attempt page.

Run standalone source checks from a checkout or the supplied bundle root:

```sh
python -m unittest discover -s tests -p 'test_m6k_evidence_humility_forecasting_sources.py' -v
```

When the previous cohort is also present, run both with:

```sh
python -m unittest discover -s tests -p '*sources.py' -v
```

The tests use Python's standard library. They check instructional structure, exact counts and arithmetic, probability validation, missing-outcome handling, prompt/fixture alignment, and preservation of source-only count declarations. They are not production scoring, compiler, Django, historical replay, or actual learner tests.

## Integration still required

The current workspace cannot resolve GitHub or package-index hosts and has no full checkout or Django installation. Authenticated connector reads/writes work, so the source can be published and local standalone verification performed. That does not establish application readiness.

Keep this publication draft. `MANIFEST.tsv` still requires regeneration in a complete checkout using the repository's verified process, followed by the contract, Ruff, and applicable source/repository checks. No gate is waived. Do not merge a manifest-incomplete checkpoint merely because its standalone tests pass.

Then scope runtime promotion explicitly. Preserve the original 09.04–09.06 packages and hashes. Project this material through the existing `docs/authoring/exercises/09.yaml` schema and authoring compiler. Retain separately revealed checks/evidence/outcomes as the runtime schema allows; do not expose future outcomes in setup or flatten keys into pre-attempt instructions. Do not invent a new runtime importer in this source-only branch.

Regenerate canonical packages, source/risk records, recovery/current-review projections, reports, and the manifest. Verify the unchanged protocol/action IDs, parent mappings, completion, activation, scoring, historical replay, and active/paused practice content. Run the actual Django guide/reveal path, required readiness gates, browser journeys, and Compose backup/restore checks. Preserve formal instructional, cold-start, learner, qualified-where-needed, and owner review statuses rather than claiming them from source tests.

Known repository entry points were inspected in Makefile: `make pilot-check curriculum-check competency-evidence-check`, `make lint`, `make e2e`, and `make compose-smoke`. These have **not** been run for this cohort in the source-only workspace. The authoritative compiler/manifest commands should be inspected rather than guessed when resuming.

Complete runtime integration of the earlier and current groups before treating them as six additional runtime-authored competencies. No automatic merge, deployment, data import, or participant-data access is authorized by this checkpoint.
