"""Source-only regression checks; no Django, score, learner, or runtime claims.

Run from this bundle or a repository containing it:
    python -m unittest discover -s tests -p test_m6k_reasoning_sources.py -v

These tests verify original toy cases and content structure. They do not establish
instructional effectiveness, complete canonical projection, or human acceptance.
"""

from __future__ import annotations

import copy
import itertools
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs" / "authoring" / "reasoning-foundations"
DATA = json.loads((CONTENT / "fixtures.json").read_text(encoding="utf-8"))


def implies(p: bool, q: bool) -> bool:
    return not p or q


def counterexamples(premises, conclusion):
    """Exhaust all four assignments, granting every premise before testing C."""
    return [
        (p, q)
        for p, q in itertools.product((False, True), repeat=2)
        if all(premise(p, q) for premise in premises) and not conclusion(p, q)
    ]


def decision(packet):
    """Apply this fictional packet's rule, not a general decision algorithm."""
    if packet["needs_rest"]:
        return "home"
    eligible = [
        option
        for option in packet["options"]
        if option["participation"]
        and option["access_confirmed"] is True
        and option["travel"] + option["session"] <= packet["budget_minutes"]
    ]
    if not eligible:
        return "home"
    return min(eligible, key=lambda o: (o["travel"] + o["session"], o["name"]))["name"]


class SourceStructure(unittest.TestCase):
    def test_exact_three_canonical_ids(self):
        self.assertEqual(DATA["cohort"], ["09.01", "09.02", "09.03"])

    def test_baseline_counts_are_not_advanced(self):
        b = DATA["baseline"]
        self.assertEqual((b["runtime_tailored"], b["runtime_pending"]), (108, 275))
        self.assertEqual(b["runtime_tailored"] + b["runtime_pending"], b["protocols"])
        self.assertEqual(b["actions"], 1151)

    def test_each_has_guide_prompt_and_separate_key(self):
        for competency in DATA["cohort"]:
            with self.subTest(competency=competency):
                for name in ("learner-guide.md", "check-prompts.md", "check-answers.md"):
                    text = (CONTENT / competency / name).read_text(encoding="utf-8")
                    self.assertTrue(text.startswith("# " + competency))
                    self.assertNotIn("TODO", text)

    def test_guides_have_scope_actions_access_and_outcomes(self):
        for competency in DATA["cohort"]:
            with self.subTest(competency=competency):
                text = (CONTENT / competency / "learner-guide.md").read_text(encoding="utf-8")
                for token in (
                    "Canonical scope",
                    "Action 1",
                    "Action 2",
                    "Action 3",
                    "Accessibility",
                    "Supportive",
                    "Mixed",
                    "Contradictory",
                    "Inconclusive",
                ):
                    self.assertIn(token, text)

    def test_prompt_files_have_two_fresh_checks(self):
        for competency in DATA["cohort"]:
            with self.subTest(competency=competency):
                text = (CONTENT / competency / "check-prompts.md").read_text(encoding="utf-8")
                self.assertIn("Check A", text)
                self.assertIn("Check B", text)
                self.assertNotIn("## Answer", text)

    def test_answers_are_not_appended_to_the_guide(self):
        for competency in DATA["cohort"]:
            with self.subTest(competency=competency):
                guide = (CONTENT / competency / "learner-guide.md").read_text(encoding="utf-8")
                answers = (CONTENT / competency / "check-answers.md").read_text(encoding="utf-8")
                self.assertNotIn(answers, guide)
                self.assertIn("check-answers.md", guide)

    def test_logic_verdicts_not_spelled_out_in_prompt(self):
        text = (CONTENT / "09.02" / "check-prompts.md").read_text(encoding="utf-8").lower()
        for giveaway in (
            "affirming the consequent",
            "modus tollens",
            "voucher argument is invalid",
            "approval argument is valid",
        ):
            self.assertNotIn(giveaway, text)

    def test_seven_bias_routes_are_present(self):
        text = (CONTENT / "09.03" / "learner-guide.md").read_text(encoding="utf-8").lower()
        for route in DATA["bias"]["routes"]:
            self.assertIn(route, text)

    def test_no_trailing_whitespace_or_nul(self):
        for path in CONTENT.rglob("*.md"):
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                with self.subTest(path=path.name, line=line_no):
                    self.assertEqual(line, line.rstrip())
                    self.assertNotIn("\0", line)


