"""Source and finite-model verification, not production or learner acceptance.

Run with the Python standard library:
    python -m unittest discover -s tests -p test_m6k_risk_judgment_inference_sources.py -v
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import math
import unittest
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs/authoring/risk-judgment-inference"
F = json.loads((CONTENT / "fixtures.json").read_text(encoding="utf-8"))
M = json.loads((CONTENT / "cohort.json").read_text(encoding="utf-8"))


def text(cid: str, name: str) -> str:
    return (CONTENT / cid / name).read_text(encoding="utf-8")


def rational(value: int | float | Q) -> Q:
    if isinstance(value, bool) or not isinstance(value, (int, float, Q)):
        raise ValueError("Expected a finite numeric value, not Boolean or text")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite number")
    return Q(str(value))


def mean(values) -> Q:
    values = list(values)
    if not values:
        raise ValueError("No observations")
    return sum((rational(x) for x in values), Q(0)) / len(values)


def median(values) -> Q:
    values = sorted(rational(x) for x in values)
    if not values:
        raise ValueError("No observations")
    n = len(values)
    return values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2


def any_event(p, n: int) -> Q:
    p = rational(p)
    if not 0 <= p <= 1 or type(n) is not int or n < 0:
        raise ValueError("Need probability in [0,1] and nonnegative integer exposures")
    return 1 - (1 - p) ** n


def chosen_method_decision(conditions: dict) -> str:
    """Toy eligibility check only; not a risk assessment or route planner."""
    keys = F["risk"]["conditions"]
    if any(k not in conditions for k in keys):
        raise ValueError("Missing condition")
    for k in keys:
        v = conditions[k]
        if v is not None and type(v) is not bool:
            raise ValueError("Unknown or an actual Boolean is required")
    return "proceed" if all(conditions[k] is True for k in keys) else "hold"


def check_private_example(record: dict) -> None:
    """Validate a synthetic teaching record, not a production evidence schema."""
    fields = set(F["decision"]["initial"])
    if set(record) != fields:
        raise ValueError("Unexpected or missing field in neutral-code example")
    if record["record_code"] != "D1" or record["category"] != "reading":
        raise ValueError("Only the supplied fictional record is supported")
    if record["objective_code"] != "O1" or record["option_codes"] != ["A", "B"]:
        raise ValueError("Unknown objective or option")
    a = record["assumption_codes"]
    if not isinstance(a, list) or len(a) > 3 or len(a) != len(set(a)):
        raise ValueError("At most three unique assumption codes")
    if not set(a) <= {"A1", "A2", "A3"} or record["counterargument_code"] not in a:
        raise ValueError("Counterargument must reference an allowed assumption")
    if record["selected_code"] not in record["option_codes"]:
        raise ValueError("Selected option is not live")
    if record["prediction"] not in {"completed", "partly completed", "not completed"}:
        raise ValueError("Unknown prediction status")
    if record["confidence"] not in {"low", "moderate", "high"}:
        raise ValueError("Unknown confidence band")
    days = [record[k] for k in ("record_day", "choice_day", "review_day")]
    if any(type(x) is not int for x in days) or not 0 <= days[0] <= days[1] < days[2]:
        raise ValueError("Invalid example chronology")
    if days[2] - days[1] > 30 or record["route"] != "simulation":
        raise ValueError("Review outside 30 days or false live-evidence claim")


def fingerprint(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def ols(xs, ys) -> tuple[Q, Q]:
    xs, ys = list(xs), list(ys)
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("At least two complete paired observations required")
    xs, ys = [rational(x) for x in xs], [rational(y) for y in ys]
    mx, my = mean(xs), mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        raise ValueError("Slope is unidentified when x has no variation")
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / denom
    return my - b * mx, b


def flag_table(p: dict) -> dict:
    n, cases, tp, fp = (p[k] for k in ("n", "cases", "tp", "fp"))
    if any(type(v) is not int for v in (n, cases, tp, fp)):
        raise ValueError("Integer counts required")
    if not (n > 0 and 0 <= tp <= cases <= n and 0 <= fp <= n - cases):
        raise ValueError("Impossible counts")
    return {"tp": tp, "fn": cases - tp, "fp": fp, "tn": n - cases - fp}


def ratio(n: int, d: int) -> Q | None:
    return Q(n, d) if d else None


def check_run(row: dict) -> None:
    n = F["science"]["assigned_per_run"]
    counts = [row[k] for k in ("correct", "incorrect", "unplaced")]
    if any(type(v) is not int or v < 0 for v in counts) or sum(counts) != n:
        raise ValueError("Assigned slips must all be accounted for")
    if row["layout"] not in {"L", "U"} or row["status"] not in {"complete", "interrupted"}:
        raise ValueError("Unknown layout or run status")
    if row["status"] == "complete":
        if row["unplaced"] or row["seconds"] is None:
            raise ValueError("Complete status requires all slips placed and a duration")
        if not 0 < rational(row["seconds"]) <= F["science"]["max_seconds"]:
            raise ValueError("Completed-run duration outside the protocol")
    elif row["seconds"] is not None:
        raise ValueError("Interrupted row has no completed-run duration in this fixture")


def pilot_summary(rows) -> dict:
    for row in rows:
        check_run(row)
    result = {}
    for layout in ("L", "U"):
        group = [r for r in rows if r["layout"] == layout]
        complete = [r for r in group if r["status"] == "complete"]
        result[layout] = {
            "mean_seconds": mean(r["seconds"] for r in complete) if complete else None,
            "duration_n": len(complete),
            "correct": sum(r["correct"] for r in group),
            "assigned": len(group) * F["science"]["assigned_per_run"],
        }
    return result


def pilot_criterion(summary) -> bool | None:
    l, u = summary["L"], summary["U"]
    if l["duration_n"] != 2 or u["duration_n"] != 2:
        return None  # Planned complete four-run comparison not available.
    return (
        u["mean_seconds"] - l["mean_seconds"] >= F["science"]["time_threshold"]
        and Q(l["correct"], l["assigned"]) >= Q(u["correct"], u["assigned"])
    )


def consistent(world) -> bool:
    if len(world) != len(F["causal"]["observed"]):
        return False
    return all(
        len(pair) == 2
        and all(type(v) is int and v in (0, 1) for v in pair)
        and pair[row["t"]] == row["y"]
        for pair, row in zip(world, F["causal"]["observed"], strict=True)
    )


def ate(world) -> Q:
    if not consistent(world):
        raise ValueError("World changes an observed value or uses invalid binary values")
    return mean(pair[1] - pair[0] for pair in world)


def possible_worlds():
    for missing in itertools.product((0, 1), repeat=4):
        world = []
        for row, other in zip(F["causal"]["observed"], missing, strict=True):
            pair = [None, None]
            pair[row["t"]] = row["y"]
            pair[1 - row["t"]] = other
            world.append(pair)
        yield world


class CohortStructure(unittest.TestCase):
    def test_exact_six_ids_and_separate_deliverables(self):
        self.assertEqual([x["id"] for x in M["competencies"]], [f"09.{i}" for i in range(10, 16)])
        self.assertEqual(len({x["deliverable"] for x in M["competencies"]}), 6)

    def test_no_coverage_or_review_promotion(self):
        self.assertEqual((M["runtime_tailored"], M["runtime_pending"]), (108, 275))
        self.assertEqual(M["protocols"], 383)
        self.assertEqual(M["actions"], 1151)
        self.assertFalse(M["runtime_changes"])
        self.assertEqual(M["formal_reviews_accepted"], 0)

    def test_eighteen_individual_guide_check_files(self):
        paths = [CONTENT / c["id"] / n for c in M["competencies"] for n in
                 ("learner-guide.md", "check-prompts.md", "check-answers.md")]
        self.assertEqual(len(paths), 18)
        for p in paths:
            self.assertTrue(p.is_file(), p)
            self.assertTrue(p.read_text().startswith("# " + p.parent.name))

    def test_exact_two_later_packets(self):
        packets = [(c["id"], c["later_packet"]) for c in M["competencies"] if c["later_packet"]]
        self.assertEqual(packets, [("09.12", "outcome-packet.md"), ("09.14", "pilot-results.md")])
        for cid, name in packets:
            self.assertTrue((CONTENT / cid / name).is_file())

    def test_each_guide_has_complete_actions_and_outcome_boundaries(self):
        for c in M["competencies"]:
            t = text(c["id"], "learner-guide.md")
            for token in ("Canonical scope", "Deliverable", "Action 1", "Action 2", "Action 3",
                          "Accessibility", "Supportive", "Mixed", "Contradictory", "Inconclusive",
                          "Final review"):
                with self.subTest(cid=c["id"], token=token):
                    self.assertIn(token, t)

    def test_exact_twelve_fresh_checks_and_keys(self):
        for c in M["competencies"]:
            for n in ("check-prompts.md", "check-answers.md"):
                t = text(c["id"], n)
                self.assertEqual(t.count("## Check A"), 1)
                self.assertEqual(t.count("## Check B"), 1)

    def test_answer_files_not_appended_to_guides(self):
        for c in M["competencies"]:
            self.assertNotIn(text(c["id"], "check-answers.md"), text(c["id"], "learner-guide.md"))

    def test_later_data_not_in_initial_guide(self):
        self.assertNotIn("two separate 15-minute", text("09.12", "learner-guide.md"))
        self.assertNotIn("| 1 | 1 | first | L | X | 40", text("09.14", "learner-guide.md"))

    def test_every_canonical_element_is_individually_mapped(self):
        scope = (CONTENT / "SCOPE-MAP.md").read_text().lower()
        for c in M["competencies"]:
            section = scope.split("## " + c["id"])[1].split("\n## ")[0]
            for term in c["canonical_elements"]:
                self.assertIn(term.lower(), section, (c["id"], term))

    def test_sources_and_privacy_boundaries_exist(self):
        s = (CONTENT / "SOURCES.md").read_text()
        for n in range(1, 9):
            self.assertIn(f"## R{n} ", s)
        self.assertIn("not production evidence", (CONTENT / "SCOPE-MAP.md").read_text())

    def test_utf8_clean_no_placeholder_or_trailing_whitespace(self):
        for p in CONTENT.rglob("*.md"):
            t = p.read_text(encoding="utf-8")
            self.assertNotIn("\0", t)
            self.assertNotIn("TODO", t)
            for line in t.splitlines():
                self.assertEqual(line, line.rstrip(), p)


class RiskCases(unittest.TestCase):
    def test_exact_three_events(self):
        for event in F["risk"]["events"]:
            self.assertEqual(chosen_method_decision(event), event["expected"])

    def test_exhaustive_known_conditions_only_all_true_proceeds(self):
        keys = F["risk"]["conditions"]
        results = []
        for values in itertools.product((False, True), repeat=5):
            result = chosen_method_decision(dict(zip(keys, values, strict=True)))
            self.assertEqual(result == "proceed", all(values))
            results.append(result)
        self.assertEqual(results.count("proceed"), 1)

    def test_each_unknown_fails_closed(self):
        for k in F["risk"]["conditions"]:
            case = dict.fromkeys(F["risk"]["conditions"], True)
            case[k] = None
            self.assertEqual(chosen_method_decision(case), "hold")

    def test_malformed_condition_not_truthiness(self):
        case = dict.fromkeys(F["risk"]["conditions"], True)
        for bad in (1, "true", [], {}):
            case["permission"] = bad
            with self.assertRaises(ValueError):
                chosen_method_decision(case)
        with self.assertRaises(ValueError):
            chosen_method_decision({})

    def test_three_passes_exact(self):
        self.assertEqual(any_event(Q(1, 10), 3), Q(271, 1000))

    def test_six_passes_exact(self):
        self.assertEqual(any_event(Q(1, 10), 6), Q(468559, 1000000))

    def test_probability_boundaries_and_invalid_input(self):
        self.assertEqual(any_event(0, 6), 0)
        self.assertEqual(any_event(1, 6), 1)
        self.assertEqual(any_event(Q(1, 10), 0), 0)
        for p, n in ((-1, 2), (2, 2), (0.1, -1), (0.1, True), (float("nan"), 2)):
            with self.assertRaises(ValueError):
                any_event(p, n)

    def test_independence_permission_and_no_field_claim_visible(self):
        t = text("09.10", "learner-guide.md")
        for phrase in ("independent crossings", "not a probability of injury", "no permission",
                       "Do not stage a physical obstruction"):
            self.assertIn(phrase, t)


class ContextCases(unittest.TestCase):
    def test_six_distinct_case_cards_exist(self):
        guide = text("09.11", "learner-guide.md")
        for label in F["wisdom"]["cases"]:
            self.assertIn("| " + label + " —", guide)

    def test_cultural_preference_is_stated_not_inferred(self):
        t = text("09.11", "learner-guide.md")
        self.assertIn("rather than assigning one from a group label", t)
        self.assertIn("has not asked you to disguise uncertainty", t)

    def test_limited_role_and_unsafe_channel_do_not_grant_authority(self):
        t = text("09.11", "learner-guide.md")
        self.assertIn("cannot approve a new opening time", t)
        self.assertIn("must not use the unsafe channel", t)

    def test_fresh_checks_include_no_safe_substitute_case(self):
        self.assertIn("no safe substitute is currently established", text("09.11", "check-prompts.md"))
        self.assertIn("does not justify unsafe contact", text("09.11", "check-answers.md"))

    def test_no_machine_wisdom_acceptance(self):
        self.assertFalse(F["wisdom"]["machine_acceptance"])
        self.assertIn("more than one response", text("09.11", "learner-guide.md"))
        self.assertIn("same-relevant-facts", text("09.11", "learner-guide.md"))


class DecisionCases(unittest.TestCase):
    def test_supplied_neutral_record_is_valid(self):
        check_private_example(F["decision"]["initial"])

    def test_record_is_preserved_when_outcome_appended(self):
        original = copy.deepcopy(F["decision"]["initial"])
        before = fingerprint(original)
        layers = [original, copy.deepcopy(F["decision"]["outcome"])]
        self.assertEqual(fingerprint(layers[0]), before)
        self.assertEqual(layers[0]["selected_code"], "A")
        self.assertEqual(layers[1]["fallback_code"], "B")
        self.assertEqual(layers[0]["prediction"], "completed")
        self.assertEqual(layers[1]["outcome"], "partly completed")

    def test_identifying_or_free_text_fields_rejected(self):
        for field in ("name", "private_quote", "narrative", "email", "medical_details"):
            r = copy.deepcopy(F["decision"]["initial"])
            r[field] = "not allowed"
            with self.assertRaises(ValueError):
                check_private_example(r)

    def test_private_content_cannot_replace_neutral_codes(self):
        for field in ("record_code", "category", "objective_code", "counterargument_code", "route"):
            r = copy.deepcopy(F["decision"]["initial"])
            r[field] = "private narrative instead of an allowed code"
            with self.assertRaises(ValueError):
                check_private_example(r)

    def test_three_unique_assumptions_and_counterargument_required(self):
        for assumptions in (["A1"] * 3, ["A1", "A2", "A3", "A4"], ["A1"]):
            r = copy.deepcopy(F["decision"]["initial"])
            r["assumption_codes"] = assumptions
            with self.assertRaises(ValueError):
                check_private_example(r)

    def test_chronology_and_review_window(self):
        for updates in ({"record_day": 2}, {"review_day": 31}, {"review_day": 0},
                        {"choice_day": True}, {"record_day": -1}):
            r = copy.deepcopy(F["decision"]["initial"])
            r.update(updates)
            with self.assertRaises(ValueError):
                check_private_example(r)
        r = copy.deepcopy(F["decision"]["initial"])
        r["review_day"] = 30
        check_private_example(r)

    def test_unknown_option_and_prediction_rejected(self):
        for field, value in (("selected_code", "C"), ("prediction", "mastered"),
                             ("confidence", "certain")):
            r = copy.deepcopy(F["decision"]["initial"])
            r[field] = value
            with self.assertRaises(ValueError):
                check_private_example(r)

    def test_notice_is_post_choice_not_ignored_pre_choice(self):
        self.assertGreater(F["decision"]["notice_available_day"], F["decision"]["initial"]["choice_day"])
        self.assertIn("did not exist at Day 0", text("09.12", "outcome-packet.md"))

    def test_hash_changes_but_no_independent_timestamp_claim(self):
        r = copy.deepcopy(F["decision"]["initial"])
        before = fingerprint(r)
        r["confidence"] = "high"
        self.assertNotEqual(before, fingerprint(r))
        self.assertIn("independent timestamp", text("09.12", "learner-guide.md"))
        self.assertFalse(F["decision"]["production_evidence"])

    def test_no_retroactive_scheduling_or_production_extension(self):
        t = text("09.12", "learner-guide.md")
        for phrase in ("does not create a reminder", "existing reviewed observation fields",
                       "not production observations"):
            self.assertIn(phrase, t)


class StatisticsCases(unittest.TestCase):
    def test_default_distribution_and_absolute_effect(self):
        a, b = F["stats"]["groups"].values()
        self.assertEqual((mean(a), median(a), max(a) - min(a)), (10, 10, 4))
        self.assertEqual((mean(b), median(b), max(b) - min(b)), (8, 8, 4))
        self.assertEqual(mean(b) - mean(a), -2)
        self.assertEqual((mean(a) - mean(b)) / mean(a), Q(1, 5))
        self.assertEqual(set(a) & set(b), {8, 9, 10})

    def test_all_six_samples_and_mean(self):
        means = [mean(pair) for pair in itertools.combinations(F["stats"]["sample_population"], 2)]
        self.assertEqual(means, [3, 4, 5, 5, 6, 7])
        self.assertEqual(mean(means), 5)

    def test_fresh_sampling_enumeration(self):
        means = [mean(pair) for pair in itertools.combinations(F["stats"]["fresh_population"], 2)]
        self.assertEqual(means, [2, Q(9, 2), Q(11, 2)])
        self.assertEqual(mean(means), 4)

    def test_default_ols_coefficients_predictions_residuals(self):
        data = F["stats"]["regression"]
        a, b = ols(data["x"], data["y"])
        self.assertEqual((a, b), (Q(3, 2), Q(7, 5)))
        self.assertEqual(a + b * 2, Q(43, 10))
        self.assertEqual(a + b * 5, Q(17, 2))
        residuals = [rational(y) - (a + b * x) for x, y in zip(data["x"], data["y"], strict=True)]
        self.assertEqual(residuals, [Q(1, 10), Q(7, 10), Q(-17, 10), Q(9, 10)])
        self.assertEqual(sum(r * r for r in residuals), Q(21, 5))

    def test_fresh_ols_coefficients(self):
        data = F["stats"]["fresh_regression"]
        a, b = ols(data["x"], data["y"])
        self.assertEqual((a, b), (Q(7, 10), Q(6, 5)))
        self.assertEqual(a + 2 * b, Q(31, 10))
        self.assertGreater(6, max(data["x"]))

    def test_ols_input_guards(self):
        for xs, ys in (([], []), ([1], [2]), ([1, 1], [2, 3]), ([1, 2], [1]),
                       ([1, float("nan")], [1, 2]), ([1, 2], [True, 2]), (["1", 2], [1, 2])):
            with self.assertRaises(ValueError):
                ols(xs, ys)

    def test_center_input_guards_and_even_median(self):
        self.assertEqual(median([2, 4, 6, 8]), 5)
        for func in (mean, median):
            for values in ([], [True, 2], [float("inf"), 2]):
                with self.assertRaises(ValueError):
                    func(values)

    def test_selected_extreme_has_nonextreme_expected_repeat(self):
        model = F["stats"]["noise"]
        trials = [(model["truth"] + e1, model["truth"] + e2)
                  for e1, e2 in itertools.product(model["errors"], repeat=2)]
        selected = [second for first, second in trials if first == 12]
        self.assertEqual(selected, [8, 10, 12])
        self.assertEqual(mean(selected), 10)
        self.assertIn(12, selected)  # Not a guarantee of decline for each object.

    def test_default_flag_table_and_different_denominators(self):
        t = flag_table(F["stats"]["flags"])
        self.assertEqual(t, {"tp": 8, "fn": 2, "fp": 10, "tn": 80})
        self.assertEqual(Q(t["tp"], t["tp"] + t["fn"]), Q(4, 5))
        self.assertEqual(Q(t["tp"], t["tp"] + t["fp"]), Q(4, 9))
        self.assertEqual(Q(t["fp"], t["fp"] + t["tn"]), Q(1, 9))

    def test_fresh_flag_table(self):
        t = flag_table(F["stats"]["fresh_flags"])
        self.assertEqual(t, {"tp": 16, "fn": 4, "fp": 98, "tn": 882})
        self.assertEqual(Q(t["tp"], t["tp"] + t["fp"]), Q(8, 57))
        self.assertEqual(Q(t["fp"], t["fp"] + t["tn"]), Q(1, 10))

    def test_matched_rates_isolate_toy_base_rate_difference(self):
        a = flag_table(F["stats"]["matched_flags"])
        b = flag_table(F["stats"]["fresh_flags"])
        self.assertEqual(Q(a["tp"], a["tp"] + a["fn"]), Q(b["tp"], b["tp"] + b["fn"]))
        self.assertEqual(Q(a["fp"], a["fp"] + a["tn"]), Q(b["fp"], b["fp"] + b["tn"]))
        self.assertGreater(Q(a["tp"], a["tp"] + a["fp"]), Q(b["tp"], b["tp"] + b["fp"]))
        self.assertEqual(Q(a["tp"], a["tp"] + a["fp"]), Q(8, 17))

    def test_flag_impossible_counts_and_undefined_ratio(self):
        for update in ({"tp": 11}, {"fp": 91}, {"cases": -1}, {"n": 0}, {"tp": True}):
            p = dict(F["stats"]["flags"], **update)
            with self.assertRaises(ValueError):
                flag_table(p)
        self.assertIsNone(ratio(0, 0))

    def test_outlier_changes_mean_not_typical_order(self):
        p, q = F["stats"]["outlier"].values()
        self.assertEqual((mean(p), median(p), max(p) - min(p)), (8, 4, 20))
        self.assertEqual((mean(q), median(q), max(q) - min(q)), (5, 5, 0))
        self.assertLess(mean(q), mean(p))
        self.assertGreater(median(q), median(p))

    def test_visible_datasets_match_fixtures(self):
        guide, prompt = text("09.13", "learner-guide.md"), text("09.13", "check-prompts.md")
        for values in F["stats"]["groups"].values():
            self.assertIn(", ".join(map(str, values)), guide)
        for values in F["stats"]["outlier"].values():
            self.assertIn(", ".join(map(str, values)), prompt)
        for i, (x, y) in enumerate(zip(F["stats"]["regression"]["x"], F["stats"]["regression"]["y"], strict=True), 1):
            self.assertIn(f"| R{i} | {x} | {y} |", guide)
        self.assertIn("Do not assume those two false-positive rates are identical", prompt)


class ExperimentCases(unittest.TestCase):
    def test_all_four_decks_have_ten_slips_two_each(self):
        for deck in F["science"]["decks"].values():
            self.assertEqual(len(deck), 10)
            self.assertEqual(Counter(deck), Counter({x: 2 for x in "ABCDE"}))

    def test_decks_and_layouts_match_visible_materials(self):
        guide = text("09.14", "learner-guide.md")
        for key, deck in F["science"]["decks"].items():
            self.assertIn(f"| {key} | {', '.join(deck)} |", guide)
        for layout in F["science"]["layouts"].values():
            self.assertEqual(set(layout), set("ABCDE"))
        self.assertIn("C, A, E, B, D", guide)

    def test_each_layout_appears_once_in_each_position(self):
        counts = Counter((r["layout"], r["position"]) for r in F["science"]["runs"])
        self.assertEqual(counts, Counter({("L", "first"): 1, ("L", "second"): 1,
                                         ("U", "first"): 1, ("U", "second"): 1}))

    def test_default_pilot_time_and_accuracy(self):
        s = pilot_summary(F["science"]["runs"])
        self.assertEqual(s["L"]["mean_seconds"], Q(73, 2))
        self.assertEqual(s["U"]["mean_seconds"], 38)
        self.assertEqual((s["L"]["correct"], s["U"]["correct"]), (20, 19))
        self.assertFalse(pilot_criterion(s))

    def test_position_contrast_and_opposing_block_signs(self):
        rows = F["science"]["runs"]
        first = mean(r["seconds"] for r in rows if r["position"] == "first")
        second = mean(r["seconds"] for r in rows if r["position"] == "second")
        self.assertEqual((first, second, first - second), (41, Q(67, 2), Q(15, 2)))
        differences = []
        for block in (1, 2):
            d = {r["layout"]: r["seconds"] for r in rows if r["block"] == block}
            differences.append(d["U"] - d["L"])
        self.assertEqual(differences, [-6, 9])

    def test_fresh_pilot_fails_both_conditions(self):
        s = pilot_summary(F["science"]["fresh_runs"])
        self.assertEqual((s["L"]["mean_seconds"], s["U"]["mean_seconds"]), (19, 23))
        self.assertEqual((s["L"]["correct"], s["U"]["correct"]), (19, 20))
        self.assertFalse(pilot_criterion(s))

    def test_threshold_is_inclusive_and_accuracy_conjunctive(self):
        s = pilot_summary(F["science"]["fresh_runs"])
        s["L"]["mean_seconds"] = 18
        s["L"]["correct"] = 20
        self.assertTrue(pilot_criterion(s))
        s["L"]["correct"] = 19
        self.assertFalse(pilot_criterion(s))

    def test_interruption_keeps_assignments_not_zero_duration(self):
        rows = copy.deepcopy(F["science"]["fresh_runs"])
        rows[1].update(status="interrupted", seconds=None, correct=6, incorrect=0, unplaced=4)
        s = pilot_summary(rows)
        self.assertEqual(s["U"]["assigned"], 20)
        self.assertEqual(s["U"]["correct"], 16)
        self.assertEqual(s["U"]["duration_n"], 1)
        self.assertEqual(s["U"]["mean_seconds"], 22)
        self.assertIsNone(pilot_criterion(s))

    def test_bad_count_status_and_duration_rejected(self):
        for updates in ({"correct": 11}, {"incorrect": -1}, {"correct": True},
                        {"seconds": None}, {"seconds": 0}, {"seconds": 121},
                        {"correct": 9, "unplaced": 1}, {"status": "interrupted"}):
            row = dict(F["science"]["runs"][0], **updates)
            with self.assertRaises(ValueError):
                check_run(row)

    def test_visible_main_and_fresh_result_rows_match(self):
        later, prompt = text("09.14", "pilot-results.md"), text("09.14", "check-prompts.md")
        for r in F["science"]["runs"]:
            self.assertIn("| " + " | ".join(str(r[k]) for k in
                          ("run", "block", "position", "layout", "deck", "seconds", "correct", "incorrect", "unplaced", "status")) + " |", later)
        for r in F["science"]["fresh_runs"]:
            self.assertIn("| " + " | ".join(str(r[k]) for k in
                          ("run", "layout", "seconds", "correct", "incorrect", "unplaced", "status")) + " |", prompt)

    def test_units_replication_and_non_timed_route_limits_visible(self):
        guide = text("09.14", "learner-guide.md")
        for phrase in ("not forty independent participants", "new observations",
                       "not establish the same speed claim", "No live"):
            if phrase == "No live":
                self.assertIn("no live task", text("09.14", "pilot-results.md").lower())
            else:
                self.assertIn(phrase, guide)


class CausalCases(unittest.TestCase):
    def test_stratum_rates_and_differences(self):
        rates = [(Q(r["t_success"], r["t_total"]), Q(r["c_success"], r["c_total"]))
                 for r in F["causal"]["strata"]]
        self.assertEqual(rates, [(Q(9, 10), Q(4, 5)), (Q(3, 10), Q(1, 5))])
        self.assertTrue(all(t - c == Q(1, 10) for t, c in rates))

    def test_crude_mixture_reverses_the_sign(self):
        rows = F["causal"]["strata"]
        t = Q(sum(r["t_success"] for r in rows), sum(r["t_total"] for r in rows))
        c = Q(sum(r["c_success"] for r in rows), sum(r["c_total"] for r in rows))
        self.assertEqual((t, c), (Q(9, 22), Q(38, 55)))
        self.assertEqual(t - c, Q(-31, 110))

    def test_equal_weight_standardization_has_explicit_target(self):
        rows = F["causal"]["strata"]
        t = mean(Q(r["t_success"], r["t_total"]) for r in rows)
        c = mean(Q(r["c_success"], r["c_total"]) for r in rows)
        self.assertEqual((t, c, t - c), (Q(3, 5), Q(1, 2), Q(1, 10)))

    def test_same_observed_zero_contrast(self):
        rows = F["causal"]["observed"]
        self.assertEqual(mean(r["y"] for r in rows if r["t"] == 1), Q(1, 2))
        self.assertEqual(mean(r["y"] for r in rows if r["t"] == 0), Q(1, 2))

    def test_positive_and_negative_worlds_preserve_all_observations(self):
        self.assertEqual(ate(F["causal"]["positive_world"]), Q(1, 2))
        self.assertEqual(ate(F["causal"]["negative_world"]), Q(-1, 2))

    def test_all_sixteen_worlds_and_effect_distribution(self):
        worlds = list(possible_worlds())
        self.assertEqual(len(worlds), 16)
        self.assertTrue(all(consistent(w) for w in worlds))
        self.assertEqual(Counter(ate(w) for w in worlds),
                         Counter({Q(-1, 2): 1, Q(-1, 4): 4, Q(0): 6, Q(1, 4): 4, Q(1, 2): 1}))

    def test_changing_observed_or_nonbinary_values_is_rejected(self):
        world = copy.deepcopy(F["causal"]["positive_world"])
        world[0][1] = 0
        with self.assertRaises(ValueError):
            ate(world)
        for value in (2, True, None):
            world = copy.deepcopy(F["causal"]["positive_world"])
            world[0][0] = value
            with self.assertRaises(ValueError):
                ate(world)

    def test_offer_assignment_contrast(self):
        a, b = F["causal"]["offer"].values()
        self.assertEqual(Q(a["completed"], a["assigned"]) - Q(b["completed"], b["assigned"]), Q(1, 10))
        self.assertEqual(Q(a["attended"], a["assigned"]) - Q(b["attended"], b["assigned"]), Q(2, 5))

    def test_attender_outcomes_not_identified_by_marginal_totals(self):
        possibilities = []
        for row in F["causal"]["offer"].values():
            low = max(0, row["completed"] - (row["assigned"] - row["attended"]))
            high = min(row["completed"], row["attended"])
            possibilities.append((low, high))
            self.assertLess(low, high)
        self.assertEqual(possibilities, [(12, 24), (0, 8)])

    def test_pre_and_post_variables_have_distinct_roles(self):
        roles = F["causal"]["temporal_roles"]
        self.assertEqual((roles["P"], roles["R"], roles["M"]), ("pre", "pre", "post"))
        self.assertIn("Holding post-attendance practice fixed", text("09.15", "learner-guide.md"))

    def test_visible_stratum_counts_and_fresh_totals_match(self):
        guide = text("09.15", "learner-guide.md")
        for r in F["causal"]["strata"]:
            self.assertIn(f"| {r['prior']} | {r['t_success']} / {r['t_total']} | {r['c_success']} / {r['c_total']} |", guide)
        prompt = text("09.15", "check-prompts.md")
        self.assertIn("24 attend and 28 complete", prompt)
        self.assertIn("8 access similar support elsewhere and 24 complete", prompt)

    def test_keys_keep_intervention_and_authority_limits(self):
        t = text("09.15", "check-answers.md")
        self.assertIn("additional assumptions not supplied", t)
        self.assertIn("not an automatically precise population effect", t)
        self.assertIn("different causal", text("09.15", "learner-guide.md"))


if __name__ == "__main__":
    unittest.main()
