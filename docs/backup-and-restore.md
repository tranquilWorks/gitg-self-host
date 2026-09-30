# Backup, upgrade, restore, and rollback

## What the backup contains

Grounded Growth uses SQLite's online backup API instead of copying a live WAL
database file. A database snapshot includes account, assessment, profile,
context, Personal OS, practice, draft/submitted check-in, evidence, score,
review, weekly-execution, assessment-calibration consent, and optional
pilot-feedback data. Treat the database and every copy as sensitive private
data.

The downloadable owner archive is not a restorable database backup. The
minimized evidence, pilot-feedback, and consent-filtered assessment calibration
JSON files are analysis exports and also cannot restore the application. The
calibration file contains linkable item responses and timing and remains
sensitive even without account identity.

## Create and verify a pre-upgrade backup

Pause application writes while creating and comparing a pre-upgrade snapshot.
Choose a new explicit filename for each snapshot so restore cannot select the
wrong pair. Never overwrite an existing backup:

```bash
docker compose exec app python manage.py backup_database \
  --output /data/backups/pre-upgrade.sqlite3
docker compose exec app python manage.py verify_database_backup \
  /data/backups/pre-upgrade.sqlite3 --compare-live
```

The command writes both files atomically with mode `0600`:

```text
/data/backups/pre-upgrade.sqlite3
/data/backups/pre-upgrade.sqlite3.manifest.json
```

It refuses to overwrite either an existing snapshot or sidecar. Move the
previous pair to its dated archive location or choose a new explicit filename.

The sidecar manifest contains no row values or database identifiers. It records
only the backup byte length and hash, SQLite integrity result, applied-migration
count/hash, and counts/hashes for critical owner state. `--compare-live`
requires the snapshot migrations and critical-state fingerprint to match the
live database exactly.

For a timestamped snapshot under `/data/backups`, use `make backup`. Keep an
independent encrypted copy outside the Docker host. Future files under
`/data/uploads` are not part of the SQLite snapshot.

## Upgrade and verify

Do not continue if backup verification fails. Record the running image ID and
repository digest using the [operator guide](operator-convenience.md). A Git
checkout revision does not identify an already running published image. Keep
the previous image available and select the desired pinned `APP_IMAGE` in `.env`.
Finish or explicitly stop affected active/paused practices on the old version
before installing changed instructions. Never bypass the importer guard.

For a published image:

```bash
docker compose pull
docker compose up -d --no-build --wait --wait-timeout 180
docker compose exec app python manage.py installation_status --check
docker compose exec app python manage.py migrate --check
docker compose exec app python manage.py verify_evidence_events
docker compose exec app python manage.py rebuild_score_state --verify-only
docker compose exec app python manage.py rebuild_composite_score_state --verify-only
docker compose exec app python manage.py verify_weekly_execution_readiness
docker compose exec app python manage.py verify_m6h_operations_readiness
docker compose exec app python manage.py verify_assessment_calibration_collection
curl --fail http://127.0.0.1:${APP_PORT:-3000}/health/
```

For a source build, use the exact clean source revision and the build command in
the operator guide before `up --no-build`. Keep the source checkout and operational
instructions matched to the image. Sign in and verify the profile, current
practice, evidence/history, Personal OS, weekly execution and Account pages before
resuming writes.

## Roll back a failed upgrade

Choose the exact pre-upgrade image and verified snapshot together. Restoring a
snapshot discards later writes, so preserve the failed state separately if needed
before replacing it. Stop the app before replacing SQLite; never copy over a
running WAL database. Do not delete the named volume.

1. Run `docker compose down` and set `APP_IMAGE` back to the recorded pre-upgrade
   digest (or preserved local image). For a source build, restore the matching
   clean checkout and build that revision first.
2. Verify the backup with the selected image before copying. Stop on any error:

   ```bash
   docker compose run --rm --no-deps --entrypoint python app manage.py verify_database_backup /data/backups/pre-upgrade.sqlite3
   ```

3. Only after successful verification, restore while stopped:

   ```bash
   docker compose run --rm --no-deps --entrypoint python app -c 'from pathlib import Path; import shutil; source=Path("/data/backups/pre-upgrade.sqlite3"); target=Path("/data/grounded_growth.sqlite3"); shutil.copy2(source, target); target.chmod(0o600); target.with_name(target.name + "-wal").unlink(missing_ok=True); target.with_name(target.name + "-shm").unlink(missing_ok=True)'
   docker compose run --rm --no-deps --entrypoint python app manage.py verify_database_backup /data/backups/pre-upgrade.sqlite3 --compare-live
   ```

4. Start only after the restored state matches:

   ```bash
   docker compose up -d --no-build --wait --wait-timeout 180
   ```

5. Repeat the migration, evidence, both score, weekly and operations checks above,
   and sign in to inspect the restored records. Older images predating
   `installation_status` can be identified through Docker; use their documented
   checks instead of assuming this new command exists.

If verification fails, keep the application stopped and preserve both files.
Investigate the selected image, volume, backup and sidecar; do not waive a mismatch.
The backup manifest detects corruption and inconsistency; it is not an external
signature or proof against a person who can replace both files.

## Isolated restore drill

`make compose-smoke` uses a throwaway Compose project and named volume. It
creates synthetic owner state, verifies a pre-upgrade backup, changes account
state across recreation, restores while stopped, and proves exact critical-
state replay plus every established readiness contract.

## Deletion and retention copies

Live account deletion and retention do not edit existing backups. A backup may
still contain a deleted account, drafts, feedback, and private narrative. Apply
the operator's agreed lifecycle separately to backup and encrypted off-host
copies; never claim erasure until that lifecycle is completed and documented.

`APP_OWNER_RETENTION_ENABLED=false` is the default. Enabling it creates no
timer, startup mutation, or background task. The authenticated owner must still
preview and confirm each application. Only old draft check-ins and optional
pilot feedback are eligible; immutable developmental history is never targeted.

## Volume deletion warning

`docker compose down` preserves data. `docker compose down --volumes` deletes
the named volume and should be treated as permanent destruction unless an
independent, verified backup exists.
