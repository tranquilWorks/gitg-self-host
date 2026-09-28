"""Executable source-case checks only; no clinical or runtime evidence engine."""

import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/health-foundations"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = ["12.01", "12.02", "12.03", "12.04", "12.06", "12.07"]


def document(competency, name="learner-guide.md"):
    return (SOURCE / competency / name).read_text()


def table_rows(competency, name="learner-guide.md"):
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in document(competency, name).splitlines()
        if line.startswith("|") and "---" not in line
    ]


def minute(clock):
    if not isinstance(clock, str) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", clock):
        raise ValueError("Expected HH:MM")
    hour, minutes = map(int, clock.split(":"))
    if hour > 23 or minutes > 59:
        raise ValueError("Clock out of range")
    return 60 * hour + minutes


def opportunity(start, end):
    duration = (minute(end) - minute(start)) % 1440
    if duration == 0:
        raise ValueError("Equal clocks need explicit dates; not assumed 24 hours")
    return duration


def observed_function(values):
    if any(value not in ("manageable", "difficult", None) for value in values):
        raise ValueError("Unknown function category")
    observed = [value for value in values if value is not None]
    return values.count("manageable"), len(observed), values.count(None)


def care_events(events):
    """Validate only the explicitly ordered events in Morgan's toy packet."""
    prerequisites = {
        "authorized": set(),
        "sent": {"authorized"},
        "acknowledged": {"sent"},
        "received_partial": {"sent"},
        "booked": set(),
    }
    seen = set()
    previous = (0, 0)
    for event, day, at in events:
        if type(day) is not int or day < 1 or type(at) is not int or not 0 <= at < 1440:
            raise ValueError("Invalid case timestamp")
        if event not in prerequisites or event in seen:
            raise ValueError("Unknown or duplicate event")
        if (day, at) < previous or not prerequisites[event] <= seen:
            raise ValueError("Chronology or authorization violation")
        seen.add(event)
        previous = (day, at)
    return seen


def meal(codes, items=None):
    items = FIX["food"]["items"] if items is None else items
    if not codes or len(codes) != len(set(codes)):
        raise ValueError("One defined portion per distinct code required")
    selected = []
    for code in codes:
        if code not in items or items[code]["safety"] != "verified":
            raise ValueError("No verified case suitability")
        item = items[code]
        for key in ("price", "prep", "portions"):
            if type(item[key]) is not int or item[key] < 0:
                raise ValueError("Invalid amount")
        if item["portions"] == 0:
            raise ValueError("Empty package")
        selected.append(item)
    totals = {key: sum(item[key] for item in selected) for key in ("price", "prep")}
    for key in ("protein", "fiber"):
        values = [item[key] for item in selected]
        if any(v is not None and (type(v) is not int or v < 0) for v in values):
            raise ValueError("Invalid nutrient value")
        totals[key] = None if None in values else sum(values)
    return totals


def usable_leftover(elapsed, refrigerated):
    if type(elapsed) is not int or elapsed < 0 or type(refrigerated) is not bool:
        raise ValueError("Need actual nonnegative elapsed time and storage status")
    return refrigerated and elapsed <= FIX["food"]["storage_limit_minutes"]


def aerobic_disposition(session):
    """A deliberately narrow review of Dev's supplied observation cycle."""
    if type(session["actual"]) is not int or not 0 <= session["actual"] <= 6:
        raise ValueError("Actual minutes outside the case plan")
    for key in ("warning", "usual_support"):
        if type(session[key]) is not bool:
            raise ValueError("Unknown safety status cannot become false")
    if session["warning"]:
        return "stop_and_medical_advice"
    if not session["usual_support"]:
        return "restore_conditions_and_review"
    recovery = session["recovery_minutes"]
    if recovery is None or session["later_function"] is None or session["actual"] == 0:
        return "inconclusive"
    if type(recovery) is not int or recovery < 0:
        raise ValueError("Malformed recovery")
    if session["later_function"] != "usual":
        return "review"
    return "repeat_unchanged_inside_plan"


