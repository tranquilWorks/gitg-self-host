# Owner-accepted catalog publication

The owner explicitly accepts the product quality for inspection and authorizes final audit/polish, merge and publication of a Docker image. Baseline: `bdc092b`. This authorizes the release operation under the engineering-execution procedure; it does not fabricate learner, specialist or formal per-competency review receipts. Those historical records remain unchanged.

## Final audit and polish

The audit traced the existing report and 383-row implementation register through authenticated guide routes, separate prompts/answers/resources and exports, safe Markdown, keyboard-scrollable mobile tables, and prospective import protection. The existing integration receipts provide the complete source, browser, replay, persistence and backup/restore evidence. No additional source editorial sweep or curriculum/scoring change is introduced.

A measured cold catalog load took 16.035 seconds. Selecting PyYAML’s safe native backend reduced it to 4.272 seconds on the same machine. Both produced content hash `ed41c16509d8c86a0f2e5fa44b5944d97309afd0532ba7dabf0cbf328a76ba8a` and 383 protocols. All four new tests passed: equality with the original safe loader for every catalog YAML document, rejection of Python-object construction on both backends, and the safe Python fallback. This is a local timing observation, not a load benchmark.

The install/update documentation now reflects all 383 authored competencies, published image selection, version pinning, verified backups and the guard against replacing active/paused practice instructions. No running owner instance is upgraded by this work.

Local release checks: Ruff, Django checks and no migrations passed; all nine deployment/parser tests passed. Exact 383-guide/1,151-action parity passed. The deterministic compiler is checked before committing. The full hosted workflow verifies the merge candidate and the main revision before publication. A final probe review caught missing required Django settings in the publishing command; the corrected command passed against a fresh Docker build (`c5875535e5b5`), reporting the same catalog and legacy hashes. The five deployment contract tests passed again after that correction.

## Publication contract

The existing full CI remains required before merge. The new publishing job runs only for main after the aggregate Pilot readiness gate succeeds. It publishes Linux AMD64/ARM64 images to `ghcr.io/tranquilworks/gitg-self-host`, with `latest`, a full-commit tag and a digest. The job pulls the resulting digest and runs canonical validation. The source-only publication probe supplies explicit synthetic Django settings and an ephemeral data directory; it does not start a server or use operator credentials. Repository and revision labels identify the source. Compose supports published images and retains explicit local builds.

GitHub package visibility is controlled separately. The publishing job uses the repository token with package-write permission. The operator CLI token currently lacks package-read permission; anonymous access or owner registry authentication must be verified after publication. The deployment guide includes GitHub’s documented authentication and package-visibility routes.

Exact CI, merge and registry outcomes belong to the linked pull request and publishing run. A successful local check alone does not mean the image was published. Specialist and actual-learner evidence remain separate from the owner’s explicit acceptance and release authorization.
