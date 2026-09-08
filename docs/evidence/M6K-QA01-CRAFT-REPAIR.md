# M6K prerequisite evidence and QA-01 craft repair

Baseline: merged PR #69, `6173b1e15596ac883fd08f9c4c1f4967f3450c6a`.
The paired Portfolio Control PR #371 is merged as
`cf8716865ca91603676ee0281a751ba9fecd91dc`.

## Delivered content

Only competency **21.03, Foundational craft competence**, changes. Its default
already contained three fictional event briefs; this continuation makes the check
procedure usable with a supplied attempt record, specific access inspections, and
a plausible wrong-date notice with a separate explanatory key. Three complete
outputs, a missing-contact case and the wrong-date case are exercised by the retained
desk run. All five factual fields have deliberate negative tests. A conflicting
second contact is rejected too.

The complete [learner exercise](../authoring/quality/21.03/learner-exercise.md)
includes the inputs, preparation, tasks, record and optional craft route. Its checks
are separate linked files. The precise authoring snapshot, prior draft record and
fresh targeted reviewer disposition are retained in the same directory.

## Supported prerequisite completion

The original GitHub artifact was downloaded, its ZIP digest verified, and its four
instructional screenshots visually inspected. All 28 hosted browser tests passed,
including 1280/390-pixel instructional prompts, keyboard reveals and 200-percent
text checks. The screenshots show 10.01 on unchanged renderer, stylesheet and source
inputs. They do not claim that the new 21.03 additions were browser-tested.
See `m6k-qa01/browser-review.md` for the observed navigation wrapping limitation.

M6K-01-01's schema, compiler round trip, active/paused import protection, text/Markdown/
HTML exports and browser criterion now have executed software evidence. M6K-01-02's
validator and negative cases and M6K-01-03's runner simulation already had matching
retained executed evidence; their records now bind that evidence and the resolved
prerequisite proofs. These are software/action dispositions, not competency A/B/C
receipts or an overall release acceptance.

QA-01 receives a targeted source-repair disposition after the actual desk review and
tests. The known 10.01, 12.05, 12.08 and 10.02 repairs and all later per-competency
passes remain separate work. The next queue action is M6K-02-02, the 10.01 delayed test.

## Validation and boundaries

Commands and full results are retained under `m6k-qa01/`:

- `.venv/bin/python -m pytest tests/test_m6k_2103.py tests/test_m6k_repair_drafts.py tests/test_instructional_content.py tests/test_m6k_review_evidence.py tests/test_m6k_continuation.py -q`
- `.venv/bin/python -m pytest tests/test_m6k_2103.py -q`
- `.venv/bin/python docs/authoring/quality/21.03/verify_repair.py`
- `.venv/bin/python docs/plans/m6k/reviews.py check --base 6173b1e15596ac883fd08f9c4c1f4967f3450c6a --output docs/authoring/quality/current-report.json`
- `./scripts/agent-verify.sh contract` and `git diff --check`.

The renderer, production code, all 383 runtime packages, all 1,151 action identities,
scoring, assessment, activation and curriculum are unchanged. Source neighbors and
21.03's scored source action definitions remain exact. Runtime stays **91 tailored /
292 pending**; all seven formal competency review dimensions stay pending.

The previous broad hosted quality and Compose jobs were cancelled and the aggregate
gate failed. Those gates remain open. Local browser installation timed out; the
browser evidence above is actual hosted evidence, not a claimed local run. Docker
is unavailable locally. No gate is waived, no deployment is performed, and no
participant, specialist, owner or mastery acceptance is inferred. Plain-text desk
checks do not establish U2 for real readers or arbitrary output formats.

Rollback: revert this isolated source/evidence change. The retained recovery baseline
and older review evidence are preserved; this batch makes no runtime import or database
migration. Restore the prior source revision if a later compiler selection needs rollback.
