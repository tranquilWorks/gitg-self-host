"""Original instructional fixtures and source checks, not application acceptance.

Run with Python's standard library:
    python -m unittest discover -s tests -p '*sources.py' -v
No network, participant records, production scoring, or Django is used here.
"""
from __future__ import annotations

import copy
import itertools
import json
import math
import re
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs/authoring/models-information-execution"
META = json.loads((CONTENT / "cohort.json").read_text())
DATA = json.loads((CONTENT / "fixtures.json").read_text())
IDS = ["09.16", "09.17", "11.01", "11.02", "11.03", "11.04"]


def text(cid, filename="learner-guide.md"):
    return (CONTENT / cid / filename).read_text(encoding="utf-8")


def model(n, setup=5, per_card=3):
    """The stated paper-card toy model, not a runtime estimator."""
    if type(n) is not int or n < 0:
        raise ValueError("Count must be a nonnegative whole number")
    for value in (setup, per_card):
        if isinstance(value, bool) or not isinstance(value, (int, float, Fraction)):
            raise ValueError("Invalid parameter type")
        if not math.isfinite(value) or value < 0:
            raise ValueError("Parameters must be finite and nonnegative")
    return 0 if n == 0 else setup + per_card * n


def source_roots(name, parents, active=()):
    if name not in parents or name in active:
        raise ValueError("Missing source or dependency cycle")
    if not parents[name]:
        return {name}
    result = set()
    for parent in parents[name]:
        result.update(source_roots(parent, parents, (*active, name)))
    return result


def minute(clock):
    if not isinstance(clock, str) or re.fullmatch(r"\d{2}:\d{2}", clock) is None:
        raise ValueError("Use HH:MM")
    h, m = map(int, clock.split(":"))
    if not 0 <= h < 24 or not 0 <= m < 60:
        raise ValueError("Invalid clock")
    return 60 * h + m


def audit(rows, start="18:00", end="21:00"):
    """Reject overlaps/gaps; never silently convert missing rows to free time."""
    cursor = minute(start)
    totals = Counter()
    for row in rows:
        a, b = minute(row["start"]), minute(row["end"])
        if a != cursor or b <= a or b - a != row["minutes"]:
            raise ValueError("Overlap, gap, invalid duration, or inconsistent row")
        if row["category"] not in {"Required", "Flexible", "Protected recovery", "Unknown"}:
            raise ValueError("Unknown category")
        totals[row["category"]] += b - a
        cursor = b
    if cursor != minute(end):
        raise ValueError("Incomplete window")
    return totals


def feasible(plan, budget, buffer=20):
    versions = DATA["priorities"]["versions"]
    if set(plan) != set(versions):
        raise ValueError("Every demand must have a disposition")
    if any(type(plan[k]) is not int or plan[k] not in versions[k] for k in versions):
        raise ValueError("Invented duration or unagreed version")
    if type(budget) is not int or type(buffer) is not int or budget < 0 or buffer < 0:
        raise ValueError("Invalid capacity")
    return sum(plan.values()) + buffer <= budget


def goal_status(record):
    """Classify this paper prototype only; not a production evidence rule."""
    if record["permission"] is not True:
        return "blocked_permission"
    if record["purchases"] != 0 or record["effort"] > DATA["goal"]["effort_limit"]:
        return "constraint_failed"
    if record["reserved_clear"] is not True or record["answer_help"] is not False:
        return "constraint_failed"
    requests, found, returned = record["requests"], record["found"], record["returned"]
    if len(requests) != 3 or set(requests) != set(DATA["goal"]["items"]):
        raise ValueError("Exactly the three requested items are required")
    if len(found) != 3 or len(returned) != 3:
        raise ValueError("Exactly three observations per type are required")
    if any(value is None for value in [*found, *returned]):
        return "inconclusive"
    homes = DATA["goal"]["homes"]
    correct = all(f == q and r == homes[q] for q, f, r in zip(requests, found, returned, strict=True))
    return "met_for_tested_scope" if correct else "partial"


def topo(tasks):
    remaining = set(tasks)
    done = []
    if any(d not in tasks for t in tasks.values() for d in t["deps"]):
        raise ValueError("Missing prerequisite")
    while remaining:
        ready = sorted(n for n in remaining if set(tasks[n]["deps"]) <= set(done))
        if not ready:
            raise ValueError("Dependency cycle")
        done.append(ready[0])
        remaining.remove(ready[0])
    return done


