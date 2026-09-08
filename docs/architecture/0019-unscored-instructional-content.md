# ADR 0019: Unscored teaching, materials and separate checks

Status: M6K-01-01 software implementation; final browser and release verification pending.

The recovered sources promise materials they do not always supply and sometimes
print answers inside a purported unaided prompt. Extra prose in a scored action
cannot by itself support a fair self-guided attempt. The M6K successor adds an
optional `GG-INSTRUCTIONAL-CONTENT-1.0` document with concepts, complete materials,
worked examples, capability-fit pathways, next steps, prompts and separate keys.
It is explicitly unscored. These sections never allocate action IDs or credit.

Typed authoring sources may supply `instructional_content`. The compiler puts
the document in the canonical protocol and projects it into imported
`setup_copy`. The existing importer compares that configuration before any
writes and refuses a change while an active or paused sprint depends on it.
No models, migrations, historical evidence or score calculation change.

The five frozen protocols cannot receive this inline field. A release may
explicitly list a companion under `registries/guides/<ID-without-dot>.yaml`.
The manifest schema restricts filenames to the five frozen IDs, and validation
checks the exact parent. Companions participate in the content hash, but remain
outside the frozen runtime fingerprint and all scored rules. They are current
unscored reference material; they are not historical sprint evidence snapshots
or rewritten frozen protocols. No companion is selected in this release.

The authenticated guide route supplies an initial teaching/materials view.
Every prompt opens separately with only its explicitly referenced materials;
teaching and worked answers are excluded from the attempt response. Keys enter
HTML, text or Markdown output only after an explicit check request. Each key
has exactly one prompt owner; IDs and material references fail closed. An
answer is never merely hidden in CSS or a collapsed HTML element. This is
instructional integrity, not proctoring; the learner can request a check at
any time and must distinguish assisted from prior unaided responses.

The renderer uses escaped text and native links, ordinary headings and lists,
and a view-specific text/Markdown download. Long material wraps without a new
frontend framework or JavaScript dependency. Guide requests use private,
no-store responses and write no events, attempts, timing, or telemetry.

All 27 authoring files are now staged, but `implemented_competency_ids`
explicitly selects only the existing 91 runtime projections. Every source is
structurally validated; an unselected source remains a draft. The compiler
does not infer protocol families for pending entries. The recovered cumulative
source ledger stays in the checkpoint until claim-level integration review.

Three related source drafts repair missing craft briefs (21.03), learning-key
leakage (10.01) and learner-visible compatibility metadata (10.02). They are
not runtime-selected or formally accepted. The initial quality ledger stays
immutable and pending. Full revision-bound receipt/dependency enforcement is
M6K-01-02, and independent review still requires a separate run with a
learner-only input bundle. Structural tests cannot certify meaning, source
support, accessibility, real learner outcomes or qualified acceptance.
