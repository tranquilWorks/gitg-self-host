"""QA-01 checks for the supplied craft exercise, separate from formal A/B/C reviews."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from growth.domain.instructional_content import learner_projection, render_text

ROOT = Path(__file__).resolve().parents[1]
BASE = "6173b1e15596ac883fd08f9c4c1f4967f3450c6a"
FOLDER = ROOT / "docs/authoring/quality/21.03"
SPEC = importlib.util.spec_from_file_location("qa01_desk", FOLDER / "verify_repair.py")
DESK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DESK)


def guide():
    return yaml.safe_load((ROOT / "docs/authoring/exercises/21.yaml").read_text())["exercises"][
        "21.03"
    ]["instructional_content"]


def test_three_default_outputs_and_counterexamples_are_reproduced():
    result = DESK.run()
    assert len([c for c in result["cases"] if not c["failures"]]) == 3
    assert result["cases"][3]["failures"] == ["contact"]
    assert result["cases"][4]["failures"] == ["date"]
    assert result == json.loads((FOLDER / "dry-run.json").read_text())
    assert result["formal_abc_or_human_acceptance"] is False


@pytest.mark.parametrize("field", ["name", "date", "time", "location", "contact"])
def test_each_required_fact_is_independently_checked(field):
    brief = json.loads((FOLDER / "event-briefs.json").read_text())[0]
    wrong = {**brief, field: "An incorrect supplied value"}
    assert DESK.inspect_notice(brief, DESK.notice(wrong)) == [field]


def test_duplicate_contact_cannot_hide_a_conflicting_route():
    brief = json.loads((FOLDER / "event-briefs.json").read_text())[0]
    output = DESK.notice(brief) + "\nContact: another@events.example"
    assert DESK.inspect_notice(brief, output) == ["duplicate_contact"]


def test_flawed_notice_has_a_separate_check_and_usable_record():
    document = guide()
    prompt = render_text(learner_projection(document, "21.03", attempt="spot-the-defect"))
    checked = render_text(learner_projection(document, "21.03", check="defect-key"))
    assert "Date: 17 May 2027" in prompt and "Date: 16 May 2027" in prompt
    assert "F2 is not met" not in prompt and "F2 is not met" in checked
    assert "Reviewer: [self / freely willing reader]" in prompt
    assert "uninspected" in prompt and "average score" in prompt
    for cid in ("seed-swap", "repair-cafe", "sketch-walk"):
        attempt = render_text(learner_projection(document, "21.03", attempt=cid + "-attempt"))
        assert "Keep the first attempt and its check" in attempt
        assert "200 percent" in attempt and "printed copy" in attempt
        assert "Check your attempt:" not in attempt


def test_repair_keeps_the_scored_source_actions_exact():
    path = "docs/authoring/exercises/21.yaml"
    old = yaml.safe_load(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))[
        "exercises"
    ]["21.03"]
    current = json.loads((FOLDER / "repair-source.json").read_text())
    assert old["actions"] == current["actions"]
    assert (
        old["instructional_content"]["scored"]
        is current["instructional_content"]["scored"]
        is False
    )
