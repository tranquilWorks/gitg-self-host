"""Standalone source and finite-model checks, not Django or learner validation.

Run: python -m unittest discover -s tests -p '*sources.py' -v
All datasets are fictional. Helpers here are test-only, not production algorithms.
"""

from __future__ import annotations

import itertools
import json
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs" / "authoring" / "systems-causes-tradeoffs"
DATA = json.loads((CONTENT / "fixtures.json").read_text(encoding="utf-8"))


def simulate(policy: str, initial: int = 2, arrivals: int = 4, days: int = 3):
    if policy not in {"baseline", "clarify", "hide"}:
        raise ValueError("Unknown policy")
    if any(type(x) is not int or x < 0 for x in (initial, arrivals, days)):
        raise ValueError("Counts must be nonnegative integers")
    ready, due, hidden, settled = initial, 0, 0, 0
    rows = []
    for day in range(1, days + 1):
        refused = min(1, arrivals) if policy == "hide" else 0
        admitted = arrivals - refused
        available = ready + due + admitted
        capacity = 3 if policy == "clarify" and day == 1 else 4
        attempts = min(available, capacity)
        ready = available - attempts
        due = int(available > 4 and attempts > 0) if policy != "clarify" else 0
        hidden += refused
        settled += attempts - due
        unfinished = ready + due + hidden
        rows.append(
            {
                "day": day,
                "D": available,
                "C": attempts,
                "ready": ready,
                "due": due,
                "hidden": hidden,
                "unfinished": unfinished,
                "settled": settled,
                "capacity": capacity,
            }
        )
    return rows


def inventory(include_pipeline: bool):
    stock, pending, orders, deliveries = 4, {}, [], []
    for week in range(1, 5):
        delivered = pending.pop(week, 0)
        stock += delivered
        deliveries.append(delivered)
        if week <= 2:
            position = stock + (sum(pending.values()) if include_pipeline else 0)
            order = max(0, 10 - position)
            pending[week + 2] = order
            orders.append(order)
    return orders, deliveries, stock


def correct_route(code: str) -> str:
    if len(code) != 2 or any(char not in "0123456789" for char in code):
        return "H"
    return "L" if int(code[-1]) % 2 else "R"


def posted_route(card: str, code: str) -> str:
    if card == "V2":
        return correct_route(code)
    if card != "V1":
        raise ValueError("Unknown instruction card")
    if not code or code[0] not in "0123456789":
        raise ValueError("V1 is defined only for a visible first ASCII digit")
    return "L" if int(code[0]) % 2 else "R"


def routing_summary(card: str, deck: list[str]):
    actual = [posted_route(card, code) for code in deck]
    required = [correct_route(code) for code in deck]
    return {
        "attempted": len(deck),
        "violations": sum(a != r for a, r in zip(actual, required, strict=True)),
        "completed": sum(a == r and a in {"L", "R"} for a, r in zip(actual, required, strict=True)),
        "held": actual.count("H"),
    }


def dominates(a, b):
    return (
        a["minutes"] <= b["minutes"]
        and a["benefit"] >= b["benefit"]
        and (a["minutes"] < b["minutes"] or a["benefit"] > b["benefit"])
    )


def rank_options(weight: str):
    factor = Fraction(weight)
    if factor < 0:
        raise ValueError("Time weight must be nonnegative in this toy preference")
    feasible = [o for o in DATA["tradeoffs"]["fresh_options"] if o["minutes"] <= 100]
    return sorted(
        [(o["name"], Fraction(o["benefit"]) - factor * o["minutes"]) for o in feasible],
        key=lambda item: (-item[1], item[0]),
    )


def availability(minutes: int, consent: bool | None, budget: int) -> str:
    if minutes > budget or consent is False:
        return "infeasible"
    return "confirmed" if consent is True else "contingent"


