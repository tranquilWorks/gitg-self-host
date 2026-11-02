# UXA-01 verification checkpoint

Owner authorized repair/merge of PR #113 and one implementation PR for #115.
No later UXA issue is included. PR #113's historical quality job failed because
the feedback document was absent from MANIFEST.tsv; the exact missing-entry
repair is published as c85b97e. Browser and Compose had passed on the prior head,
but fresh exact-head verification is still required before merge.

Implemented: public policy and ordinary account entry, Django password/CSRF
validation, operator registration switch, shared footer consolidation, visible
focus and native dismissible help, clearer entry copy and neutral informational
styling. Actual error alerts retain their existing treatment. The policy is
reachable without access to private records. No canonical content, score,
evidence, model or migration changed. Existing application pages stay authenticated.

Initial focused run: 25 passed, one failed because an existing test expected
the removed shared-footer disclaimer on Profile. That assertion now checks
the policy link and the same human-worth statement at its new destination.
Four new account/policy tests passed independently. No prior failure is relabeled.

Environment: Python 3.13.16 / Django 6.0.9. Initial full harness bootstrap failed
because uv's venv lacked pip; ensurepip repaired the environment without changing
requirements or gates. Full local verification is running; not yet a pass.
Chromium installation failed with truncated CDN downloads. Docker is absent;
no local browser/screenshot or Compose pass is claimed. Required hosted checks
and visual artifact inspection remain outstanding. No deployment or human
acceptance is claimed. Do not close #115 until exact-head gates are complete.
