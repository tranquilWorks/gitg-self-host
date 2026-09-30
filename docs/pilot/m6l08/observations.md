# Observation dictionary and private lifecycle

Contract: `GG-M6L08-OBSERVATIONS-1.0`. The CLI creates an empty JSON file. Enter
only consented observations using the following exact fields. Do not copy the
example below into a real dataset; it is explicitly synthetic.

```json
{
  "schema_version": "GG-M6L08-OBSERVATIONS-1.0",
  "product_revision": "0000000000000000000000000000000000000000",
  "data_kind": "synthetic",
  "participants": [{
    "ref": "study-00000000000000000000000000000001",
    "consent": "consented",
    "observations": [{
      "cycle": 0,
      "task": "entry",
      "outcome": "completed",
      "assistance": "none",
      "time_band": "under_2",
      "fit": "not_asked",
      "barrier": "none_reported"
    }]
  }]
}
```

For actual participants generate an independent random reference, for example
`study-` followed by `uuid.uuid4().hex` using Python locally. Never derive it from
a name, account, assessment token or email. Keep any contact-to-reference lookup
in a separate restricted file; do not include it in this JSON or Git. Record
consent evidence separately; this field is the operator's current disposition,
not a substitute for that evidence. Do not enter never-consented people.

| Field | Values and interpretation |
| --- | --- |
| `schema_version` | Exact version above; cannot silently change the form |
| `product_revision` | Full lowercase 40-character Git commit; one candidate per dataset |
| `data_kind` | `synthetic` for rehearsals; `participant` only for actual consented observations |
| `ref` | `study-` plus 32 random lowercase hexadecimal characters; unique per dataset |
| `consent` | `consented` or `withdrawn`; withdrawn participants contribute nothing to the summary |
| `cycle` | Integer 0 (entry), 1, 2 or 3 (weekly cycles) |
| `task` | Exact task ID in the protocol; must belong to that cycle |
| `outcome` | `completed` (observed task outcome), `unable` (attempted but blocked), `stopped` (started then chose to stop), `skipped` (offered but declined) |
| `assistance` | `none` (no observer help), `prompted` (observer helped), `not_observed` (unknown) |
| `time_band` | Participant-selected minutes: `under_2` (<2), `2_to_5` (2 to <5), `5_to_15` (5 to 15 inclusive), `over_15` (>15), `not_reported`; never derive from a stopwatch or browser analytics |
| `fit` | `fits`, `does_not_fit`, `uncertain`, `not_asked`; ask only for `context_choice` or `start_practice`, otherwise `not_asked` |
| `barrier` | Optional single primary category chosen with the participant: `none_reported`, `access`, `comprehension`, `burden`, `privacy_safety`, `not_asked`; no category means a diagnosis |

One row per participant/task/cycle. If a task was never offered or observed,
leave it absent. A participant who never returns has no invented later rows.
An assisted completion remains completed with `prompted`; it is not an unassisted
success. A skipped task normally uses unknown time/assistance/fit where those
were not reported. Do not infer a barrier from a stop or a fit judgment from
completion. Multiple or ambiguous barriers can be documented as minimized
interface defects in the separate private reviewer record; do not add arbitrary
free-text fields to this dataset.

## Retention and withdrawal

Proposed operational defaults for reviewer approval: delete raw observations,
consent/contact lookup and exports within 90 days of the final planned contact;
expire backups no later than 30 days after that deadline. Fill actual calendar
dates and authorized recipients into the information sheet before consent.
These are study choices, not automatic application settings or legal limits.
If the operator cannot implement them, agree and disclose a feasible policy
before collecting anything. Keep only separately reviewed, non-identifying
product corrections after that period.

On withdrawal, stop collection/contact, mark the reference withdrawn to exclude
it immediately, then remove its observations and applicable private copies under
the agreement. Regenerate aggregate outputs and retire previous copies; the CLI
does not recall files. Record the minimal disposal receipt separately, with a
backup expiry date. Keep no participant reference in public findings. If all
records are withdrawn or empty, the report must show no usable observations.

Study withdrawal, optional feedback purge, calibration withdrawal and account
deletion are separate operations. Use the existing preview-first operator
commands or participant controls for each; do not delete private account state
merely because someone leaves the study. Backups and previously distributed
exports need their own handling. No deletion or purge runs as part of this kit.