class SourceStructure(unittest.TestCase):
    def test_exact_cohort_and_unadvanced_runtime_counts(self):
        self.assertEqual(DATA["cohort"], ["09.07", "09.08", "09.09"])
        b = DATA["baseline"]
        self.assertEqual((b["runtime_tailored"], b["runtime_pending"]), (108, 275))
        self.assertEqual(b["runtime_tailored"] + b["runtime_pending"], b["protocols"])
        self.assertEqual(b["actions"], 1151)

    def test_guides_have_individual_complete_operations_and_limits(self):
        for cid in DATA["cohort"]:
            text = (CONTENT / cid / "learner-guide.md").read_text(encoding="utf-8")
            for term in [
                "Canonical scope",
                "Deliverable",
                "Action 1",
                "Action 2",
                "Action 3",
                "Accessibility",
                "Supportive",
                "Mixed",
                "Contradictory",
                "Inconclusive",
            ]:
                with self.subTest(cid=cid, term=term):
                    self.assertIn(term, text)

    def test_two_fresh_prompts_per_competency_with_separate_keys(self):
        for cid in DATA["cohort"]:
            prompt = (CONTENT / cid / "check-prompts.md").read_text(encoding="utf-8")
            answers = (CONTENT / cid / "check-answers.md").read_text(encoding="utf-8")
            self.assertIn("Check A", prompt)
            self.assertIn("Check B", prompt)
            self.assertNotIn(answers, prompt)
            self.assertNotIn("## Check A — Key", prompt)

    def test_root_cause_results_are_separate_from_main_guide(self):
        guide = (CONTENT / "09.08" / "learner-guide.md").read_text(encoding="utf-8")
        result = (CONTENT / "09.08" / "test-results.md").read_text(encoding="utf-8")
        self.assertIn("test-results.md", guide)
        self.assertNotIn(result, guide)
        self.assertNotIn("| V1/full | 8 | 4 | 4 | 0 |", guide)

    def test_source_files_have_no_placeholder_or_whitespace_defects(self):
        for path in CONTENT.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("TODO", text)
            self.assertNotIn("\x00", text)
            self.assertTrue(text.endswith("\n"))
            for line in text.splitlines():
                self.assertEqual(line, line.rstrip(), str(path))


class SystemDynamics(unittest.TestCase):
    def test_all_nine_fixture_rows_follow_the_given_recurrence(self):
        for policy in DATA["systems"]["policies"]:
            rows = [
                [r[k] for k in ["D", "C", "ready", "due", "hidden", "unfinished"]]
                for r in simulate(policy)
            ]
            self.assertEqual(rows, DATA["systems"]["expected"][policy])

    def test_conservation_across_small_complete_parameter_grid(self):
        for initial, arrivals, policy in itertools.product(
            range(6), range(7), DATA["systems"]["policies"]
        ):
            for row in simulate(policy, initial, arrivals, 5):
                self.assertEqual(
                    initial + row["day"] * arrivals, row["settled"] + row["unfinished"]
                )
                self.assertGreaterEqual(row["ready"], 0)
                self.assertGreaterEqual(row["settled"], 0)
                self.assertLessEqual(row["C"], min(row["D"], row["capacity"]))

    def test_next_day_rework_is_not_processed_on_the_same_day(self):
        rows = simulate("baseline")
        self.assertEqual(rows[0]["D"], 6)
        self.assertEqual(rows[1]["D"], rows[0]["ready"] + rows[0]["due"] + 4)

    def test_setup_cost_does_not_imply_higher_total_unfinished_initially(self):
        baseline, clarify = simulate("baseline")[0], simulate("clarify")[0]
        self.assertGreater(clarify["ready"], baseline["ready"])
        self.assertEqual(clarify["unfinished"], baseline["unfinished"])

    def test_hiding_improves_dashboard_not_total_unfinished(self):
        for honest, hidden in zip(simulate("baseline"), simulate("hide"), strict=True):
            self.assertLess(hidden["ready"], honest["ready"])
            self.assertEqual(hidden["unfinished"], honest["unfinished"])

    def test_clarification_stabilizes_but_does_not_clear_the_queue(self):
        self.assertEqual([r["unfinished"] for r in simulate("clarify", days=8)], [3] * 8)

    def test_processing_count_is_not_permanently_settled_count(self):
        rows = simulate("baseline")
        self.assertEqual(sum(r["C"] for r in rows), 12)
        self.assertEqual(rows[-1]["settled"], 9)
        self.assertEqual(simulate("clarify")[-1]["settled"], 11)

    def test_empty_system_does_not_create_work(self):
        for policy in DATA["systems"]["policies"]:
            self.assertTrue(
                all(r["unfinished"] == r["C"] == 0 for r in simulate(policy, initial=0, arrivals=0))
            )

    def test_invalid_parameters_fail_instead_of_normalizing(self):
        for args in [
            ("unknown", 2, 4, 3),
            ("baseline", -1, 4, 3),
            ("baseline", 1, 2.5, 3),
            ("baseline", True, 4, 3),
        ]:
            with self.assertRaises(ValueError):
                simulate(*args)

    def test_fresh_queue_conserves_and_keeps_delayed_stock(self):
        f = DATA["systems"]["fresh_queue"]
        self.assertEqual(f["initial"] + f["arrivals"] - f["attempts"], f["ready_end"])
        self.assertEqual(f["ready_end"] + f["reopen"], f["unfinished_end"])
        self.assertEqual(f["attempts"] - f["reopen"], f["settled"])
        self.assertEqual(f["unfinished_end"] + f["settled"], 10)

    def test_inventory_delay_and_pipeline_correct_duplicate_order(self):
        self.assertEqual(inventory(False), ([6, 6], [0, 0, 6, 6], 16))
        self.assertEqual(inventory(True), ([6, 0], [0, 0, 6, 0], 10))


