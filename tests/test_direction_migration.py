"""Empty additive rollback is safe; populated-table rollback requires a backup."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_direction_migration_round_trip_keeps_existing_data(tmp_path):
    root = Path(__file__).resolve().parents[1]
    environment = {
        **os.environ,
        "APP_DATA_DIR": str(tmp_path),
        "DJANGO_SETTINGS_MODULE": "grounded_growth.settings",
        "APP_DEBUG": "true",
        "DJANGO_SECRET_KEY": "isolated-migration-test",
    }

    def migrate(target):
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate", "growth", target, "--noinput"],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr

    migrate("0013")
    database = tmp_path / "grounded_growth.sqlite3"
    with sqlite3.connect(database) as db:
        db.execute(
            "INSERT INTO growth_curriculumversion VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("migration-fixture", "v1", "v1", "v1", "a" * 64, 1, "2026-09-29 00:00:00"),
        )
        original = db.execute("SELECT * FROM growth_curriculumversion").fetchall()
        tables_before = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        migrations_before = db.execute(
            "SELECT app, name FROM django_migrations ORDER BY app, name"
        ).fetchall()
    migrate("0014")
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT COUNT(*) FROM growth_practicedirectionrevision").fetchone() == (
            0,
        )
        assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert db.execute("SELECT * FROM growth_curriculumversion").fetchall() == original
    migrate("0013")
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT * FROM growth_curriculumversion").fetchall() == original
        assert (
            db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            == tables_before
        )
        assert (
            db.execute("SELECT app, name FROM django_migrations ORDER BY app, name").fetchall()
            == migrations_before
        )
    migrate("0014")
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT * FROM growth_curriculumversion").fetchall() == original
        assert db.execute("SELECT COUNT(*) FROM growth_practicedirectionrevision").fetchone() == (
            0,
        )