class ObservationCases(unittest.TestCase):
    def test_sent_log_does_not_establish_reading_or_agreement(self):
        claim = DATA["observation"]["claims"][0]
        self.assertEqual(claim["classification"], "bounded_observation")
        self.assertIn("reading", claim["does_not_establish"])
        self.assertIn("deadline agreement", claim["does_not_establish"])

    def test_emotion_remains_a_report_not_motive_evidence(self):
        claim = DATA["observation"]["claims"][2]
        self.assertEqual(claim["classification"], "attributed_report")
        self.assertIn("Lea's motive", claim["does_not_establish"])

    def test_secondary_online_report_is_not_promoted_to_direct_fact(self):
        claim = DATA["observation"]["claims"][3]
        self.assertEqual(claim["source"], "Sam")
        self.assertEqual(claim["classification"], "attributed_report")
        self.assertIn("message read", claim["does_not_establish"])

    def test_reply_and_screenshot_have_distinct_limits(self):
        reply, screenshot = DATA["observation"]["claims"][-2:]
        self.assertNotEqual(reply["classification"], screenshot["classification"])
        for claim in (reply, screenshot):
            self.assertIn("completed chair count", claim["does_not_establish"])

    def test_fresh_case_preserves_prediction_and_conclusion(self):
        labels = DATA["observation"]["check_a_expected"]
        self.assertEqual(labels[-2:], ["prediction", "conclusion"])
        self.assertIn("attributed_report_containing_unverified_motive", labels)

    def test_tool_location_does_not_establish_witnessed_cause(self):
        o = DATA["observation"]
        self.assertEqual(o["check_b_new_location"], "Cabinet D")
        self.assertEqual(o["check_b_move_cause"], "staff_report_not_independently_witnessed")


class LogicCases(unittest.TestCase):
    def test_worked_token_argument_is_sound_in_closed_world(self):
        tokens = DATA["logic"]["tokens"]
        self.assertTrue(all(t["location"] == "drawer" for t in tokens if t["color"] == "blue"))
        t1 = next(t for t in tokens if t["id"] == "T1")
        self.assertEqual((t1["color"], t1["location"]), ("blue", "drawer"))

    def test_modus_ponens_has_no_counterexample(self):
        self.assertEqual(counterexamples([implies, lambda p, q: p], lambda p, q: q), [])

    def test_affirming_consequent_has_true_premises_false_conclusion(self):
        self.assertEqual(
            counterexamples([implies, lambda p, q: q], lambda p, q: p), [(False, True)]
        )

    def test_modus_tollens_has_no_counterexample(self):
        self.assertEqual(counterexamples([implies, lambda p, q: not q], lambda p, q: not p), [])

    def test_a_is_valid_but_has_false_first_premise(self):
        events = DATA["logic"]["events"]
        cedar = events[0]
        p1 = all(e["admission"] + e["travel"] == 0 for e in events if e["advertised_free"])
        p2 = cedar["advertised_free"]
        conclusion = cedar["admission"] + cedar["travel"] == 0
        self.assertEqual([p1, p2], DATA["logic"]["argument_a"]["premises_true_in_packet"])
        self.assertFalse(conclusion)
        self.assertEqual(cedar["admission"] + cedar["travel"], 6)

    def test_b_inventory_supplies_counterexample(self):
        events = DATA["logic"]["events"]
        many = DATA["logic"]["many_threshold"]
        p1 = all(e["reservations"] >= many for e in events if e["reservations"] == e["seats"])
        cedar = events[0]
        p2 = cedar["reservations"] >= many
        conclusion = cedar["reservations"] == cedar["seats"]
        self.assertEqual([p1, p2], DATA["logic"]["argument_b"]["premises_true_in_packet"])
        self.assertTrue(p1 and p2 and not conclusion)

    def test_invalid_form_can_have_true_conclusion(self):
        p, q = True, True
        self.assertTrue(implies(p, q) and q and p)
        self.assertNotEqual(counterexamples([implies, lambda p, q: q], lambda p, q: p), [])

    def test_room_capacity_is_not_opening_confirmation(self):
        room = DATA["logic"]["fresh_room"]
        self.assertGreaterEqual(room["M_seats"], room["attendees"])
        self.assertLess(room["N_seats"], room["attendees"])
        self.assertTrue(room["M_reservation_confirmation"])
        self.assertIsNone(room["M_opening_confirmation"])
        self.assertIsNone(room["M_access_confirmation"])

    def test_different_day_claims_do_not_form_same_proposition(self):
        self.assertNotEqual(("room open", "Day 4", "18:00"), ("room open", "Day 5", "18:00"))


