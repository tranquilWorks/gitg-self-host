# Installation choices, version checks and recovery

## Choose a personal start or a demonstration

Copy `.env.example` to `.env`, replace the secret and bootstrap credentials, and
set the hostnames/IP addresses used to open the instance. New containers default
to `APP_SEED_DEMO=false`: the complete practice library is imported, but no
assessment is invented for the first account. Sign in and take or import your own
assessment. Home explains the next step until then.

To explore the example first, explicitly set `APP_SEED_DEMO=true` before starting.
Startup adds the Pilot 002 demonstration to the earliest-created account. Its
results are labelled as a demonstration, not your personal assessment. Use a
separate installation/Compose project if you want a disposable demonstration.
A second account does not automatically receive the example.

```bash
docker compose config --quiet
docker compose pull
docker compose up -d --no-build --wait --wait-timeout 180
docker compose exec app python manage.py installation_status --check
```

Changing `APP_SEED_DEMO` later requires container recreation, for example
`docker compose up -d --no-build --force-recreate --wait --wait-timeout 180`.
False never removes an existing demo, personal assessment, active practice or
history. True is an explicit request to add the example if absent. Repeated
startup preserves existing passwords and does not create duplicate demo runs.
Only the literal values `true` and `false` are accepted; a typo stops before
migrations or seeding. This mode neither enables research consent nor changes
scoring or practice activation.

The existing explicit `manage.py seed_canonical` command still includes Pilot 002
for compatibility with established development/readiness workflows. Operators who
want library-only reconciliation should use `seed_canonical --without-demo`.
Container startup uses `seed_canonical --startup` to respect the configured choice.
The historical importer remains byte-identical. The separate library-only importer
reuses its validation and in-progress practice guards; shared-record parity and
transaction rollback are tested.
Do not run the legacy command expecting a personal-only start.

## Identify the installation before updating

Open **Account → Installation version and recovery help**, or run
`docker compose exec app python manage.py installation_status`. The JSON contains
only the embedded revision, demo-seeding flag, readiness boolean and issue codes.
It sends no request to a remote service. `--check` exits nonzero when attention is
needed. This is a configuration/database check, not a backup or evidence replay.
The public health endpoint remains only `{"status":"ok"}`.

Published images embed the full Git revision at build time. Unknown/malformed
metadata is shown as `unknown`, never guessed from the source checkout or a
mutable image tag. Metadata is not a signature, does not identify uncommitted
source edits, and is different from a registry digest or local image ID.
For a clean source build:

```bash
git status --short
# Commit or set aside intended edits before identifying a reproducible revision.
APP_BUILD_REVISION="$(git rev-parse HEAD)" docker compose build app
docker compose up -d --no-build --wait --wait-timeout 180
```

If you intentionally build an uncommitted tree, leave `APP_BUILD_REVISION` unset
so the revision is `unknown`. No Git binary is needed in the running container.

Record both the local image ID and available registry digest before changing it:

```bash
container_id="$(docker compose ps -q app)"
image_id="$(docker inspect --format '{{.Image}}' "$container_id")"
docker image inspect "$image_id" --format '{{.Id}} {{json .RepoDigests}}'
```

Use the matching `ghcr.io/tranquilworks/gitg-self-host@sha256:…` repository digest
in `APP_IMAGE` for an immutable registry pin. A `sha-<full-commit>` tag is also
published; `latest` moves. Keep the prior image locally and record its reference
with the backup. A source build may have no repository digest: keep the local
image and exact clean source revision. Changing `.env` does not change an already
running container until it is recreated.

## Resolve a startup or login problem

| Observation / issue code | Next action |
| --- | --- |
| Compose configuration is invalid | Run `docker compose config --quiet`; check `.env` location, syntax and port availability. The non-quiet command can print secrets. |
| Required secret/hosts missing, or invalid `APP_SEED_DEMO` | Correct the named setting in `.env`, then recreate the container. Settings validation can stop before the status command runs. |
| `example_secret`, `debug_enabled`, `hosts_not_restricted` | Replace the example secret, set `APP_DEBUG=false`, and list actual hostnames/IPs instead of `*`. Changing a secret invalidates sessions and signed previews. |
| HTTP 400 when opening the instance | Add the hostname/IP actually used to `DJANGO_ALLOWED_HOSTS` and recreate. Never put a URL scheme or port in that hostname list. |
| Login succeeds but the session does not persist over local HTTP | Keep `APP_SECURE_COOKIES=false` for HTTP; use true when actually served through HTTPS. |
| Forgotten password | Reset the existing account with the local password command below. Bootstrap variables only create the first account and never reset an existing password. |
| `database_not_initialized`, `account_not_initialized` | Confirm the correct persistent volume and image first. For an intentional fresh install, provide bootstrap credentials and allow normal startup to initialize it. An unexpectedly empty volume is not a reason to overwrite an old backup. |
| `database_unavailable_or_incomplete`, `database_integrity_failed` | Stop writes, preserve the volume, and inspect logs/permissions. Restore only a verified backup using its matching image. The diagnostic does not repair corruption. |
| `migration_mismatch` | Check that image and volume belong together. Use the normal startup migration path for an intended upgrade, or the matched image/backup rollback below. Do not fake migration history. |
| `unsupported_database` | This installation workflow supports SQLite; use the documented single-service configuration. |
| Changed instructions blocked by an active or paused practice | Return to the prior image, finish or explicitly stop the affected practice there, then retry. Never delete the practice or bypass the importer guard. |

```bash
docker compose ps
docker compose logs --tail 100 app
docker compose exec app python manage.py changepassword <username>
```

The password command prompts locally; do not place the new password in a shell
argument. If Gunicorn is unavailable, use the matching installed image and
`docker compose run --rm --no-deps --entrypoint python app manage.py changepassword <username>`.
After first login, remove the bootstrap password from `.env` and recreate the
container. Existing account hashes remain unchanged on subsequent startups.

## Update, restore or roll back

Follow [backup and restore](backup-and-restore.md) for the ordered workflow.
Pause writes while making the pre-upgrade backup and comparing it to live state.
Keep the database file and its manifest together, verify both, and copy the pair
to protected storage outside the host. An account JSON archive cannot restore the
database. Record the prior image before selecting/pulling a replacement.

After updating, check health, `installation_status --check`, migration status,
evidence replay, both historical/composite score replays and operations readiness;
then sign in and inspect current practice/history. If verification fails, preserve
the failed state and stop before accepting new work. Restore while the app is
stopped, using the backup's matching image and verifying the snapshot before
copying and the restored database before startup. This can discard writes made
after the snapshot: choose the restore point deliberately.

The automated acceptance uses only synthetic data in an isolated volume. It
exercises personal startup, explicit demo opt-in, existing-account preservation,
embedded revision, container recreation and verified backup restoration. Unit
checks cover malformed configuration, missing/corrupt database, migration mismatch,
missing account and privacy of diagnostic output. This does not operate on a live
owner volume or certify an untested deployment.

Docker references checked 30 September 2026: [Compose startup options](https://docs.docker.com/reference/cli/docker/compose/up/),
[build arguments](https://docs.docker.com/reference/compose-file/build/), and
[pulling an image by digest](https://docs.docker.com/reference/cli/docker/image/pull/).
