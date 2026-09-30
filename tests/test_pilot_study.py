import copy
import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from growth.services.assessment_calibration_analysis import PARTICIPANT_EVIDENCE_AXES
from scripts import pilot_study as study

ROOT = Path(__file__).resolve().parents[1]


def observation(cycle=0, task="entry", outcome="completed"):
    return {
        "cycle": cycle,
        "task": task,
        "outcome": outcome,
        "assistance": "none",
        "time_band": "under_2",
        "fit": "not_asked",
        "barrier": "none_reported",
    }


def dataset(count=5):
    return {
        "schema_version": study.VERSION,
        "product_revision": "a" * 40,
        "data_kind": "synthetic",
        "participants": [
            {
                "ref": f"study-{i:032x}",
                "consent": "consented",
                "observations": [observation()],
            }
            for i in range(count)
        ],
    }


def cli(*args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/pilot_study.py"), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("count", [0, 1, 4, 5, 6])
def test_suppression_boundary_and_no_empirical_claim(count):
    report = study.summarize(dataset(count))
    assert report["completed_axes"] == 0
    assert tuple(report["open_axes"]) == PARTICIPANT_EVIDENCE_AXES
    assert report["consented_participants"] == count
    assert report["data_kind"] == "synthetic"
    histogram = report["task_rows"][0]["outcomes"]
    assert histogram["status"] == ("suppressed" if 0 < count < 5 else "available")
    if count >= 5:
        assert histogram["counts"]["completed"] == count
    assert report["observation_status"] == ("observations_present" if count else "no_observations")


def test_whole_breakdown_suppressed_when_complement_would_reveal_rare_cell():
    source = dataset(6)
    source["participants"][0]["observations"][0]["outcome"] = "stopped"
    report = study.summarize(source)
    assert report["task_rows"][0]["outcomes"] == {"status": "suppressed", "counts": None}


def test_withdrawal_excludes_records_without_mutating_input_or_leaking_refs():
    source = dataset(6)
    source["participants"][0]["consent"] = "withdrawn"
    source["participants"][0]["observations"][0]["outcome"] = "unable"
    snapshot = copy.deepcopy(source)
    report = study.summarize(source)
    assert source == snapshot
    assert report["consented_participants"] == 5
    assert report["task_rows"][0]["outcomes"]["counts"]["unable"] == 0
    encoded = json.dumps(report)
    assert all(p["ref"] not in encoded for p in source["participants"])
    assert report == study.summarize(source)


def test_absence_is_not_stopped_and_only_observed_completed_reviews_count_as_return():
    source = dataset()
    for participant in source["participants"]:
        participant["observations"] += [
            observation(1, "weekly_review"),
            observation(2, "weekly_review", "skipped"),
        ]
    report = study.summarize(source)
    absent = next(r for r in report["task_rows"] if (r["cycle"], r["task"]) == (3, "check_in"))
    assert absent["outcomes"]["counts"]["not_observed"] == 5
    assert absent["outcomes"]["counts"]["stopped"] == 0
    assert report["observed_multiple_weekly_reviews"]["counts"]["observed"] == 0
    for participant in source["participants"]:
        participant["observations"][-1]["outcome"] = "completed"
    assert study.summarize(source)["observed_multiple_weekly_reviews"]["counts"]["observed"] == 5


def test_all_withdrawn_is_no_observations():
    source = dataset()
    for participant in source["participants"]:
        participant["consent"] = "withdrawn"
    report = study.summarize(source)
    assert report["consented_participants"] == 0
    assert report["observation_status"] == "no_observations"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.update(private_notes="PRIVATE-MARKER"),
        lambda d: d.update(data_kind="validated"),
        lambda d: d.update(product_revision="main"),
        lambda d: d.update(product_revision="a" * 40 + "\n"),
        lambda d: d["participants"][0].update(ref="study-" + "0" * 32 + "\n"),
        lambda d: d["participants"][0].update(name="PRIVATE-MARKER"),
        lambda d: d["participants"][0].update(consent="pending"),
        lambda d: d["participants"].append(copy.deepcopy(d["participants"][0])),
        lambda d: d["participants"][0]["observations"].append(observation()),
        lambda d: d["participants"][0]["observations"][0].update(cycle=2),
        lambda d: d["participants"][0]["observations"][0].update(cycle=True),
        lambda d: d["participants"][0]["observations"][0].update(fit="fits"),
        lambda d: d["participants"][0]["observations"][0].update(outcome="assumed_success"),
    ],
)
def test_rejects_unconsented_unknown_duplicate_and_impossible_records(mutation):
    source = dataset(1)
    mutation(source)
    with pytest.raises(ValueError) as error:
        study.summarize(source)
    assert "PRIVATE-MARKER" not in str(error.value)


def test_cli_empty_init_private_summary_no_overwrite_or_input_mutation(tmp_path):
    source, target = tmp_path / "study.json", tmp_path / "summary.json"
    assert cli("init", "--revision", "a" * 40, "--output", source).returncode == 0
    original = source.read_bytes()
    assert stat.S_IMODE(source.stat().st_mode) == 0o600
    assert not json.loads(original)["participants"]
    assert cli("init", "--revision", "b" * 40, "--output", source).returncode == 2
    assert cli("summarize", "--input", source, "--output", target).returncode == 2
    assert not target.exists()
    args = ("summarize", "--input", source, "--output", target, "--confirm-sensitive-input")
    assert cli(*args).returncode == 0
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    report = target.read_bytes()
    assert json.loads(report)["observation_status"] == "no_observations"
    assert cli(*args).returncode == 2
    assert target.read_bytes() == report and source.read_bytes() == original


@pytest.mark.parametrize("bad_input", ['{"private":"PRIVATE-MARKER"}', '{"a":1,"a":2}', "{"])
def test_cli_bad_input_does_not_echo_private_values_or_create_output(tmp_path, bad_input):
    source, target = tmp_path / "PRIVATE-PATH.json", tmp_path / "summary.json"
    source.write_text(bad_input)
    result = cli("summarize", "--input", source, "--output", target, "--confirm-sensitive-input")
    assert result.returncode == 2 and not target.exists()
    assert "PRIVATE" not in result.stdout + result.stderr


def test_cli_rejects_oversized_input_and_symlink_output(tmp_path):
    source, target = tmp_path / "study.json", tmp_path / "summary.json"
    source.write_bytes(b" " * (study.MAX_BYTES + 1))
    args = ("summarize", "--input", source, "--output", target, "--confirm-sensitive-input")
    assert cli(*args).returncode == 2 and not target.exists()
    source.write_text(json.dumps(dataset()))
    original = source.read_bytes()
    target.symlink_to(source)
    assert cli(*args).returncode == 2 and source.read_bytes() == original
    assert cli("init", "--revision", "b" * 40, "--output", target).returncode == 2
    assert source.read_bytes() == original
