# Method and limits

Baseline: `8377d21e348eda14dd5e66153637293aeaca1a5b`, after PR #103. Audit date: 27 September 2026 UTC. The governing standards are the exact A1–A6, B1–B6 and C1–C6 in [program.json](../../plans/m6k/program.json), [the original audit](../../plans/m6k/AUDIT.md) and [review requirements](../../plans/m6k/REVIEW_RECORD.md). [CRITERIA.md](CRITERIA.md) maps the audit to those requirements without awarding formal passes.

## Coverage and reading depth

Every one of the 383 canonical IDs has a full primary-text editorial review, a distinct design description, criterion-linked findings and a follow-up. No targeted-only or instruction-only entries remain. The primary is the additional learner guide for 275 IDs and the entire implemented exercise record for 108 IDs. The latter includes outer setup/actions/adaptations and any rich instructional sections and checks; it is not limited to the rendered instructional text.

For all 275 companions, every file in the competency folder other than the author-facing SCOPE-MAP was read, including check prompts, answers, later/outcome packets and nested supplied materials. Scope maps were inspected selectively, not accepted facet by facet for all entries. Parent sources/review files and fixtures were consulted where relevant; not every parent fixture, citation, author rationale, runtime projection or retained reader received full semantic review. Recursive hashes preserve identity without pretending those files were all independently reviewed. A companion's older exercise is a fingerprinted related input, not a substitute for the new guide.

The reviewer compared each canonical scope and progress statement with the actual teaching/task, checked the supplied reasoning and relevant arithmetic, traced material dependencies and reveal order, and recorded distinctive mechanisms and gaps. All [383 notes](editorial-notes.json) were written from those readings; generation assembles them and does not itself perform semantic review. Particular calculations and literal defects have executable reproductions; the report does not claim a formal cold-start execution of every task or an exhaustive independent recomputation of every possible numerical statement.

The 91 older implemented records without rich `instructional_content` are not automatically failed because of that schema absence. Likewise, a repeated recall question is not intrinsically defective, a safe default is not necessarily trivial, and all canonical alternatives are not simultaneous obligations. Findings concern the particular unsupported claim, missing route/material, assessment use or presentation problem described in the note.

## Finding interpretation

There are 310 entries with a follow-up and 73 with no new blocker observed. Neither disposition grants acceptance. Categories are transparent summaries of the editorial note: `learner_copy` means B4-only; `presentation_or_progression` means only B4/A5 or explicitly unperformed C1/C5 issues; `substantive_editorial_followup` contains other criterion combinations; `no_new_blocker_observed` preserves that narrower finding. These categories are not severity scores, and some substantive follow-ups are limited progression questions rather than factual errors. Read the narrative and repair order before prioritizing.

A current formal ledger with zero receipts means retained formal acceptance is absent; it does not prove no informal review ever happened. Good case specificity, detailed author review, merged commits and structural tests do not close that gap. The audit does not alter the formal ledger or claim completed A/B/C gates.

## Text reuse and semantic comparison

[compare_text.py](compare_text.py) compares all 73,153 primary-text pairs. It removes Markdown heading lines, lowercases and tokenizes alphanumeric text, then compares sets of five-token sequences with Jaccard overlap. A second measure removes sequences occurring in more than twelve records. Names, numbers and YAML fields remain. Twelve is a screening choice, not an acceptance threshold.

Output retains the top 100 overall pairs, top 50 cross-domain pairs and three nearest records per ID. Zero exact normalized duplicate primary bodies were found. Low overlap can miss paraphrased templates; high overlap can reflect useful shared boundaries. [DISTINCTNESS.md](DISTINCTNESS.md) compares actual operations in neighboring lessons, and every individual note identifies a particular design. This supplies semantic evidence, not proof of independent authorship or external plagiarism clearance.

[context-excerpts.json](context-excerpts.json) retains mechanically selected quotations, truncated with `[…]` where needed. They were inspected as source evidence but are not the reviewer narratives. The domain pages render links within quotations as plain labels to avoid incorrect relative resolution. Publication hashes and last-file commits identify the retained version; a shared YAML commit is not per-entry authorship evidence.

## Checks and source support

The verifier checks IDs, file/record hashes, excerpts, metadata anchors, note/category counts, domain pages, CSV consistency and the unchanged empty ledger. It parses 10.03's actual pair list and reproduces the four-versus-seven contradiction; establishes 10.09's prior answer exposure; records 10.11's inconsistent lens partition; recomputes 10.01's delayed statistics and 24.11's fresh balance; and checks the original 21.03 materials against keys.

The broad metadata scan initially found 194 candidates. Direct inspection narrowed the catalogue-wide finding to 171 companion guides containing explicit schema/review/compatibility language. Benign phrases about an owner accepting work were excluded. Exact lines are retained. Additional implemented-copy findings are manual; this literal scan is not claimed exhaustive for all editorial jargon.

[Twenty-five external source checks](SOURCE-CHECKS.md) retain exact URLs, date and claim-specific scope. Sources include official standards, government/health pages, license text, an identified product-care page and museum catalogue text. Retrieval limitations are recorded. No image/audio inspection, individual professional advice, exhaustive medical/legal/financial revalidation or credentialed acceptance is inferred.

The existing source suite passed 1,234 tests in 21.807 seconds while substantive defects remained. This is structural evidence and demonstrates the suite's semantic limits. No application, browser, Compose, CI/CD, deployment, actual participant session, clinical assessment or legal opinion was performed in this audit.

## Independence and revision integrity

This audit continues the authoring conversation. It cannot satisfy C1's separate run receiving only learner-visible content, allowed materials and prerequisites. Reading a key and imagining not having seen it is not a cold start. The supporting packets' fictional responses were treated as learning materials, never actual participant or observer evidence. No specialist, owner approval or live event was invented.

All 383 formal C runs and applicable actual learner/qualified/owner acceptance remain unestablished. Full primary reading is complete; those are different outstanding dimensions. Content changes invalidate affected notes and reviews. Source fingerprints and defect assertions deliberately fail when the audited version changes.

## Reproduce

From the repository root, using its existing environment:

```sh
.venv/bin/python docs/authoring/catalog-quality-audit-20260927/verify.py
.venv/bin/python docs/authoring/catalog-quality-audit-20260927/compare_text.py
.venv/bin/python docs/authoring/catalog-quality-audit-20260927/build.py
.venv/bin/python docs/authoring/catalog-quality-audit-20260927/verify.py
.venv/bin/python -m unittest discover -s tests -p '*sources.py'
.venv/bin/python scripts/verify-manifest.py
```

Verify the saved audit before regeneration. Do not overwrite hashes to carry old notes onto changed lessons. Reinspect changed material and update notes, excerpts, findings and review state first. The builder rejects missing notes or a changed acceptance-ledger assumption. A successful verifier run proves documentary consistency and the named reproductions, not professional quality.