def earliest_parallel(tasks):
    finish = {}
    for n in topo(tasks):
        effort = tasks[n]["effort"]
        if type(effort) is not int or effort < 0:
            raise ValueError("Invalid duration")
        finish[n] = max((finish[d] for d in tasks[n]["deps"]), default=0) + effort
    return max(finish.values(), default=0)


def ready_for_confirmation(branch):
    return all(branch[k] is True for k in ("R_consent", "T_consent", "time_agreed", "access_agreed"))


class SourceStructure(unittest.TestCase):
    def test_exact_six_new_ids(self):
        self.assertEqual([c["id"] for c in META["competencies"]], IDS)
        self.assertEqual(META["user_batch_size"], 6)

    def test_does_not_duplicate_authored_learning_domain(self):
        self.assertFalse(any(c.startswith("10.") for c in IDS))

    def test_runtime_and_formal_counts_unchanged(self):
        self.assertEqual((META["runtime_tailored"], META["runtime_pending"]), (108, 275))
        self.assertEqual(META["protocols"], 383)
        self.assertEqual(META["actions"], 1151)
        self.assertFalse(META["runtime_changes"])
        self.assertEqual(META["formal_reviews_accepted"], 0)

    def test_all_declared_materials_exist(self):
        for c in META["competencies"]:
            for key in ("guide", "prompts", "answers", "later_packet"):
                if c[key]:
                    self.assertTrue((CONTENT / c["id"] / c[key]).is_file())

    def test_guides_are_distinct_and_have_complete_actions(self):
        guides = [text(c) for c in IDS]
        self.assertEqual(len(set(guides)), 6)
        for guide in guides:
            for phrase in ("Canonical scope", "Action 1", "Action 2", "Action 3",
                           "Supportive", "Mixed", "Contradictory", "Inconclusive", "Final review"):
                self.assertIn(phrase, guide)

    def test_twelve_fresh_checks_and_eighteen_key_sections(self):
        for cid in IDS:
            prompts = text(cid, "check-prompts.md")
            answers = text(cid, "check-answers.md")
            self.assertEqual(len(re.findall(r"^## Check [AB]", prompts, re.M)), 2)
            self.assertEqual(len(re.findall(r"^## ", answers, re.M)), 3)
            self.assertNotIn(answers, text(cid))

    def test_five_separate_later_packets(self):
        self.assertEqual(sum(c["later_packet"] is not None for c in META["competencies"]), 5)
        for c in META["competencies"]:
            if c["later_packet"]:
                self.assertNotIn(text(c["id"], c["later_packet"]), text(c["id"]))

    def test_no_source_placeholders_or_trailing_space(self):
        for path in CONTENT.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("TODO", content)
            self.assertNotIn("\0", content)
            for line in content.splitlines():
                self.assertEqual(line, line.rstrip(), path)

    def test_all_canonical_elements_mapped(self):
        scope = (CONTENT / "SCOPE-MAP.md").read_text().lower()
        for c in META["competencies"]:
            for element in c["canonical_elements"]:
                self.assertIn(element.lower(), scope)

    def test_private_records_are_not_scoring_inputs(self):
        self.assertIn("not automated scoring inputs", text("11.03"))
        self.assertIn("does not require continuous tracking", text("11.01"))
        self.assertIn("No live invitation", text("11.04"))


