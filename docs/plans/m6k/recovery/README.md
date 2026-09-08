# M6K recovered source checkpoint

Recovered on 2026-09-08 from the owner-supplied execution package. This is a
reconstruction of the lost local recovery work, not either of the missing
commits `f874d49` or `d5eb6ff`.

All 383 competency drafts are preserved in `selected/exercises/`. Nineteen
domain files come from the hash-pinned unpublished archive; eight come from
its declared source base `c3491a4`. The seven domain files already on current
main are byte-identical. Domain 07 existed on that source branch but never
reached current main. Current main has 91 tailored runtime practices, not 105.

`source-inventory.json` records each canonical definition and semantic source
fingerprint. `reconciliation.json` records file origins and both versions of
changed source notes. The recovered cumulative source ledger is preserved
without treating its references as newly inspected evidence.

The original nested ZIP preserves its supporting archives and unfinished
compiler preparation intact. None of that archived code is executed or
installed as a runtime overlay. The later completion compiler was not archived.

`runtime-invariants.json` pins all 383 package hashes, 1,151 action IDs,
completion/evidence hashes and protected baseline files. It explicitly names
the five frozen legacy and four retained typed packages. The initial quality
ledger keeps all seven review dimensions pending for all 383 IDs and QA-01
through QA-05 open. Later evidence must be appended elsewhere; this baseline
must never be rewritten to manufacture acceptance.

Run `.venv/bin/python docs/plans/m6k/recovery.py` to verify. Initialization
refuses to overwrite an existing checkpoint. No participant data, source
activation, scored action, assessment or runtime package changes are included.
