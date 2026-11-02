# UXA-01 shared shell

Issue #115 is the only implementation scope in this batch. PR #113 preserves
the October 7 feedback; issues #116–124 remain separate and open.

The shared footer links to `/data-policy/` instead of repeating scoring caveats.
Repeated Profile mastery/model footnotes, Weekly mastery notice and Personal OS
privacy reassurance are removed; their boundaries live on that policy surface.
Practice-specific credit consequences and actionable safety notices remain.
The policy covers installation-owner responsibility, stored records, exports,
backups, deletion, research consent and product limitations. It is available
before sign-in; Account links to it explicitly. No record is exported by this page.

Login offers working account creation through Django's UserCreationForm.
Passwords use configured validators and hashing, POST requires CSRF, new accounts
are neither staff nor superusers, and account creation does not seed a profile or
sign anyone in automatically. Anyone who can reach the instance can register by
default; operators can set `APP_ALLOW_REGISTRATION=false` in `.env` and recreate
the container to close registration. Existing accounts are unaffected. There is
no email verification or anti-abuse service in this batch; operators should
restrict network exposure or disable registration as appropriate.

Native `details.inline-help` is a reusable help disclosure: click or Enter/Space
opens it, Escape closes and returns focus, and Tab reaches its contents. No
required information depends on hovering or JavaScript. Shared focus outlines and
heading levels are explicit; ordinary informational notes use neutral colors.
Actionable validation/error treatments remain distinct. No text is hidden by CSS.

The shared shell and account-entry copy are audited here. Route-specific question,
profile, Personal OS, practice and weekly rewrites remain in their own UXA issues;
this batch does not claim the entire application has passed the final copy audit.
