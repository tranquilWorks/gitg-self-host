import json
import os
import sqlite3
import subprocess
import sys
from io import StringIO

import pytest
from django.core.management import CommandError, call_command
from django.db import connection
from django.db.migrations.loader import MigrationLoader

from growth.installation import installation_diagnostics, installation_information
from growth.models import AssessmentRun, LeverBaseline, PracticeProtocol


def test_invalid_startup_choice_fails_before_database_creation(tmp_path):
    result = subprocess.run(
        [sys.executable, "manage.py", "check"],
        env={
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "grounded_growth.settings",
            "APP_DATA_DIR": str(tmp_path),
            "APP_SEED_DEMO": "mistyped",
            "DJANGO_SECRET_KEY": "test-only-private-value",
            "DJANGO_ALLOWED_HOSTS": "localhost",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "APP_SEED_DEMO must be true or false" in result.stderr
    assert "test-only-private-value" not in result.stderr
    assert not (tmp_path / "grounded_growth.sqlite3").exists()


@pytest.mark.django_db
def test_personal_start_then_opt_in_and_disable_demo_preserves_existing_history(user, settings):
    settings.SEED_DEMO = False
    call_command("seed_canonical", "--startup")
    assert PracticeProtocol.objects.count() == 383
    assert not AssessmentRun.objects.exists()
    assert not LeverBaseline.objects.exists()
    password = user.password
    settings.SEED_DEMO = True
    call_command("seed_canonical", "--startup")
    call_command("seed_canonical", "--startup")
    run = AssessmentRun.objects.get()
    assert run.source == AssessmentRun.Source.PILOT_SEED
    before = list(AssessmentRun.objects.values()), list(LeverBaseline.objects.values())
    settings.SEED_DEMO = False
    call_command("seed_canonical", "--startup")
    call_command("seed_canonical", "--without-demo")
    assert (list(AssessmentRun.objects.values()), list(LeverBaseline.objects.values())) == before
    user.refresh_from_db()
    assert user.password == password


@pytest.mark.django_db
def test_personal_start_preserves_real_assessment_without_adding_demo(user, settings):
    from growth.services.assessment import persist_assessment_run
    from tests.test_assessment_integration import golden_payload

    call_command("seed_canonical", "--without-demo")
    run, _ = persist_assessment_run(user, golden_payload())
    before = list(AssessmentRun.objects.values()), list(LeverBaseline.objects.values())
    settings.SEED_DEMO = False
    call_command("seed_canonical", "--startup")
    assert AssessmentRun.objects.get().pk == run.pk
    assert (list(AssessmentRun.objects.values()), list(LeverBaseline.objects.values())) == before


@pytest.mark.parametrize("value", [None, "unknown", "abc", "<script>private</script>", "a" * 40])
def test_revision_is_bounded_build_metadata(tmp_path, settings, value):
    settings.BASE_DIR = tmp_path
    if value is not None:
        (tmp_path / "BUILD_REVISION").write_text(value)
    info = installation_information()
    assert info["revision"] == (value if value == "a" * 40 else "unknown")
    assert set(info) == {"revision", "demo_seed_enabled"}


def diagnostic_database(tmp_path, settings, *, migrations=True, account=True):
    path = tmp_path / "probe.sqlite3"
    database = sqlite3.connect(path)
    database.execute("CREATE TABLE django_migrations (app TEXT, name TEXT)")
    database.execute("CREATE TABLE auth_user (id INTEGER)")
    if migrations:
        database.executemany(
            "INSERT INTO django_migrations VALUES (?, ?)", MigrationLoader(None).disk_migrations
        )
    if account:
        database.execute("INSERT INTO auth_user VALUES (1)")
    database.commit()
    database.close()
    settings.DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": path}}
    settings.DEBUG = False
    settings.SECRET_KEY = "PRIVATE-CONFIGURATION-SENTINEL"
    settings.ALLOWED_HOSTS = ["private-host.example"]
    return path


@pytest.mark.parametrize("case", ["ready", "missing", "corrupt", "migrations", "account"])
def test_diagnostics_read_only_and_failures_are_actionable(tmp_path, settings, case):
    path = diagnostic_database(
        tmp_path, settings, migrations=case != "migrations", account=case != "account"
    )
    if case == "missing":
        path.unlink()
    elif case == "corrupt":
        path.write_bytes(b"not a database")
    before = path.read_bytes() if path.exists() else None
    result = installation_diagnostics()
    assert result["ready"] == (case == "ready")
    expected = {
        "ready": [],
        "missing": ["database_not_initialized"],
        "corrupt": ["database_unavailable_or_incomplete"],
        "migrations": ["migration_mismatch"],
        "account": ["account_not_initialized"],
    }
    assert result["issues"] == expected[case]
    assert (path.read_bytes() if path.exists() else None) == before
    output = json.dumps(result)
    assert "PRIVATE-CONFIGURATION-SENTINEL" not in output
    assert "private-host.example" not in output
    assert str(path) not in output
    stream = StringIO()
    if case == "ready":
        call_command("installation_status", "--check", stdout=stream)
    else:
        with pytest.raises(CommandError, match="needs attention"):
            call_command("installation_status", "--check", stdout=stream)
    assert json.loads(stream.getvalue()) == result


def test_diagnostics_flag_example_config_without_printing_it(tmp_path, settings):
    diagnostic_database(tmp_path, settings)
    settings.DEBUG = True
    settings.SECRET_KEY = "replace-with-a-long-random-secret"
    settings.ALLOWED_HOSTS = ["*"]
    assert installation_diagnostics()["issues"] == [
        "debug_enabled",
        "example_secret",
        "hosts_not_restricted",
    ]


@pytest.mark.django_db
def test_installation_page_requires_authentication_is_read_only_and_private(client, user):
    url = "/account/installation/"
    assert client.get(url).status_code == 302
    client.force_login(user)
    before = connection.introspection.table_names()
    response = client.get(url)
    assert response.status_code == 200
    assert b"Know what is running." in response.content
    assert b"Personal start is selected." in response.content
    assert "no-store" in response["Cache-Control"]
    assert client.post(url).status_code == 405
    assert connection.introspection.table_names() == before
    assert not AssessmentRun.objects.exists()