class SourceFixtureAlignment(unittest.TestCase):
    def test_observation_prompt_and_key_order_matches_fixture(self):
        prompt = (CONTENT / "09.01" / "check-prompts.md").read_text(encoding="utf-8")
        key = (CONTENT / "09.01" / "check-answers.md").read_text(encoding="utf-8")
        self.assertIn("2. The coordinator personally changed the entry.", prompt)
        self.assertIn("2. **Unestablished inference about the actor:**", key)
        self.assertEqual(DATA["observation"]["check_a_expected"][1], "unknown")
        self.assertIn("3. Robin reports embarrassment.", prompt)
        self.assertEqual(DATA["observation"]["check_a_expected"][2], "attributed_report")
        self.assertIn("4. Pat attributes the cancellation", prompt)
        self.assertEqual(
            DATA["observation"]["check_a_expected"][3],
            "attributed_report_containing_unverified_motive",
        )

    def test_event_inventory_matches_learner_table(self):
        text = (CONTENT / "09.02" / "learner-guide.md").read_text(encoding="utf-8")
        for e in DATA["logic"]["events"]:
            free = "Yes" if e["advertised_free"] else "No"
            row = (
                f"| {e['name']} | {free} | {e['admission']} units | {e['travel']} units | "
                f"{e['seats']} | {e['reservations']} |"
            )
            self.assertIn(row, text)

    def test_default_bias_times_match_learner_table(self):
        text = (CONTENT / "09.03" / "learner-guide.md").read_text(encoding="utf-8")
        for o in DATA["bias"]["default"]["options"]:
            self.assertIn(f"| {o['name']} | {o['travel']} minutes | {o['session']} minutes |", text)
        self.assertIn("70 minutes door-to-door", text)

    def test_fresh_bias_times_match_prompts_and_key(self):
        prompt = (CONTENT / "09.03" / "check-prompts.md").read_text(encoding="utf-8")
        key = (CONTENT / "09.03" / "check-answers.md").read_text(encoding="utf-8")
        for o in DATA["bias"]["fresh"]["options"]:
            self.assertIn(
                f"**{o['name']}:** {o['travel']} minutes round-trip travel "
                f"and {o['session']} minutes",
                prompt,
            )
            self.assertIn(
                f"{o['name']} totals {o['travel']} + {o['session']} "
                f"= {o['travel'] + o['session']}",
                key,
            )

    def test_token_inventory_matches_guide(self):
        text = (CONTENT / "09.02" / "learner-guide.md").read_text(encoding="utf-8")
        for token in DATA["logic"]["tokens"]:
            position = "in drawer" if token["location"] == "drawer" else "on desk"
            self.assertIn(f"{token['id']}: {token['color']}, {position}", text)

    def test_all_canonical_scope_elements_have_traceability(self):
        text = (CONTENT / "SCOPE-MAP.md").read_text(encoding="utf-8").lower()
        for term in (
            "assumptions",
            "stories",
            "emotions",
            "motives",
            "predictions",
            "conclusions",
            "premises",
            "validity",
            "soundness",
            "contradiction",
            "inference",
            "fallacy",
            "burden of proof",
        ):
            self.assertIn(term, text)
        for term in DATA["bias"]["routes"]:
            self.assertIn(term, text)


class BiasCases(unittest.TestCase):
    def test_default_future_totals(self):
        totals = {o["name"]: o["travel"] + o["session"] for o in DATA["bias"]["default"]["options"]}
        self.assertEqual(totals, {"A": 85, "B": 60, "C": 0})

    def test_default_decision_uses_constraints_and_aim(self):
        self.assertEqual(decision(DATA["bias"]["default"]), "B")

    def test_missing_access_is_not_confirmed(self):
        packet = copy.deepcopy(DATA["bias"]["default"])
        packet["options"][1]["access_confirmed"] = None
        self.assertEqual(decision(packet), "home")

    def test_rest_can_change_appropriate_route(self):
        packet = copy.deepcopy(DATA["bias"]["default"])
        packet["needs_rest"] = True
        self.assertEqual(decision(packet), "home")

    def test_swapping_irrelevant_labels_does_not_change_default(self):
        packet = copy.deepcopy(DATA["bias"]["default"])
        packet["options"][0]["group_label"] = "unfamiliar"
        packet["options"][1]["group_label"] = "familiar"
        self.assertEqual(decision(packet), "B")

    def test_irrecoverable_cost_without_future_effect_does_not_change_choice(self):
        packet = copy.deepcopy(DATA["bias"]["default"])
        for o in packet["options"]:
            o["past_irrecoverable"] = 1000000
        self.assertEqual(decision(packet), "B")

    def test_fresh_totals(self):
        totals = {o["name"]: o["travel"] + o["session"] for o in DATA["bias"]["fresh"]["options"]}
        self.assertEqual(totals, {"X": 50, "Y": 55})

    def test_better_procedure_does_not_require_switching(self):
        packet = DATA["bias"]["fresh"]
        self.assertEqual(decision(packet), packet["initial_preference"])
        self.assertEqual(decision(packet), packet["expected"])

    def test_fresh_label_swap_and_past_cost_still_keep_x(self):
        packet = copy.deepcopy(DATA["bias"]["fresh"])
        packet["options"][0]["group_label"] = "familiar"
        packet["options"][1]["group_label"] = "unfamiliar"
        packet["options"][1]["past_irrecoverable"] = 80000
        self.assertEqual(decision(packet), "X")

    def test_worked_future_comparison(self):
        case = DATA["bias"]["worked"]
        self.assertEqual((case["old_remaining"], case["new_remaining"]), (40, 15))
        self.assertLess(case["new_remaining"], case["old_remaining"])

    def test_independent_anchor_calculation(self):
        case = DATA["bias"]["anchor_case"]
        self.assertEqual(case["step_count"] * case["minutes_each"], case["expected_total"])
        self.assertEqual(case["expected_total"], 25)


if __name__ == "__main__":
    unittest.main()
