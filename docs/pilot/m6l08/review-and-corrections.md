# Execution, review and correction records

Current status: no assigned study operator, participant dataset, reviewer receipt
or pilot-launch decision was supplied for M6L-08. All fields below are unfilled
preparation, not approvals. Store completed records privately outside Git.

## Launch record

| Record | Required content |
| --- | --- |
| Study responsibility | Named owner/contact, observers, data custodian, access recipients and conflicts |
| Qualified review | Named UX researcher, accessibility reviewer, measurement/statistical reviewer and privacy/safety reviewer; relevant competence, scope, date and receipt |
| Existing governance | Disposition of the applicable `ER-M6A-003`/`RG-M6A-002` and practice-specific specialist requirements; do not overwrite them from this checklist |
| Candidate | Exact commit, image digest, deployment environment, aggregate CI URL/result and reviewed desktop/mobile artifacts |
| Operational rehearsal | Synthetic-only login, private export, backup/restore, account isolation, stop and withdrawal drill results |
| Protocol | Version, tasks/practices, proposed cohort, recruitment/access coverage, compensation if any, neutral contact script and who may send it |
| Participant disclosure | Completed information sheet, consent method, separate calibration choice and no recording/telemetry boundary |
| Lifecycle | Storage/access, actual retention and backup-expiry dates, withdrawal contact, external-copy handling |
| Decision | Named responsible approver, date, precise approved scope and unresolved conditions; pending is not approved |

No recruitment or participant outreach is sent by this implementation. Once the
responsible people and required decisions exist, the operator recruits the agreed
cohort, records consent, runs cycle 0, then three weekly cycles. The software
cannot substitute for those elapsed weeks or observations.

## Study closeout record

Record candidate/protocol versions, study dates privately, invitation/enrollment/
contact/observation totals, recruitment coverage and absent groups, exclusions,
withdrawals, unknowns and attrition. Attach private input/output digests and
analysis command/revision. Distinguish what was directly observed, what was
participant-reported and what is the reviewer's inference. Include failures,
contradictory cases, access barriers and inconclusive outcomes alongside success.

Review the tool's suppressed/unknown categories without trying to reverse them.
A qualified reviewer may inspect the approved private underlying records under
the consent agreement; a developer does not need them to fix a generic interface
bug. Write minimal reproducible defects with synthetic examples. Public repo
issues must exclude participant references, quotes, private screenshots and raw
records. No aggregate is automatically approved for public release.

## Versioned correction register

Use this header in a private CSV or equivalent reviewed record:

```csv
finding_id,source_receipt,product_revision,protocol_version,journey,severity,observation_or_inference,result,proposed_fix,owner_role,review_receipt,followup_batch,acceptance,retest_receipt,disposition
```

Use stable finding IDs, for example `M6L08-F001`, assigned only to an actual
finding. Do not pre-populate evidence rows. Dispositions include `open`,
`needs_more_evidence`, `accepted_for_followup`, `fixed_pending_retest`,
`verified_with_limits` and `not_supported`. No majority vote erases an access or
safety failure. Privacy exposure, broken consent, unsafe instructions or loss of
private state stops affected sessions until reviewed; an ordinary wording issue
can enter a bounded follow-up batch.

Each accepted fix names its observable acceptance and original version. Preserve
old findings/results, implement a new reviewed version, test with synthetic data,
and repeat the affected real-user task where feasible. Never rewrite historical
scores or assessment responses to make study outcomes look better. Qualified
assessment changes require a separate contract, prospective versioning and exact
historical replay.

## What is still needed from people

1. Assign the operator/data custodian and qualified reviewers; fill the launch
   record and agree feasible dates/retention/access arrangements.
2. Obtain the applicable study/content release decisions, recruit and consent
   actual participants, and run the agreed cycles.
3. Supply authorized private evidence paths and consent/provenance receipts for
   analysis; never paste raw participant records into public issues or Git.
4. Retain signed reviewer conclusions and approve evidence-backed follow-up work.

These requirements are external evidence dependencies. Preparation and automated
checks can pass while these remain incomplete. Batch 08 stays open until its
actual observation, assessment-evidence and qualified-review acceptance is met.