class IdentityAndTeachingTests(unittest.TestCase):
    def test_exact_six_and_no_duplicate_existing_strength(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)

    def test_next_pending_selection_from_actual_contract(self):
        selection = yaml.safe_load(
            (ROOT / "contracts/tailored-practice-authoring.yaml").read_text()
        )
        implemented = set(selection["implemented_competency_ids"])
        self.assertEqual({i for i in implemented if i.startswith("12.")}, {"12.05", "12.08"})
        next_ids = [f"12.{n:02}" for n in range(1, 17) if f"12.{n:02}" not in implemented][:6]
        self.assertEqual(next_ids, IDS)

    def test_complete_canonical_entries_match_current_input(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        domain = next(d for d in catalog["curriculum"]["domains"] if d["id"] == "12")
        self.assertEqual(COHORT["entries"], [c for c in domain["competencies"] if c["id"] in IDS])

    def test_input_byte_pins(self):
        for path, expected in COHORT["input_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_runtime_accounting_and_simulation_flags(self):
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertTrue(COHORT["source_only"])
        self.assertTrue(FIX["synthetic"])
        self.assertFalse(FIX["runtime_evidence"])

    def test_exact_companion_files_per_id(self):
        expected = {
            "learner-guide.md",
            "later-packet.md",
            "check-prompts.md",
            "check-answers.md",
            "SCOPE-MAP.md",
        }
        for competency in IDS:
            self.assertEqual({p.name for p in (SOURCE / competency).iterdir()}, expected)

    def test_three_fresh_checks_have_separate_keys(self):
        for competency in IDS:
            for file in ("check-prompts.md", "check-answers.md"):
                self.assertEqual(
                    re.findall(r"^(\d)\. ", document(competency, file), re.M), ["1", "2", "3"]
                )
            self.assertNotEqual(
                document(competency, "check-prompts.md"), document(competency, "check-answers.md")
            )

    def test_local_learning_links_resolve(self):
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target:
                    self.assertTrue(
                        (path.parent / target.split("#")[0]).resolve().is_file(),
                        f"{path}: {target}",
                    )

    def test_scope_maps_keep_exact_scope_and_progress(self):
        for entry in COHORT["entries"]:
            text = document(entry["id"], "SCOPE-MAP.md")
            for key in ("name", "scope", "evidence_of_progress", "professional_boundary"):
                self.assertIn(entry[key], text)
            self.assertIn(entry["measurement"]["minimum_standard"], text)

    def test_separate_later_reveal_and_evidence_outcomes(self):
        for competency in IDS:
            guide = document(competency)
            self.assertIn("before", guide)
            self.assertIn("later-packet.md", guide)
            for outcome in ("Supportive", "Mixed", "Contradictory", "Inconclusive"):
                self.assertIn(f"**{outcome}:**", guide)

    def test_different_cases_not_repeated_guides(self):
        names = {
            "12.01": "Morgan",
            "12.02": "Lee",
            "12.03": "Ari",
            "12.04": "Rowan",
            "12.06": "Dev",
            "12.07": "Noor",
        }
        for competency, name in names.items():
            self.assertIn(name, document(competency))
            for other in set(names.values()) - {name}:
                self.assertNotRegex(document(competency), rf"\b{other}\b")


class CareSourceTests(unittest.TestCase):
    def test_six_areas_align_with_actual_source_table(self):
        rows = table_rows("12.01")
        self.assertEqual([r[0] for r in rows[1:]], FIX["care"]["areas"])

    def test_partial_record_is_not_interpretation_or_attendance(self):
        events = care_events(FIX["care"]["branches"]["A"])
        self.assertIn("received_partial", events)
        self.assertIn("booked", events)
        self.assertNotIn("interpreted", events)
        self.assertNotIn("attended", events)

    def test_acknowledgement_does_not_supply_record(self):
        events = care_events(FIX["care"]["branches"]["B"])
        self.assertEqual(events, {"authorized", "sent", "acknowledged"})

    def test_care_chronology_rejects_backdating(self):
        events = copy.deepcopy(FIX["care"]["branches"]["A"])
        events[-1][1] = 2
        with self.assertRaises(ValueError):
            care_events(events)

    def test_send_requires_authorization(self):
        with self.assertRaises(ValueError):
            care_events([["sent", 1, 660]])

    def test_received_requires_actual_sent_request_in_this_case(self):
        with self.assertRaises(ValueError):
            care_events([["received_partial", 3, 600]])

    def test_unknown_duplicate_and_malformed_events_fail(self):
        for events in (
            [["interpreted", 1, 0]],
            [["authorized", 1, 0]] * 2,
            [["authorized", True, 0]],
            [["authorized", 1, 1440]],
        ):
            with self.subTest(events=events), self.assertRaises(ValueError):
                care_events(events)

    def test_event_times_align_with_later_source(self):
        later = document("12.01", "later-packet.md")
        for fragment in (
            "Day 1, 11:00",
            "Day 1, 14:00",
            "Day 3, 10:00",
            "Day 3, 15:00",
            "day 8",
            "day 4",
            "not yet made",
        ):
            self.assertIn(fragment, later)
        self.assertEqual(FIX["care"]["followup_day"], 4)
        self.assertEqual(FIX["care"]["appointment_day"], 8)

    def test_permission_and_absent_record_key_regressions(self):
        key = document("12.01", "check-answers.md")
        for fragment in ("uncertain", "not confirmed", "exceed permission", "Withhold both"):
            self.assertIn(fragment, key)


class SleepSourceTests(unittest.TestCase):
    def test_baseline_source_table_matches_fixture(self):
        rows = table_rows("12.02")[1:]
        self.assertEqual(
            [[r[0], *r[1].split("\u2013"), r[2]] for r in rows], FIX["sleep"]["baseline"]
        )

    def test_trial_source_table_matches_fixture(self):
        rows = table_rows("12.02", "later-packet.md")[1:]
        actual = [
            [r[0], *r[1].split("\u2013"), r[2] == "yes", None if r[3] == "missing" else r[3]]
            for r in rows
        ]
        self.assertEqual(actual, FIX["sleep"]["trial"])

    def test_opportunity_arithmetic_and_means(self):
        baseline = [opportunity(r[1], r[2]) for r in FIX["sleep"]["baseline"]]
        trial = [opportunity(r[1], r[2]) for r in FIX["sleep"]["trial"]]
        self.assertEqual(baseline, [480, 450, 480])
        self.assertEqual(trial, [480, 480, 480, 420])
        self.assertEqual(sum(baseline), 1410)
        self.assertEqual(sum(trial), 1860)
        self.assertEqual(sum(trial) / 4 - sum(baseline) / 3, -5)

    def test_missingness_is_separate_from_denominator(self):
        self.assertEqual(observed_function([r[3] for r in FIX["sleep"]["baseline"]]), (2, 3, 0))
        self.assertEqual(observed_function([r[4] for r in FIX["sleep"]["trial"]]), (2, 3, 1))

    def test_all_missing_is_not_success(self):
        self.assertEqual(observed_function([None] * 4), (0, 0, 4))

    def test_sensitivity_can_make_trial_worse(self):
        values = [r[4] for r in FIX["sleep"]["trial"]]
        low = observed_function(["difficult" if v is None else v for v in values])
        high = observed_function(["manageable" if v is None else v for v in values])
        self.assertEqual(low, (2, 4, 0))
        self.assertEqual(high, (3, 4, 0))
        self.assertLess(low[0] / low[1], 2 / 3)

    def test_exposure_does_not_fill_missing_outcome(self):
        rows = FIX["sleep"]["trial"]
        self.assertEqual(sum(r[3] for r in rows), 3)
        self.assertIsNone(rows[2][4])

    def test_malformed_clocks_and_equal_clock_ambiguity(self):
        for clock in ("24:00", "12:60", "7:00", "-1:00", "\uff10\uff17:00", None):
            with self.subTest(clock=clock), self.assertRaises(ValueError):
                minute(clock)
        with self.assertRaises(ValueError):
            opportunity("07:00", "07:00")

    def test_bad_category_is_not_missing_or_good(self):
        with self.assertRaises(ValueError):
            observed_function(["fine"])

    def test_fresh_clock_and_no_restriction_answer(self):
        self.assertEqual(opportunity("22:50", "06:20"), 450)
        self.assertEqual(opportunity("23:20", "06:20"), 420)
        self.assertIn("30-minute reduction", document("12.02", "check-answers.md"))


class NutritionSourceTests(unittest.TestCase):
    def test_prices_and_preparation_match_source_table(self):
        rows = table_rows("12.03")[1:]
        for row in rows:
            item = FIX["food"]["items"][row[0]]
            self.assertIn(f"{item['price'] / 100:.2f}", row[2])
            self.assertEqual(int(re.search(r"\d+", row[3])[0]), item["prep"])
            self.assertIn(f"{item['portions']} portions", row[1])

    def test_known_nutrients_match_source_table(self):
        for row in table_rows("12.03")[1:]:
            item = FIX["food"]["items"][row[0]]
            if item["protein"] is not None:
                self.assertIn(f"protein {item['protein']} g", row[4].lower())
                self.assertIn(f"fiber {item['fiber']} g", row[4].lower())

    def test_default_whole_package_budget_and_time(self):
        totals = meal(FIX["food"]["default"])
        self.assertEqual((totals["price"], totals["prep"]), (700, 7))
        self.assertLessEqual(totals["price"], FIX["food"]["budget_cents"])
        self.assertLessEqual(totals["prep"], FIX["food"]["prep_limit_minutes"])

    def test_known_subtotal_is_not_full_meal_total(self):
        known = meal(["R", "B", "V", "O"])
        self.assertEqual((known["protein"], known["fiber"]), (10, 8))
        complete = meal(FIX["food"]["default"])
        self.assertIsNone(complete["protein"])
        self.assertIsNone(complete["fiber"])

    def test_alternate_is_feasible_but_nutrients_unknown(self):
        alternate = meal(FIX["food"]["alternate"])
        self.assertEqual((alternate["price"], alternate["prep"]), (740, 7))
        self.assertIsNone(alternate["protein"])
        self.assertIsNone(alternate["fiber"])

    def test_allergen_and_unknown_each_block_selection(self):
        self.assertNotEqual(
            FIX["food"]["items"]["S"]["safety"], FIX["food"]["items"]["U"]["safety"]
        )
        for code in ("S", "U", "missing"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                meal(["R", code])

    def test_duplicate_and_empty_meals_rejected(self):
        for codes in ([], ["R", "R"]):
            with self.assertRaises(ValueError):
                meal(codes)

    def test_bad_prices_quantities_and_nutrients_rejected(self):
        for key, value in (
            ("price", -1),
            ("prep", True),
            ("portions", 0),
            ("protein", "7"),
            ("fiber", -2),
        ):
            items = copy.deepcopy(FIX["food"]["items"])
            items["R"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                meal(["R"], items)

    def test_toy_storage_boundary_inclusive_and_conditions_required(self):
        self.assertTrue(usable_leftover(1440, True))
        self.assertFalse(usable_leftover(1441, True))
        self.assertFalse(usable_leftover(10, False))
        for elapsed, stored in ((-1, True), (None, True), (True, True), (1, None)):
            with self.assertRaises(ValueError):
                usable_leftover(elapsed, stored)

    def test_actual_repeat_elapsed_times(self):
        repeats = FIX["food"]["repeat_minutes"]
        self.assertTrue(usable_leftover(repeats["A"], True))
        self.assertFalse(usable_leftover(repeats["B"], True))
        self.assertEqual(repeats["A"], 24 * 60 - 10)
        self.assertEqual(repeats["B"], 24 * 60 + 30)

    def test_failed_repeat_cannot_spend_same_money_twice(self):
        remaining = FIX["food"]["budget_cents"] - meal(FIX["food"]["default"])["price"]
        replacement = meal(["R", "B", "V"])["price"]
        self.assertEqual((remaining, replacement), (100, 600))
        self.assertGreater(replacement, remaining)

    def test_fresh_label_quantity_and_cash_key(self):
        self.assertEqual((2 * 4, 2 * 2), (8, 4))
        key = document("12.03", "check-answers.md")
        for fragment in (
            "8 g protein",
            "4 g fiber",
            "3.60",
            "2.40",
            "not a portion recommendation",
        ):
            self.assertIn(fragment, key)


class BodyCareSourceTests(unittest.TestCase):
    def test_meal_can_occur_without_positive_feelings(self):
        for branch in FIX["body"].values():
            self.assertEqual(branch["meal"], "occurred")
            self.assertEqual(branch["feelings"], "uncomfortable")

    def test_draft_does_not_become_response_or_care(self):
        branch = FIX["body"]["B"]
        self.assertEqual(branch["message"], "drafted")
        self.assertFalse(branch["response"])
        self.assertFalse(branch["qualified_contact"])

    def test_later_record_preserves_unresolved_interference(self):
        later = document("12.04", "later-packet.md")
        for fragment in (
            "feelings remain",
            "does not send",
            "no qualified contact",
            "repeatedly interferes",
        ):
            self.assertIn(fragment, later)
        self.assertEqual(FIX["body"]["B"]["interference"], "repeated")

    def test_garment_route_has_favorable_and_unfavorable_outcomes(self):
        guide = document("12.04")
        self.assertIn("shirt changed and comfort improved", guide)
        self.assertIn("shirt changed but discomfort persisted", guide)

    def test_help_not_denied_by_appearance(self):
        key = document("12.04", "check-answers.md")
        self.assertIn("Appearance does not establish health", key)
        self.assertIn("not sent", key)

    def test_preference_not_conditional_care(self):
        key = document("12.04", "check-answers.md")
        self.assertIn("style preference can coexist", key)
        self.assertIn("compulsory body positivity", key)


class AerobicSourceTests(unittest.TestCase):
    def test_loop_fits_including_return_but_alternate_does_not(self):
        case = FIX["aerobic"]
        self.assertEqual(case["loop_minutes"] * case["loops"], case["limit"])
        self.assertEqual(case["outbound"] + case["return"], 8)
        self.assertGreater(case["outbound"] + case["return"], case["limit"])

    def test_actual_stopped_work_is_not_target_completion(self):
        actual = sum(s["actual"] for s in FIX["aerobic"]["sessions"])
        self.assertEqual(actual, 10)
        self.assertNotEqual(actual, 2 * FIX["aerobic"]["limit"])
        self.assertIn("6 + 4 = 10", document("12.06", "later-packet.md"))

    def test_ordinary_first_session_permits_repeat_not_progress(self):
        self.assertEqual(
            aerobic_disposition(FIX["aerobic"]["sessions"][0]), "repeat_unchanged_inside_plan"
        )

    def test_warning_overrides_target_and_missing_recovery(self):
        second = FIX["aerobic"]["sessions"][1]
        self.assertEqual(aerobic_disposition(second), "stop_and_medical_advice")
        self.assertIsNone(second["recovery_minutes"])
        self.assertFalse(FIX["aerobic"]["clearance_to_resume"])

    def test_missing_recovery_does_not_mean_no_burden(self):
        session = dict(FIX["aerobic"]["sessions"][0], recovery_minutes=None)
        self.assertEqual(aerobic_disposition(session), "inconclusive")

    def test_changed_assistance_blocks_comparison(self):
        session = dict(FIX["aerobic"]["sessions"][0], usual_support=False)
        self.assertEqual(aerobic_disposition(session), "restore_conditions_and_review")

    def test_zero_attempt_or_missing_later_function_inconclusive(self):
        for changes in ({"actual": 0}, {"later_function": None}):
            self.assertEqual(
                aerobic_disposition(dict(FIX["aerobic"]["sessions"][0], **changes)), "inconclusive"
            )

    def test_delayed_worse_function_requires_review(self):
        session = dict(FIX["aerobic"]["sessions"][0], later_function="worse")
        self.assertEqual(aerobic_disposition(session), "review")

    def test_bad_or_unknown_data_cannot_become_clearance(self):
        for changes in (
            {"actual": -1},
            {"actual": 7},
            {"actual": True},
            {"warning": None},
            {"usual_support": "yes"},
            {"recovery_minutes": -1},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                aerobic_disposition(dict(FIX["aerobic"]["sessions"][0], **changes))

    def test_fresh_route_and_existing_help_boundary(self):
        self.assertEqual(6 + 6 - 10, 2)
        key = document("12.06", "check-answers.md")
        self.assertIn("12 minutes", key)
        self.assertIn("Do not invent clearance", key)
        self.assertIn("no automatic graded increase", document("12.06"))


class MobilitySourceTests(unittest.TestCase):
    def test_source_geometry_matches_fixture(self):
        rows = table_rows("12.07")[1:]
        for row, code in zip(rows, ("A", "B", "C"), strict=True):
            x, y, _ = FIX["mobility"]["arrangements"][code]
            self.assertEqual((row[1], row[2]), (f"{x} cm", f"{y} cm"))

    def test_closer_shelf_changes_one_dimension(self):
        a, b = (FIX["mobility"]["arrangements"][k] for k in ("A", "B"))
        self.assertEqual((a[0] - b[0], a[1] - b[1]), (10, 0))

    def test_unfamiliar_shelf_not_attempted(self):
        self.assertIsNone(FIX["mobility"]["arrangements"]["C"][2])
        self.assertFalse(FIX["mobility"]["C_attempted"])
        self.assertIn("C is never attempted", document("12.07", "later-packet.md"))

    def test_all_four_initial_criteria_but_not_repeat(self):
        case = FIX["mobility"]
        self.assertEqual(len(case["criteria"]), 4)
        for key in ("initial_A", "initial_B"):
            self.assertEqual(case[key], [True] * 4)
        self.assertEqual(case["repeat_B"].count(True), 3)
        self.assertIsNone(case["repeat_B"][3])
        self.assertTrue(case["grip_fatigue"])

    def test_unknown_is_not_fourth_pass_in_source(self):
        later = document("12.07", "later-packet.md")
        self.assertIn("not four passes", later)
        self.assertIn("later recovery are unknown", later)

    def test_geometry_is_not_personal_range_change(self):
        self.assertEqual(40 - 28, 12)
        key = document("12.07", "check-answers.md")
        self.assertIn("decreased by 12 cm", key)
        self.assertIn("not a measured change", key)

    def test_no_required_unsafe_baseline_attempt(self):
        key = document("12.07", "check-answers.md")
        self.assertIn("Do not repeat a now-unsafe task", key)
        self.assertIn("Support and object load changed", key)


if __name__ == "__main__":
    unittest.main()