class RootCause(unittest.TestCase):
    def test_all_four_conditions_match_derived_counts(self):
        c = DATA["causes"]
        for condition in c["conditions"]:
            deck = c["baseline_deck"] if condition["feed"] == "full" else c["masked_deck"]
            expected = {k: condition[k] for k in ["attempted", "violations", "completed", "held"]}
            self.assertEqual(routing_summary(condition["card"], deck), expected)

    def test_wrong_card_has_exact_four_full_feed_counterexamples(self):
        bad = [
            s for s in DATA["causes"]["baseline_deck"] if posted_route("V1", s) != correct_route(s)
        ]
        self.assertEqual(bad, ["12", "21", "34", "43"])

    def test_lucky_masked_guess_is_still_a_violation(self):
        self.assertEqual(posted_route("V1", "1?"), correct_route("11"))
        self.assertNotEqual(posted_route("V1", "1?"), correct_route("1?"))

    def test_correct_hold_is_not_completed_service(self):
        result = routing_summary("V2", DATA["causes"]["masked_deck"])
        self.assertEqual(result, {"attempted": 8, "violations": 0, "completed": 0, "held": 8})

    def test_fresh_deck_is_disjoint_from_baseline(self):
        c = DATA["causes"]
        self.assertFalse(set(c["baseline_deck"]) & set(c["fresh_deck"]))
        self.assertEqual(len(set(c["fresh_deck"])), 8)

    def test_fresh_valid_deck_meets_all_three_acceptance_conditions(self):
        c = DATA["causes"]
        self.assertEqual([correct_route(s) for s in c["fresh_deck"]], c["fresh_expected"])
        self.assertEqual(
            routing_summary("V2", c["fresh_deck"]),
            {"attempted": 8, "violations": 0, "completed": 8, "held": 0},
        )

    def test_invalid_challenge_has_a_separate_hold_denominator(self):
        c = DATA["causes"]
        self.assertEqual([correct_route(s) for s in c["invalid_deck"]], ["H"] * 4)
        self.assertEqual(routing_summary("V2", c["invalid_deck"])["completed"], 0)

    def test_exhaustive_hundred_ascii_codes(self):
        codes = [f"{n:02d}" for n in range(100)]
        self.assertEqual(routing_summary("V1", codes)["violations"], 50)
        self.assertEqual(routing_summary("V2", codes)["completed"], 100)

    def test_malformed_and_non_ascii_digits_are_not_silently_accepted(self):
        for code in ["", "1", "123", " 12", "12\n", "a2", "\uff11\uff12", "١٢", "?2"]:
            self.assertEqual(correct_route(code), "H")

    def test_unrecognized_card_is_rejected(self):
        with self.assertRaises(ValueError):
            posted_route("V3", "12")

    def test_followup_compares_label_within_each_location(self):
        rows = DATA["causes"]["confounded_followup"]
        for location in ["desk", "away"]:
            pair = [r for r in rows if r["location"] == location]
            self.assertEqual({r["label"] for r in pair}, {True, False})
            self.assertEqual(pair[0]["available"], pair[1]["available"])
        self.assertEqual([r["available"] for r in rows], [2, 2, 0, 0])

    def test_zero_wrong_routes_does_not_hide_lower_completion(self):
        before, after, verified = DATA["causes"]["service"]
        for row in [before, after, verified]:
            self.assertEqual(row["total"], row["completed"] + row["wrong"] + row["held"])
        self.assertEqual(Fraction(before["completed"], before["total"]), Fraction(7, 10))
        self.assertEqual(Fraction(after["completed"], after["total"]), Fraction(2, 5))
        self.assertEqual(Fraction(after["held"], after["total"]), Fraction(3, 5))
        self.assertEqual(verified["completed"], verified["total"])


