# M6K recovery evidence — 2026-09-08

Scope: M6K-00-01 and M6K-00-02 reconstructed from the supplied archive against
main `8aaf3a27b2522e09c7796fb3ad256ce481eb7932`. The archive predates the lost
local implementation commits. New commits will have new identities.

The supplied execution ZIP has SHA-256
`be79b722b2fcc3a022892a21ac88c3b046545f21e507812390e39a92b5a593c8`;
all 18 declared member hashes pass. Its unpublished input ZIP has SHA-256
`c22e69229a8836b8e21dbf74228ac014205f3bef9e2a68b2d50dae9ddfe82597`;
all 22 declared input/supporting files pass.

All 383 canonical IDs have retrievable exact sources and no unresolved source
conflicts. The reconciliation retains both versions of changed source notes.
All 383 protocol packages, 1,151 action identities, completion/evidence hashes,
and protected curriculum, assessment, model and replay files remain unchanged.

Executed `.venv/bin/python -m pytest tests/test_m6k_recovery.py -q`:
**5 passed in 26.65 seconds**. Checks cover the exact recovered baseline,
archive tampering, changed source bytes, fabricated initial acceptance and
changed protected rules. They establish recovery/software integrity only.

Current runtime: 91 individually authored projections, 292 rewrite-pending.
Recovered source drafts: 383. New scope/instructional/cold-start/integration/
learner/qualified/owner acceptances: zero. Browser, Compose and hosted release
verification are not established by these source-only recovery checks.

The owner explicitly authorized public GitHub publication of the recovered
source bundle and a PR. This recovery checkpoint is ready for that publication.
The active successor scope also permits reconstruction of instructional
support and three prepared content repairs; those are separate work and must
carry their own verification and honest dependency states.