class ModelCases(unittest.TestCase):
    def test_fit_records_match_without_being_holdouts(self):
        for row in DATA["model"]["fit"]:
            self.assertEqual(model(row["n"]), row["minutes"])
        self.assertEqual(len(DATA["model"]["fit"]), 2)

    def test_zero_has_no_setup(self):
        self.assertEqual(model(0), 0)

    def test_positive_values(self):
        self.assertEqual([model(n) for n in (2, 3, 4, 6)], [11, 14, 17, 23])

    def test_invalid_counts_rejected(self):
        for n in (-1, 1.5, None, True, "3", float("inf"), float("nan")):
            with self.subTest(n=n), self.assertRaises(ValueError):
                model(n)

    def test_invalid_parameters_rejected(self):
        for p in (-1, None, True, "3", float("nan"), float("inf")):
            with self.subTest(p=p), self.assertRaises(ValueError):
                model(3, per_card=p)

    def test_sensitivity_all_four_corners(self):
        s = DATA["model"]["sensitivity"]
        values = [model(s["n"], a, b) for a, b in itertools.product(s["setup"], s["per_card"])]
        self.assertEqual(values, [15, 27, 19, 31])
        self.assertEqual((min(values), max(values)), (15, 31))

    def test_deadline_not_robust(self):
        self.assertLess(model(6), 25)
        self.assertGreater(model(6, 7, 4), 25)

    def test_parameter_spreads_not_probabilities(self):
        self.assertEqual(7 - 3, 4)
        self.assertEqual((4 - 2) * 6, 12)
        self.assertNotIn("probability", DATA["model"]["sensitivity"])

    def test_holdout_errors(self):
        errors = [row["minutes"] - model(row["n"]) for row in DATA["model"]["holdouts"]]
        self.assertEqual(errors, [1, 8])
        self.assertEqual([abs(e) > 5 for e in errors], [False, True])

    def test_strict_trigger_boundary(self):
        self.assertFalse(abs(5) > DATA["model"]["error_trigger"])
        self.assertTrue(abs(-6) > DATA["model"]["error_trigger"])

    def test_fresh_rate_units(self):
        f = DATA["model"]["fresh"]
        self.assertEqual(f["setup"] + Fraction(f["count"], f["rate"]), 8)

    def test_identical_small_fit_not_unique_extrapolation(self):
        second = lambda n: model(n) + max(0, n - 6)
        for n in range(0, 7):
            self.assertEqual(model(n), second(n))
        self.assertEqual((model(10), second(10)), (35, 39))

    def test_visible_fit_and_holdout_tables_match(self):
        for row in DATA["model"]["fit"]:
            self.assertIn(f"| {row['n']} | {row['minutes']} minutes |", text("09.16"))
        later = text("09.16", "later-packet.md")
        for row in DATA["model"]["holdouts"]:
            self.assertIn(f"| {row['id']} | {row['n']} |", later)
            self.assertIn(f"| {row['minutes']} minutes |", later)


class InformationCases(unittest.TestCase):
    def test_three_reposts_have_one_claim_root(self):
        p = DATA["information"]["parents"]
        self.assertEqual(set.union(*(source_roots(n, p) for n in ("A1", "A2", "A3"))), {"H1"})

    def test_contact_and_notice_not_independent_observations(self):
        p = DATA["information"]["parents"]
        self.assertEqual(source_roots("P1", p), source_roots("N1", p))

    def test_visit_is_a_distinct_narrow_record(self):
        p = DATA["information"]["parents"]
        self.assertEqual(source_roots("W1", p), {"W1"})
        self.assertEqual(DATA["information"]["visit"]["room"], "South Room")
        self.assertNotEqual(DATA["information"]["visit"]["room"], DATA["information"]["notice"]["room"])

    def test_claim_graph_cycle_rejected(self):
        with self.assertRaises(ValueError):
            source_roots("A", {"A": ["B"], "B": ["A"]})

    def test_missing_source_rejected_not_counted_as_independent(self):
        with self.assertRaises(ValueError):
            source_roots("A", {"A": ["missing"]})

    def test_notice_bounded_closure_and_no_payment(self):
        notice = DATA["information"]["notice"]
        self.assertFalse(notice["permanent"])
        self.assertFalse(notice["rescue_payment_required"])
        self.assertEqual(minute(notice["end"]) - minute(notice["start"]), 120)

    def test_actor_and_transfers_remain_unestablished(self):
        unknown = DATA["information"]["unestablished"]
        self.assertIn("operator identity", unknown)
        self.assertIn("payment transfers", unknown)
        self.assertIn("hostile controller", unknown)

    def test_fresh_case_does_not_restore_cancelled_class(self):
        key = text("09.17", "check-answers.md")
        self.assertIn("pottery class", key)
        self.assertIn("preserves the pottery cancellation", key)
        self.assertIn("does not make an otherwise corroborated fact false", key)

    def test_no_live_payment_or_contact_link_in_exercises(self):
        for name in ("learner-guide.md", "later-packet.md", "check-prompts.md", "check-answers.md"):
            self.assertNotRegex(text("09.17", name), r"https?://|mailto:")

    def test_source_chain_visible_in_materials(self):
        guide = text("09.17")
        self.assertIn("A2 -> A1 -> H1", guide)
        self.assertIn("A3 -> H1", guide)
        self.assertIn("not a second independently observed event", text("09.17", "check-answers.md"))


