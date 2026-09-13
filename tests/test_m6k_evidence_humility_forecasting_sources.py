"""Standalone instructional checks, not application or learner validation.

Run: python -m unittest discover -s tests -p '*sources.py' -v
No Django, network, production scoring, or participant data is used.
"""

from __future__ import annotations

import copy
import itertools
import json
import math
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs/authoring/evidence-humility-forecasting"
DATA = json.loads((CONTENT / "fixtures.json").read_text(encoding="utf-8"))


def response_bounds(selected: int, responded: int, yes: int):
    """Bounds from missing binary responses, not population confidence intervals."""
    if any(type(v) is not int for v in (selected, responded, yes)):
        raise ValueError("Counts must be integers, not Boolean or fractional values")
    if not 0 <= yes <= responded <= selected or selected == 0:
        raise ValueError("Require 0 <= yes <= responded <= selected and selected > 0")
    return Fraction(yes, selected), Fraction(yes + selected - responded, selected)


def probability(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
        raise ValueError("A numeric probability is required")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Probability must be finite and between zero and one")
    return Fraction(str(value))


def brier(probabilities, outcomes):
    if not probabilities or len(probabilities) != len(outcomes):
        raise ValueError("Nonempty equally sized probability/outcome records required")
    ps = [probability(p) for p in probabilities]
    if any(type(y) is not int or y not in (0, 1) for y in outcomes):
        raise ValueError("Resolve outcomes to integer 0 or 1 before scoring")
    return sum((p - y) ** 2 for p, y in zip(ps, outcomes, strict=True)) / len(ps)


def resolve(delay, *, cancelled=False, confirmed_no_start=False):
    """Apply this packet's fixed rule only; unknown is not a failed event."""
    if cancelled:
        return "void", None
    if delay is None:
        return ("scored", 0) if confirmed_no_start else ("unresolved", None)
    if isinstance(delay, bool) or not isinstance(delay, (int, float)):
        raise ValueError("Delay must be a finite number or missing")
    if not math.isfinite(delay):
        raise ValueError("Delay must be finite")
    return "scored", int(delay <= DATA["forecasting"]["threshold_minutes"])


def net_saving(p, cost, benefit):
    if cost < 0 or benefit <= 0:
        raise ValueError("Require nonnegative cost and positive avoided disruption")
    return probability(p) * benefit - cost


def text(cid, filename="learner-guide.md"):
    return (CONTENT / cid / filename).read_text(encoding="utf-8")


class Structure(unittest.TestCase):
    def test_three_next_ids_not_prior_cohort(self):
        self.assertEqual(DATA["cohort"], ["09.04", "09.05", "09.06"])

    def test_runtime_count_unchanged(self):
        b = DATA["runtime_baseline"]
        self.assertEqual((b["tailored"], b["pending"]), (108, 275))
        self.assertEqual(b["tailored"] + b["pending"], b["protocols"])
        self.assertEqual(b["actions"], 1151)
        self.assertEqual(DATA["stage"], "source_candidates_not_runtime_selected")

    def test_every_guide_has_individual_practice_and_routes(self):
        for cid in DATA["cohort"]:
            with self.subTest(cid=cid):
                guide = text(cid)
                self.assertTrue(guide.startswith("# " + cid))
                for marker in (
                    "Canonical scope", "Action 1", "Action 2", "Action 3",
                    "Accessibility", "Supportive", "Mixed", "Contradictory",
                    "Inconclusive", "Final review", "check-prompts.md", "check-answers.md",
                ):
                    self.assertIn(marker, guide)
                self.assertNotIn("TODO", guide)

    def test_each_has_two_fresh_checks_and_separate_answers(self):
        for cid in DATA["cohort"]:
            with self.subTest(cid=cid):
                prompts, answers = text(cid, "check-prompts.md"), text(cid, "check-answers.md")
                self.assertIn("## Check A", prompts)
                self.assertIn("## Check B", prompts)
                self.assertNotIn(answers, prompts)
                self.assertNotIn(answers, text(cid))

    def test_new_evidence_and_outcomes_are_separate_files(self):
        self.assertNotIn(text("09.05", "evidence-update.md"), text("09.05"))
        self.assertNotIn(text("09.06", "outcomes.md"), text("09.06"))
        self.assertIn("evidence-update.md", text("09.05"))
        self.assertIn("outcomes.md", text("09.06"))

    def test_no_future_outcome_sequence_in_forecast_guide(self):
        guide = text("09.06")
        self.assertNotIn("F1, F2, F3 resolve to 1, 0, 1", guide)
        self.assertNotIn("| F2 | 11", guide)

    def test_scope_map_covers_every_canonical_element(self):
        scope = (CONTENT / "SCOPE-MAP.md").read_text(encoding="utf-8").lower()
        for word in (
            "expertise", "incentives", "methodology", "sample quality", "replication",
            "uncertainty", "competing explanations", "confidence", "assumptions",
            "unknowns", "limitations", "change a belief", "ranges", "likelihoods",
            "base rates", "scenarios", "sensitivity", "expected value", "calibration",
        ):
            self.assertIn(word, scope)

    def test_text_cleanliness(self):
        for path in CONTENT.rglob("*.md"):
            data = path.read_text(encoding="utf-8")
            self.assertNotIn("\0", data)
            for line in data.splitlines():
                self.assertEqual(line, line.rstrip(), str(path))


class SourceEvaluation(unittest.TestCase):
    def test_main_respondent_ratio_is_two(self):
        new, old = DATA["source_evaluation"]["main"]
        self.assertEqual(Fraction(new["yes"], new["responded"]), 1)
        self.assertEqual(Fraction(old["yes"], old["responded"]), Fraction(1, 2))
        self.assertEqual(
            Fraction(new["yes"], new["responded"]) / Fraction(old["yes"], old["responded"]), 2
        )

    def test_main_missing_bounds(self):
        self.assertEqual(response_bounds(12, 10, 10), (Fraction(5, 6), Fraction(1)))

    def test_fresh_missing_bounds(self):
        self.assertEqual(response_bounds(12, 6, 6), (Fraction(1, 2), Fraction(1)))

    def test_bounds_cover_every_possible_missing_response_assignment(self):
        for selected, responded, yes in ((12, 10, 10), (12, 6, 6)):
            lo, hi = response_bounds(selected, responded, yes)
            possible = [
                Fraction(yes + sum(values), selected)
                for values in itertools.product((0, 1), repeat=selected - responded)
            ]
            self.assertEqual((min(possible), max(possible)), (lo, hi))

    def test_invalid_count_inputs_rejected(self):
        for values in ((0, 0, 0), (4, 5, 3), (4, 4, 5), (4, 3, -1), (4, True, 1), (4, 2.5, 1)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                response_bounds(*values)

    def test_republication_is_one_dataset(self):
        for key in ("main_dataset_ids", "fresh_a_dataset_ids"):
            self.assertEqual(len(set(DATA["source_evaluation"][key])), 1)

    def test_independent_new_data_not_collapsed_with_republication(self):
        self.assertEqual(len(set(DATA["source_evaluation"]["fresh_b_dataset_ids"])), 2)

    def test_fresh_b_risk_differences(self):
        studies = DATA["source_evaluation"]["fresh_b"]
        observed = {
            name: Fraction(*groups[0]) - Fraction(*groups[1])
            for name, groups in studies.items()
        }
        self.assertEqual(observed, {"Q": Fraction(1, 5), "R": Fraction(1, 10)})

    def test_main_table_matches_fixture(self):
        guide = text("09.04")
        for row in DATA["source_evaluation"]["main"]:
            line = (
                f"| {row['label']} | {row['selected']} | {row['responded']} | "
                f"{row['yes']} | {row['selected'] - row['responded']} |"
            )
            self.assertIn(line, guide)

    def test_measure_and_replication_limits_are_explicit(self):
        guide = text("09.04")
        self.assertIn("did you feel able to contribute?", guide)
        self.assertIn("not a count of actual contributions", guide)
        self.assertIn("not a new intervention study", guide)
        self.assertIn("not confidence intervals", guide)


class Humility(unittest.TestCase):
    def test_initial_observation_does_not_survey_every_room(self):
        observations = DATA["humility"]["initial"]
        self.assertEqual(len(observations), 1)
        self.assertEqual({o["room"] for o in observations}, {"Main"})

    def test_later_successes_supply_counterexamples_to_universal_failure(self):
        initial = DATA["humility"]["initial"]
        later = DATA["humility"]["later"]
        self.assertFalse(any(o["usable"] for o in initial))
        self.assertEqual([o["id"] for o in later if o["usable"]], ["L3", "L4"])

    def test_main_room_failures_are_retained(self):
        observations = DATA["humility"]["initial"] + DATA["humility"]["later"]
        self.assertEqual(
            [o["usable"] for o in observations if o["room"] == "Main"], [False, False]
        )
        self.assertEqual([o["usable"] for o in observations if o["room"] == "Quiet Q"], [True, True])

    def test_fresh_counterexample_does_not_establish_majority_success(self):
        observations = DATA["humility"]["fresh_a"]
        successes = sum(o["usable"] for o in observations)
        self.assertGreater(successes, 0)
        self.assertLess(successes / len(observations), 0.5)

    def test_pressure_is_not_new_official_notice(self):
        initial, pressure, correction = DATA["humility"]["closure_versions"]
        official = [
            record for record in (initial, pressure, correction) if record["source"] == "official"
        ]
        self.assertEqual(official, [initial, correction])
        self.assertEqual((initial["scheduled"], correction["scheduled"]), ("closed", "open"))
        self.assertEqual(initial["effective_day"], correction["effective_day"])

    def test_scope_change_and_append_only_records_are_taught(self):
        guide = text("09.05")
        self.assertIn("scope changed or same proposition?", guide)
        self.assertIn("Append V2 rather than editing", guide)
        self.assertIn("Fictional updating demonstrates the procedure", guide)

    def test_new_evidence_ids_align_with_visible_packet(self):
        evidence = text("09.05", "evidence-update.md")
        for row in DATA["humility"]["later"]:
            self.assertIn(f"| {row['id']} |", evidence)
            self.assertIn(row["room"], evidence)
        for report in DATA["humility"]["reports_not_observations"]:
            self.assertIn(f"**{report}:**", evidence)


class Forecasting(unittest.TestCase):
    def test_base_rate_and_inclusive_boundary(self):
        ds = DATA["forecasting"]["history_delays"]
        self.assertEqual(sum(resolve(d)[1] for d in ds), 8)
        self.assertEqual(Fraction(sum(resolve(d)[1] for d in ds), len(ds)), Fraction(4, 5))
        self.assertEqual(resolve(5), ("scored", 1))
        self.assertEqual(resolve(5.1), ("scored", 0))

    def test_history_matches_visible_records(self):
        guide = text("09.06")
        for index, value in enumerate(DATA["forecasting"]["history_delays"], 1):
            self.assertIn(f"H{index}={value}", guide)

    def test_future_outcomes_match_separate_packet(self):
        packet = text("09.06", "outcomes.md")
        f = DATA["forecasting"]
        for key, delay in zip(f["forecast_ids"], f["outcome_delays"], strict=True):
            self.assertIn(f"| {key} | {delay} minutes", packet)
        self.assertEqual([resolve(d)[1] for d in f["outcome_delays"]], [1, 0, 1])

    def test_main_example_brier(self):
        self.assertEqual(brier([0.8] * 3, [1, 0, 1]), Fraction(6, 25))
        self.assertIn("0.72/3 = 0.24", text("09.06", "check-answers.md"))

    def test_low_probability_does_not_exclude_success(self):
        self.assertEqual(brier([0.25], [1]), Fraction(9, 16))
        self.assertGreater(probability(0.25), 0)

    def test_scoring_does_not_mutate_original_forecasts(self):
        ps, ys = [0.75, 0.25], [1, 1]
        before = copy.deepcopy((ps, ys))
        brier(ps, ys)
        self.assertEqual((ps, ys), before)

    def test_bad_probabilities_rejected(self):
        for p in (-0.1, 1.1, math.nan, math.inf, True, "0.8", None):
            with self.subTest(p=p), self.assertRaises(ValueError):
                brier([p], [1])

    def test_empty_mismatched_and_unresolved_scoring_rejected(self):
        for ps, ys in (([], []), ([0.2], []), ([0.2], [None]), ([0.2], [2]), ([0.2], [True])):
            with self.subTest(ps=ps, ys=ys), self.assertRaises(ValueError):
                brier(ps, ys)

    def test_score_extremes_and_fair_coin(self):
        self.assertEqual(brier([0, 1], [0, 1]), 0)
        self.assertEqual(brier([1, 0], [0, 1]), 1)
        self.assertEqual(brier([0.5, 0.5], [1, 0]), Fraction(1, 4))

    def test_missing_cancelled_and_confirmed_nonstart_are_distinct(self):
        self.assertEqual(resolve(None), ("unresolved", None))
        self.assertEqual(resolve(None, cancelled=True), ("void", None))
        self.assertEqual(resolve(None, confirmed_no_start=True), ("scored", 0))
        self.assertEqual(resolve(30), ("scored", 0))

    def test_invalid_delay_rejected(self):
        for delay in (math.inf, math.nan, "3", True):
            with self.subTest(delay=delay), self.assertRaises(ValueError):
                resolve(delay)

    def test_fresh_scored_denominator_and_exclusion_counts(self):
        records = DATA["forecasting"]["fresh_a"]
        statuses = [resolve(r["delay"], cancelled=r["cancelled"]) for r in records]
        self.assertEqual([s for s, _ in statuses], ["scored", "scored", "unresolved", "void"])
        pairs = [(r["p"], y) for r, (s, y) in zip(records, statuses, strict=True) if s == "scored"]
        self.assertEqual(len(pairs), 2)
        self.assertEqual(brier([p for p, _ in pairs], [y for _, y in pairs]), Fraction(5, 16))
        self.assertIn("0.625/2 = 0.3125", text("09.06", "check-answers.md"))

    def test_scenario_net_values_and_break_even(self):
        f = DATA["forecasting"]
        nets = [net_saving(p, f["cost"], f["benefit"]) for p in f["scenario_probabilities"]]
        self.assertEqual(nets, [Fraction(-1, 2), Fraction(7), Fraction(17, 2)])
        self.assertEqual(net_saving(Fraction(1, 3), 5, 15), 0)

    def test_sensitivity_range(self):
        self.assertEqual([net_saving(p, 5, 15) for p in (0.6, 0.9)], [Fraction(4), Fraction(17, 2)])

    def test_fresh_decision_and_worked_example(self):
        self.assertEqual(net_saving(Fraction(2, 5), 4, 10), 0)
        self.assertEqual([net_saving(p, 4, 10) for p in (0.2, 0.7)], [-2, 3])
        self.assertEqual(net_saving(0.25, 2, 12), 1)
        self.assertEqual(net_saving(Fraction(1, 6), 2, 12), 0)

    def test_invalid_costs_rejected(self):
        for cost, benefit in ((-1, 15), (5, 0), (5, -1)):
            with self.subTest(cost=cost, benefit=benefit), self.assertRaises(ValueError):
                net_saving(0.8, cost, benefit)

    def test_calibration_groups_and_whole_score(self):
        groups = DATA["forecasting"]["calibration"]
        for g in groups:
            self.assertEqual(len(g["outcomes"]), 10)
            self.assertEqual(Fraction(sum(g["outcomes"]), 10), probability(g["p"]))
            self.assertEqual(brier([g["p"]] * 10, g["outcomes"]), Fraction(4, 25))
        ps = [g["p"] for g in groups for _ in g["outcomes"]]
        ys = [y for g in groups for y in g["outcomes"]]
        self.assertEqual(brier(ps, ys), Fraction(4, 25))

    def test_calibration_sequences_match_prompt(self):
        prompt = text("09.06", "check-prompts.md")
        for g in DATA["forecasting"]["calibration"]:
            self.assertIn(", ".join(str(y) for y in g["outcomes"]), prompt)

    def test_low_brier_does_not_equal_empirical_calibration(self):
        rare = DATA["forecasting"]["rare_set"]
        self.assertEqual(brier([rare["p"]] * rare["n"], [0] * rare["n"]), Fraction(1, 10000))
        self.assertNotEqual(probability(rare["p"]), Fraction(rare["successes"], rare["n"]))
        self.assertIn("not calibration by itself", text("09.06"))


if __name__ == "__main__":
    unittest.main()
