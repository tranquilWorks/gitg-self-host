# Explicit practice connections

`GG-PRACTICE-DIRECTION-1.0` records an owner’s chosen intention for one
assessment period and canonical practice protocol. It has four explicit states:
unknown, declined, selected saved priority, or authored intended outcome.
No connection is created merely by visiting a page or starting a practice.
Unknown and declined impose no penalty and do not prevent practice.

A saved priority points to an exact immutable Personal OS revision and its
zero-based position. The snapshot binds that source revision and content hash.
Changing the priority stack never silently retargets an existing connection.
An intended outcome is private text, limited to 500 characters. The system does
not interpret either kind of prose, match it to competencies, or use it in
recommendation, assessment, evidence, completion or score mathematics.

Each changed choice appends a contiguous revision. An unchanged save creates no
additional record. Saves lock the assessment record and check both the submitted
connection revision and Personal OS revision. Concise direction reviews check
the Personal OS revision and merge only mission, anti-goals, priority stack and
twelve-month direction; principles and audit responses remain intact. An old
assessment form cannot save into the current period. Ownership, snapshots,
source priority and revision sequences are verified before showing intentions.
Database contention or concurrent saves ask the owner to reload, without
returning private values in error text.

Setup and weekly planning show the **current** connection for the practice and
assessment period. This is not an immutable attachment to an individual sprint
or weekly plan: revising it changes that current display, while prior choices,
plans, reviews and evidence remain unchanged. An active practice from another
assessment period does not inherit the current period’s connection. Cross-period
navigation and explicit reuse remain M6L-05 work. Both review pages show prior
revisions in pages of five and require an authenticated owner. No automatic
review schedule, telemetry or prose analysis is introduced.

## Private data and operations

Migration `0014_practice_direction_revision` adds one table and no backfill.
The owner-only archive becomes `grounded-growth-owner-private-archive-v4` with
`practice_direction_revisions`. Source references use the existing archive
assessment reference and Personal OS revision number, not opaque record IDs.
Account deletion includes the new records before deleting their source Personal
OS revisions. Retention never silently purges these intentions. Shared evidence,
pilot and calibration export contracts are unchanged and exclude this text.
Database backup fingerprints include the new table; operations readiness checks
its immutable history. Existing backup files remain independent private copies.

Before upgrade, create and verify a backup with the installed version using the
[backup procedure](backup-and-restore.md). Reverting presentation/service code
can leave the additive table and intentions intact. Rolling migration 0014 back
removes its table: only do that on an empty table or after preserving a verified
backup and accepting that later intentions are absent from the older application.
Restore an older backup with its matching application version, then migrate
forward deliberately. Do not use a newer table inventory to claim that an older,
unmigrated backup matches the new schema. No live owner data is used by tests.
