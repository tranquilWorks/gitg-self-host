# M6L-08 — Multi-cycle study kit

This kit prepares evaluation of the guided product delivered in M6L-01–07.
It contains no participant observations or reviewer acceptance. Batch 08 is
**prepared for execution, not empirically complete**. The historical
[Private Pilot 001](../PRIVATE_PILOT_001_FINDINGS.md) concerns an earlier build
and one session; it does not establish current fit, repeated use or validity.

Start with the [protocol](protocol.md), give participants the completed
[information and consent sheet](participant-information.md), and use the
[observation dictionary](observations.md). The
[assessment evidence plan](assessment-evidence-plan.md) identifies what the
existing consented export can and cannot answer. Complete the
[review and correction record](review-and-corrections.md) before launch and at
closeout. Reviewer identities, participant contacts and data stay outside Git.

## Prepare a private workspace

Use a restricted directory outside the checkout, on the approved study host.
These commands create empty preparation files; they do not recruit anyone,
record consent, start a participant session, or read the application database.

```bash
install -d -m 700 /path/to/private-study
.venv/bin/python scripts/pilot_study.py init \
  --revision "$(git rev-parse HEAD)" --kind participant \
  --output /path/to/private-study/observations.json
```

Use the actual candidate's full source revision, then record its image digest,
CI result and study approval in the private execution record. A source revision
is not a registry digest. Keep one dataset per candidate and protocol version;
a changed build starts a new cohort/file, rather than mixing outcomes silently.
`--kind synthetic` is the default for rehearsals. Never relabel test fixtures
as participant observations.

After actual consented sessions, enter only the fields defined in the dictionary:

```bash
.venv/bin/python scripts/pilot_study.py summarize \
  --input /path/to/private-study/observations.json \
  --output /path/to/private-study/summary-01.json \
  --confirm-sensitive-input
```

Outputs are new mode-0600 files; existing files and symlinks are not overwritten.
Input is limited to 2 MiB. Unknown fields, duplicate keys/references/task rows,
invalid task/cycle combinations and out-of-scope fit ratings are rejected.
Use a new output filename for each analysis. No data is uploaded and no runtime
state is opened or changed. The tool does not verify that recorded consent or
provenance is true: signed records and human review remain necessary.

The summary excludes withdrawn participants, reports absent observations
separately, suppresses an entire categorical breakdown if any nonzero cell is
below five, and keeps every assessment axis open. Exact included cohort totals
remain visible. It emits neither participant references nor individual rows.
It is still private: repeated or overlapping aggregates can reveal information.
Do not publish it or combine releases to recover suppressed values.

## Current disposition

| Action | Prepared deliverable | Remaining execution |
| --- | --- | --- |
| 08-01 | Protocol, tasks, recruitment, consent, retention and stop rules | Assign operators/reviewers and approve the exact study before recruitment |
| 08-02 | Observation capture and private summary; analysis rules | Actual consented observations across three weekly cycles, including non-return and barriers |
| 08-03 | Eight-axis collection and analysis plan; existing export/analyzer instructions | Approved additional measures, actual data and qualified assessment analysis |
| 08-04 | Reviewer brief, evidence checklist and versioned correction template | Named qualified review, signed findings and evidence-backed corrections |

Preparation completes 08-01's planning deliverable. The batch and the other
three actions remain open. Software tests, the owner's product acceptance and a
small usability cohort cannot close an assessment-evidence axis.