class TimeAuditCases(unittest.TestCase):
    def rows(self, day):
        return [r for r in DATA["audit"]["rows"] if r["day"] == day]

    def test_every_day_covers_exact_window(self):
        for day in ("D1", "D2", "D3", "D4"):
            self.assertEqual(sum(audit(self.rows(day)).values()), 180)

    def test_baseline_category_totals(self):
        result = Counter()
        for day in DATA["audit"]["baseline_days"]:
            result.update(audit(self.rows(day)))
        self.assertEqual(dict(result), {"Required": 315, "Flexible": 105, "Protected recovery": 90, "Unknown": 30})
        self.assertEqual(sum(result.values()), 540)

    def test_reading_record_and_unknown_bound(self):
        rows = [r for r in DATA["audit"]["rows"] if r["day"] in DATA["audit"]["baseline_days"]]
        reading = sum(r["minutes"] for r in rows if r["activity"] == "Reading")
        unknown = sum(r["minutes"] for r in rows if r["category"] == "Unknown")
        self.assertEqual((reading, reading + unknown), (10, 40))
        self.assertEqual({r["day"] for r in rows if r["activity"] == "Reading"}, {"D2"})

    def test_trial_not_original_ten_minute_success(self):
        trial = self.rows("D4")
        reading = next(r for r in trial if r["activity"] == "Reading")
        self.assertEqual(reading["minutes"], 7)
        self.assertLess(reading["minutes"], DATA["audit"]["reading_goal_minutes"])

    def test_trial_category_totals(self):
        self.assertEqual(dict(audit(self.rows("D4"))), {"Required": 115, "Flexible": 35, "Protected recovery": 30})

    def test_trial_context_not_equal_to_baseline(self):
        durations = {day: next(r["minutes"] for r in self.rows(day) if r["activity"] == "Care") for day in ("D1", "D2", "D3", "D4")}
        self.assertEqual(durations, {"D1": 30, "D2": 45, "D3": 60, "D4": 55})

    def test_overlap_rejected(self):
        rows = copy.deepcopy(self.rows("D1"))
        rows[1]["start"] = "18:20"
        rows[1]["minutes"] = 40
        with self.assertRaises(ValueError):
            audit(rows)

    def test_missing_interval_rejected(self):
        with self.assertRaises(ValueError):
            audit(self.rows("D1")[1:])

    def test_inconsistent_duration_rejected(self):
        rows = copy.deepcopy(self.rows("D1"))
        rows[0]["minutes"] = 31
        with self.assertRaises(ValueError):
            audit(rows)

    def test_incomplete_end_rejected(self):
        with self.assertRaises(ValueError):
            audit(self.rows("D1")[:-1])

    def test_clock_bounds(self):
        for clock in ("24:00", "08:60", "8:00", "invalid", None):
            with self.subTest(clock=clock), self.assertRaises(ValueError):
                minute(clock)

    def test_no_capacity_case_balances_without_hidden_free_time(self):
        d = DATA["audit"]["no_capacity"]
        self.assertEqual(d["window"] - d["meal"] - d["care"] - d["recovery"], 0)

    def test_all_baseline_rows_match_visible_table(self):
        guide = text("11.01")
        for day in DATA["audit"]["baseline_days"]:
            for r in self.rows(day):
                self.assertIn(f"| {day} | {r['start']}–{r['end']} | {r['activity']} | {r['minutes']} | {r['category']} | {r['energy']} |", guide)

    def test_all_trial_rows_match_visible_packet(self):
        later = text("11.01", "later-packet.md")
        for r in self.rows("D4"):
            self.assertIn(f"| {r['start']}–{r['end']} | {r['activity']} | {r['minutes']} | {r['category']} |", later)


