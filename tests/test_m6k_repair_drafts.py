import copy
import json
import statistics
from pathlib import Path

import yaml

from docs.plans.m6k.recovery import fingerprint
from growth.domain.instructional_content import learner_projection, render_text

ROOT = Path(__file__).resolve().parents[1]


def entry(cid):
    return yaml.safe_load((ROOT / f"docs/authoring/exercises/{cid[:2]}.yaml").read_text())[
        "exercises"
    ][cid]


def test_recovery_draft_receipts_remain_historical_not_current_acceptance():
    # These are receipts of PR 67/70 source repairs, not a ban on future authoring.
    for cid in ("10.01", "10.02", "21.03"):
        folder = ROOT / f"docs/authoring/quality/{cid}"
        record = json.loads((folder / "draft-record.json").read_text())
        if cid == "21.03":
            source = json.loads((folder / "repair-source.json").read_text())
        else:
            source = json.loads((folder / "recovered-repair-source.json").read_text())
        assert record["source_after_sha256"] == fingerprint(source)
        assert record["review_acceptance"] is False


def test_delayed_key_is_independently_recomputed_and_not_in_prompt():
    exercise = entry("10.01")
    guide = exercise["instructional_content"]
    initial = render_text(learner_projection(guide, "10.01"))
    attempt = render_text(learner_projection(guide, "10.01", attempt="delayed-transfer"))
    key = render_text(learner_projection(guide, "10.01", check="delayed-key"))
    assert "2, 5 and 11" not in initial
    assert "2, 5 and 11" in attempt
    values, changed = [2, 5, 11], [2, 5, 17]
    for dataset in (values, changed):
        for label, value in (
            ("mean", statistics.mean(dataset)),
            ("median", statistics.median(dataset)),
            ("range", max(dataset) - min(dataset)),
        ):
            assert f"{label} {value} minutes" in key
    assert statistics.mean(changed) - statistics.mean(values) == 2
    assert statistics.median(changed) - statistics.median(values) == 0
    assert (max(changed) - min(changed)) - (max(values) - min(values)) == 6
    assert "mean 6 minutes" not in attempt and "range 15 minutes" not in attempt
    assert "mean 6 minutes" not in exercise["actions"][2]["instructions"]


def test_three_complete_craft_briefs_and_discriminating_accuracy_check():
    base = ROOT / "docs/authoring/quality/21.03"
    briefs = json.loads((base / "event-briefs.json").read_text())
    desk = json.loads((base / "desk-test.json").read_text())
    guide = entry("21.03")["instructional_content"]
    required = {"name", "date", "time", "location", "contact"}
    by_id = {b["id"]: b for b in briefs}
    assert len(by_id) == 3
    for brief in briefs:
        assert all(brief[field] for field in required)
        key = render_text(learner_projection(guide, "21.03", check=brief["id"] + "-key"))
        assert all(brief[field] in key for field in required)

    def errors(output):
        return sorted(k for k in required if output.get(k) != by_id[output["id"]][k])

    assert all(not errors(output) for output in desk["competent_outputs"])
    assert errors(desk["partial_output"]) == ["contact"]
    assert errors(desk["plausible_incorrect_output"]) == ["date"]


def test_deliberate_practice_scope_moves_metadata_without_changing_actions_or_other_fields():
    before = json.loads((ROOT / "docs/authoring/quality/10.02/before.json").read_text())
    after = copy.deepcopy(
        json.loads((ROOT / "docs/authoring/quality/10.02/recovered-repair-source.json").read_text())
    )
    scope = after.pop("scope_note")
    before.pop("scope_note")
    assert after == before and len(after["actions"]) == 4
    assert not any(
        token in scope.lower() for token in ("measurement", "ratio", "retained", "protocol")
    )
