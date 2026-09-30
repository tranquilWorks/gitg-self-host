"""Local installation metadata and diagnostics; never fetch remote state."""

import re
import sqlite3
from pathlib import Path

from django.conf import settings
from django.db.migrations.loader import MigrationLoader


def installation_information():
    try:
        revision = (settings.BASE_DIR / "BUILD_REVISION").read_text(encoding="ascii").strip()
    except (OSError, UnicodeError):
        revision = "unknown"
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        revision = "unknown"
    return {"revision": revision, "demo_seed_enabled": settings.SEED_DEMO}


def installation_diagnostics():
    """Return an allowlist of statuses, without secrets, paths or record values."""
    issues = []
    if settings.DEBUG:
        issues.append("debug_enabled")
    if settings.SECRET_KEY in {"replace-with-a-long-random-secret", "unsafe-local-development-key"}:
        issues.append("example_secret")
    if not settings.ALLOWED_HOSTS or "*" in settings.ALLOWED_HOSTS:
        issues.append("hosts_not_restricted")
    if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
        issues.append("unsupported_database")
    else:
        path = Path(settings.DATABASES["default"]["NAME"]).resolve()
        if not path.is_file():
            issues.append("database_not_initialized")
        else:
            database = None
            try:
                database = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)
                if database.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                    issues.append("database_integrity_failed")
                applied = set(database.execute("SELECT app, name FROM django_migrations"))
                loader = MigrationLoader(None)
                expected = set(loader.disk_migrations)
                if expected != applied:
                    issues.append("migration_mismatch")
                if not database.execute("SELECT 1 FROM auth_user LIMIT 1").fetchone():
                    issues.append("account_not_initialized")
            except sqlite3.DatabaseError:
                issues.append("database_unavailable_or_incomplete")
            finally:
                if database is not None:
                    database.close()
    return {**installation_information(), "ready": not issues, "issues": issues}