class PriorityCases(unittest.TestCase):
    def test_full_plan_exceeds_capacity(self):
        p = DATA["priorities"]
        self.assertEqual(sum(p["full"].values()) + p["buffer"], 350)
        self.assertFalse(feasible(p["full"], p["budget"]))

    def test_every_nonzero_minimum_still_exceeds(self):
        p = DATA["priorities"]
        plan = {k: min(v for v in values if v > 0) for k, values in p["versions"].items()}
        self.assertEqual(sum(plan.values()) + 20, 215)
        self.assertFalse(feasible(plan, 210))

    def test_learning_plan_fits_with_real_spare_time(self):
        p = DATA["priorities"]["plan_learning"]
        self.assertTrue(feasible(p, 210))
        self.assertEqual(210 - 20 - sum(p.values()), 25)

    def test_project_plan_also_fits(self):
        p = DATA["priorities"]["plan_project"]
        self.assertTrue(feasible(p, 210))
        self.assertEqual(210 - 20 - sum(p.values()), 10)

    def test_both_old_plans_fail_reduced_budget(self):
        for key in ("plan_learning", "plan_project"):
            self.assertFalse(feasible(DATA["priorities"][key], 160))

    def test_revised_plan_fits(self):
        plan = DATA["priorities"]["plan_revised"]
        self.assertTrue(feasible(plan, 160))
        self.assertEqual(160 - 20 - sum(plan.values()), 5)

    def test_no_invented_five_minute_project(self):
        plan = dict(DATA["priorities"]["plan_learning"], P=5)
        with self.assertRaises(ValueError):
            feasible(plan, 210)

    def test_omitted_demand_is_not_silent_deferral(self):
        plan = dict(DATA["priorities"]["plan_learning"])
        del plan["P"]
        with self.assertRaises(ValueError):
            feasible(plan, 210)

    def test_all_fifty_four_defined_plan_combinations(self):
        p = DATA["priorities"]
        keys = list(p["versions"])
        plans = [dict(zip(keys, values, strict=True)) for values in itertools.product(*(p["versions"][k] for k in keys))]
        self.assertEqual(len(plans), 54)
        for plan in plans:
            self.assertEqual(feasible(plan, 210), sum(plan.values()) <= 190)
            self.assertEqual(feasible(plan, 160), sum(plan.values()) <= 140)

    def test_new_visit_agreement_changes_feasibility(self):
        plan = dict(DATA["priorities"]["plan_revised"], R=60)
        self.assertEqual(sum(plan.values()) + 20, 185)
        self.assertFalse(feasible(plan, 160))
        plan["G"] = 0
        self.assertEqual(sum(plan.values()) + 20, 170)
        self.assertFalse(feasible(plan, 160))

    def test_prompt_and_key_visit_figures_match(self):
        self.assertIn("O=60, M=30, R=30, G=15, buffer=20", text("11.02", "check-prompts.md"))
        self.assertIn("**185**", text("11.02", "check-answers.md"))


class GoalCases(unittest.TestCase):
    def prototype(self):
        return copy.deepcopy(DATA["goal"]["prototype"])

    def good(self):
        result = self.prototype()
        result["returned"] = [DATA["goal"]["homes"][q] for q in result["requests"]]
        return result

    def test_prototype_is_partial_not_met(self):
        self.assertEqual(goal_status(self.prototype()), "partial")

    def test_three_finds_two_returns(self):
        r = self.prototype()
        homes = DATA["goal"]["homes"]
        self.assertEqual(sum(f == q for q, f in zip(r["requests"], r["found"], strict=True)), 3)
        self.assertEqual(sum(v == homes[q] for q, v in zip(r["requests"], r["returned"], strict=True)), 2)

    def test_correct_local_scope_not_household_mastery(self):
        self.assertEqual(goal_status(self.good()), "met_for_tested_scope")

    def test_permission_missing_blocks(self):
        for value in (False, None):
            r = self.good(); r["permission"] = value
            self.assertEqual(goal_status(r), "blocked_permission")

    def test_reserved_zone_violation_fails(self):
        r = self.good(); r["reserved_clear"] = False
        self.assertEqual(goal_status(r), "constraint_failed")

    def test_unrecorded_returns_inconclusive(self):
        r = self.good(); r["returned"] = [None, None, None]
        self.assertEqual(goal_status(r), "inconclusive")

    def test_answer_selection_help_not_independent_result(self):
        r = self.good(); r["answer_help"] = True
        self.assertEqual(goal_status(r), "constraint_failed")

    def test_purchases_and_effort_limit_enforced(self):
        r = self.good(); r["purchases"] = 1
        self.assertEqual(goal_status(r), "constraint_failed")
        r = self.good(); r["effort"] = 21
        self.assertEqual(goal_status(r), "constraint_failed")
        r["effort"] = 20
        self.assertEqual(goal_status(r), "met_for_tested_scope")

    def test_repeated_request_cannot_replace_missing_item(self):
        r = self.good(); r["requests"] = ["PENCIL"] * 3
        with self.assertRaises(ValueError):
            goal_status(r)

    def test_all_sixty_four_find_return_patterns(self):
        for flags in itertools.product((False, True), repeat=6):
            r = self.good()
            r["found"] = [q if ok else "wrong" for q, ok in zip(r["requests"], flags[:3], strict=True)]
            r["returned"] = [home if ok else "D" for home, ok in zip(r["returned"], flags[3:], strict=True)]
            expected = "met_for_tested_scope" if all(flags) else "partial"
            self.assertEqual(goal_status(r), expected)

    def test_original_prototype_not_mutated_by_repairs(self):
        original = json.dumps(DATA["goal"]["prototype"], sort_keys=True)
        self.good()
        self.assertEqual(json.dumps(DATA["goal"]["prototype"], sort_keys=True), original)

    def test_packet_matches_actual_return_rows(self):
        r = self.prototype(); homes = DATA["goal"]["homes"]
        for q, f, returned in zip(r["requests"], r["found"], r["returned"], strict=True):
            self.assertIn(f"| {q} | {f} | {returned} | {homes[q]} |", text("11.03", "later-packet.md"))


