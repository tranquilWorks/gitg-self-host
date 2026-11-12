# TranquilWorks dark theme

## Authorization and boundary

On 12 November 2026 Kian requested dark mode for the app and a palette matching
tranquilworks.dev. This is a separate presentation-only batch, based on merged
main `cc3b56a9c4662737022540c2970032c1dad8d63f` (#132). No later UXA/product slice,
deployment, participant data, assessment/scoring/storage change or CI/permission
change is included. Human verification in #131 remains open and unaccepted.

## Palette provenance and mapping

Read the actual live site's HTML and stylesheet using ordinary HTTPS on
12 November 2026. The reference was
`https://tranquilworks.dev/assets/index-D0IUqirT.css`, not an inferred screenshot
color. The public search reader could not open the site; direct HTTPS succeeded.
No remote stylesheet, font or other network dependency is added to the app.

| Role | TranquilWorks swatch | App use |
| --- | --- | --- |
| Ink | `#081114` | Page background and text on filled actions |
| Deep ink | `#050b0e` | Header |
| Surface | `#0d181c` | Panels and dialogs |
| Raised surface | `#142328` | Fields and muted panels |
| Paper | `#edf3ef` | Main text |
| Muted | `#a8b5b0` | Secondary text and placeholders |
| Signal | `#e6ad4b` | Primary actions, focus, progress |
| Soft signal | `#ffd486` | Hover and warning text |
| Moss | `#79bea9` | Links, secondary actions, positive state |
| Oxide | `#e17555` | Errors and destructive actions |

App legacy token names are retained: `--ink` means text and `--paper` means
background, so their role mapping is intentionally reversed from the site's names.
Additional dark semantic backgrounds/borders preserve readable warning/error and
control contrast. The default is dark even when the OS preference is light; no
settings, cookies, storage, scripts or theme toggle are needed. System forced
colors remain in control. Existing reduced-motion and hidden-state rules remain.

## Implementation

- One locally served final `dark_theme.css` layer after all shared/page styles.
- Base metadata advertises dark native controls and the blue-black browser color.
- All existing template-based surfaces inherit the theme, including public auth
  and policy pages. Native selects, input/textarea fills, autofill text, checkbox
  accent, button variants, dialogs, backdrop, warning/error/contrary state and
  focus rings are covered. No filter-based inversion or content recoloring script.
- Existing `app.css`, lesson renderer inputs, canonical material and all services
  are unchanged. No historical content receipts are rehashed or promoted; actual
  owner/source/accessibility acceptance remains separate.

## Actual verification before publication

- Focused theme/auth/stage suite: **34 passed in 34.08 seconds**. This includes
  25 new static palette/request tests and existing account/stage regressions;
  the suite's counts are not a whole-repository pass.
- Palette checks require at least 4.5:1 for the enumerated text pairs and 3:1 for
  field boundaries/focus. They check declared pairs, not every rendered pixel or
  a claim of full accessibility compliance.
- Two new Playwright cases collected at 390/1280: actual computed native colors,
  keyboard focus, wrong-password error, assessed app pages, Share modal/Escape
  focus return, destructive-action contrast and forced-colors control. The fixture
  uses synthetic seeded/golden assessment data; not human testing or a new full
  assessment lifecycle. Eighteen new `dark-{state}-{390,1280}` screenshots are
  configured (login, login-error, home, Personal OS, practices, Weekly, Account,
  Profile, Share). Collection is **not execution**.
- Actual local Chromium launch failed with `socket() failed: Operation not
  permitted`; no permission workaround, package install or retry. No local
  browser execution, screenshots, forced-colors or mobile visual acceptance is
  claimed. Docker is unavailable; no local Compose pass is claimed.
- Separate existing presentation plus current-governance-fingerprint regression
  suite: **19 passed in 34.21 seconds**. This confirms no historical renderer
  report drift without modifying the renderer or report. Do not sum overlapping
  suites as a new whole-repository total.
- Fast full-repository contract passed: **3,532 manifest entries**, Ruff and
  format (**2,067 Python files reported locally**), Django system checks and no
  migration drift. Exact eight-path scope audit: zero violations; protected
  code/data/authoring/CI and old renderer CSS diff empty. `git diff --check` passed.
- All **71 browser cases collected / 2,095 non-browser deselected**; not execution.
  Full pytest/readiness, browser execution and Compose remain distinct from
  these local preflight receipts.

## Remaining verification

Review actual desktop/mobile captures before asserting visual acceptance. Check
active work/guide/check-in, invalid form/error recovery, selected assessment
answers, modal help/share, completed/paused states and Account data/privacy as
well as the new captures. Existing lifecycle/no-JS/replay/owner tests stay intact.
Human device/keyboard/assistive-technology judgment remains uncompleted in #131;
neither these tests nor a future agent screenshot review can close it. Nothing
is deployed by this styling batch.