class Tradeoffs(unittest.TestCase):
    def test_all_main_plans_preserve_the_protected_promise(self):
        m = DATA["tradeoffs"]["main"]
        self.assertEqual(m["total_minutes"] - m["protected_minutes"], m["optional_minutes"])
        for plan in m["plans"].values():
            self.assertEqual(sum(plan), 110)

    def test_combined_plan_is_infeasible_and_later_visit_unconfirmed(self):
        m = DATA["tradeoffs"]["main"]
        self.assertEqual(sum(m["combined_without_recovery"]), 180)
        self.assertEqual(sum(m["combined_without_recovery"]) - m["optional_minutes"], 70)
        self.assertFalse(m["later_visit_confirmed"])

    def test_feasibility_precedes_weighted_score(self):
        for weight in ["0", "0.1", "0.2", "2"]:
            self.assertNotIn("S", [name for name, _ in rank_options(weight)])

    def test_exact_pareto_frontier_on_stipulated_criteria(self):
        options = DATA["tradeoffs"]["fresh_options"][:3]
        frontier = [o["name"] for o in options if not any(dominates(other, o) for other in options)]
        self.assertEqual(frontier, ["P", "Q"])
        self.assertTrue(dominates(options[1], options[2]))

    def test_low_time_weight_prefers_q_and_foregoes_p(self):
        self.assertEqual(rank_options("0.10"), [("Q", 1), ("P", 0), ("R", -2)])

    def test_high_time_weight_prefers_p_and_foregoes_q(self):
        self.assertEqual(rank_options("0.20"), [("P", -5), ("Q", -6), ("R", -10)])

    def test_tie_weight_preserves_tie_instead_of_claiming_unique_choice(self):
        ranked = rank_options("0.15")
        self.assertEqual(ranked[0][1], Fraction(-5, 2))
        self.assertEqual(ranked[0][1], ranked[1][1])
        self.assertEqual({ranked[0][0], ranked[1][0]}, {"P", "Q"})

    def test_infeasible_and_unknown_permission_have_distinct_status(self):
        self.assertEqual(availability(45, None, 60), "contingent")
        self.assertEqual(availability(50, True, 60), "confirmed")
        self.assertEqual(availability(70, True, 60), "infeasible")

    def test_later_consent_can_change_feasibility_without_claiming_completion(self):
        self.assertEqual(availability(45, True, 60), "confirmed")
        self.assertEqual(availability(45, False, 60), "infeasible")
        self.assertNotEqual(availability(45, True, 60), "completed")


class SourceAlignment(unittest.TestCase):
    def test_system_answer_table_matches_every_fixture_row(self):
        text = (CONTENT / "09.07" / "check-answers.md").read_text(encoding="utf-8")
        for policy, label in [("baseline", "Baseline"), ("clarify", "Clarify"), ("hide", "Hide")]:
            for day, values in enumerate(DATA["systems"]["expected"][policy], 1):
                self.assertIn(f"| {label} {day} | " + " | ".join(map(str, values)) + " |", text)

    def test_queue_rules_in_guide_match_fixture_inputs(self):
        guide = (CONTENT / "09.07" / "learner-guide.md").read_text(encoding="utf-8")
        for text in [
            "**2 requests are ready**",
            "**4 new legitimate requests arrive each day.**",
            "3 on Day 1; 4 afterward",
            "B_next + R_next + H",
        ]:
            self.assertIn(text, guide)

    def test_routing_decks_in_guide_match_fixtures(self):
        guide = (CONTENT / "09.08" / "learner-guide.md").read_text(encoding="utf-8")
        for name in ["baseline_deck", "masked_deck", "fresh_deck"]:
            self.assertIn(", ".join(DATA["causes"][name]), guide)
        self.assertIn("exactly two ASCII digits", guide)

    def test_routing_result_table_matches_model_summaries(self):
        text = (CONTENT / "09.08" / "test-results.md").read_text(encoding="utf-8")
        for c in DATA["causes"]["conditions"]:
            vals = [c[k] for k in ["attempted", "violations", "completed", "held"]]
            self.assertIn(f"| {c['card']}/{c['feed']} | " + " | ".join(map(str, vals)) + " |", text)

    def test_tradeoff_prompt_has_exact_numeric_dataset(self):
        text = (CONTENT / "09.09" / "check-prompts.md").read_text(encoding="utf-8")
        for o in DATA["tradeoffs"]["fresh_options"]:
            self.assertIn(f"| {o['name']} | {o['minutes']} | {o['benefit']} |", text)

    def test_canonical_scope_map_covers_every_element(self):
        text = (CONTENT / "SCOPE-MAP.md").read_text(encoding="utf-8").lower()
        elements = [
            "components",
            "interfaces",
            "feedback",
            "delays",
            "incentives",
            "unintended",
            "second-order",
            "define the problem",
            "symptoms",
            "causes",
            "gather evidence",
            "test hypotheses",
            "verify improvement",
        ]
        for element in elements + DATA["tradeoffs"]["scope_elements"]:
            self.assertIn(element, text)


if __name__ == "__main__":
    unittest.main()