class MilestoneCases(unittest.TestCase):
    def test_preparation_and_total_effort_separate(self):
        m = DATA["milestones"]
        self.assertEqual(sum(m["tasks"][k]["effort"] for k in m["prep_ids"]), 35)
        self.assertEqual(sum(t["effort"] for t in m["tasks"].values()), 60)
        self.assertEqual(m["prep_limit"], 40)

    def test_wait_and_session_date_not_active_work(self):
        m = DATA["milestones"]
        self.assertEqual(m["response_checkpoint"], "Day 3 noon")
        self.assertEqual(m["external_requirements"]["A"], ["required_replies"])
        self.assertEqual(m["external_requirements"]["E"], ["agreed_session_time"])

    def test_ready_branch_not_event_completion(self):
        r = DATA["milestones"]["ready"]
        self.assertTrue(ready_for_confirmation(r))
        self.assertFalse(r["final_confirmation"])
        self.assertFalse(r["event_occurred"])

    def test_silence_blocks_not_consent(self):
        r = DATA["milestones"]["blocked"]
        self.assertFalse(ready_for_confirmation(r))
        self.assertIsNone(r["T_consent"])

    def test_all_sixteen_boolean_readiness_combinations(self):
        keys = ("R_consent", "T_consent", "time_agreed", "access_agreed")
        for values in itertools.product((False, True), repeat=4):
            self.assertEqual(ready_for_confirmation(dict(zip(keys, values, strict=True))), all(values))

    def test_unknown_in_each_gate_stays_unready(self):
        for key in ("R_consent", "T_consent", "time_agreed", "access_agreed"):
            r = dict(DATA["milestones"]["ready"]); r[key] = None
            self.assertFalse(ready_for_confirmation(r))

    def test_two_valid_single_worker_orders(self):
        tasks = DATA["milestones"]["fresh_tasks"]
        valid = []
        for order in itertools.permutations(tasks):
            positions = {n: i for i, n in enumerate(order)}
            if all(positions[d] < positions[n] for n, task in tasks.items() for d in task["deps"]):
                valid.append("".join(order))
        self.assertEqual(valid, ["ABCDE", "ACBDE"])

    def test_parallel_lower_bound_and_single_worker_effort(self):
        tasks = DATA["milestones"]["fresh_tasks"]
        self.assertEqual(earliest_parallel(tasks), 25)
        self.assertEqual(sum(t["effort"] for t in tasks.values()), 30)

    def test_revised_duration_updates_both_measures(self):
        tasks = copy.deepcopy(DATA["milestones"]["fresh_tasks"])
        tasks["B"]["effort"] = 8
        self.assertEqual(earliest_parallel(tasks), 23)
        self.assertEqual(sum(t["effort"] for t in tasks.values()), 28)

    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):
            topo({"proposal": {"deps": ["confirmation"]}, "confirmation": {"deps": ["proposal"]}})

    def test_missing_prerequisite_rejected(self):
        with self.assertRaises(ValueError):
            topo({"A": {"deps": ["absent"]}})

    def test_invalid_duration_rejected(self):
        for value in (-1, 1.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                earliest_parallel({"A": {"deps": [], "effort": value}})

    def test_source_branches_explicitly_not_combined(self):
        p = text("11.04", "later-packet.md")
        self.assertIn("mutually exclusive", p)
        self.assertIn("Neither contains a completed discussion", p)

    def test_complete_story_and_questions_exist(self):
        guide = text("11.04")
        self.assertIn("The community cupboard had one blank shelf", guide)
        self.assertIn("What evidence should change the first plan?", guide)
        self.assertIn("When does leaving space serve a purpose", guide)


if __name__ == "__main__":
    unittest.main()
