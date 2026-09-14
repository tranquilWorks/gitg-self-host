"""Check six original source cases; helpers are not clinical/runtime evaluators."""

import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/health-stewardship"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"12.{n:02}" for n in range(9, 15)]


def document(competency, name="learner-guide.md"):
    return (SOURCE / competency / name).read_text()


def rows(competency, name="learner-guide.md"):
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in document(competency, name).splitlines()
        if line.startswith("|") and "---" not in line
    ]


def minute(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        raise ValueError("Expected ASCII HH:MM")
    hour, mins = map(int, value.split(":"))
    if hour > 23 or mins > 59:
        raise ValueError("Clock outside one case day")
    return hour * 60 + mins


def nonnegative(value):
    if type(value) is not int or value < 0:
        raise ValueError("Expected nonnegative integer, not missing or Boolean")
    return value


def task_comparison(first, second):
    times = [nonnegative(item["seconds"]) for item in (first, second)]
    for item in (first, second):
        if nonnegative(item["books"]) == 0 or times.count(0):
            raise ValueError("No completed case task")
    same = all(
        first[key] is not None and first[key] == second[key]
        for key in ("books", "route", "aid", "helper")
    )
    return {"seconds_quicker": times[0] - times[1], "comparable": same}


def weekly_minutes(duration, count):
    return nonnegative(duration) * nonnegative(count)


def return_status(record):
    """Only Jules's fictional advice/function statuses, never medical clearance."""
    if record["advice"] not in ("acknowledged", "individual_plan_received", None):
        raise ValueError("Unknown advice status")
    if record["function"] not in ("usual", "different", None):
        raise ValueError("Unknown function status")
    if type(record["return_performed"]) is not bool:
        raise ValueError("Return action unknown")
    if record["return_performed"]:
        return "performed_record_needs_its_own_review"
    if record["function"] == "usual" and record["advice"] == "individual_plan_received":
        return "planned_inside_received_guidance"
    return "unresolved_no_return_claim"


def ride_fits(option, now, wait_end, funds):
    funds = nonnegative(funds)
    cost = nonnegative(option["cost"])
    if not all(option[key] is True for key in ("confirmed", "driver_suitable", "accessible")):
        return False
    if option["pickup"] is None:
        return False
    return minute(now) <= minute(option["pickup"]) <= minute(wait_end) and cost <= funds


def permission_trace(events):
    """Current scope-specific permissions in the voluntary fictional greeting."""
    current = {"handshake": False, "photo": False, "publish": False, "share_reason": False}
    last = -1
    for event in events:
        at = minute(event["time"])
        if at < last or event["action"] not in current:
            raise ValueError("Invalid chronology or permission scope")
        if event["choice"] not in ("yes", "no", "unknown", "withdraw"):
            raise ValueError("Unknown choice does not default to yes")
        current[event["action"]] = event["choice"] == "yes"
        last = at
    return current


def schedule_minutes(tasks):
    previous_end = None
    total = 0
    for start, end, duration in tasks:
        a, b = minute(start), minute(end)
        if b <= a or b - a != nonnegative(duration):
            raise ValueError("Invalid interval/duration")
        if previous_end is not None and a != previous_end:
            raise ValueError("Case schedule needs contiguous, nonoverlapping intervals")
        total += duration
        previous_end = b
    return total


def count_opportunities(records):
    done = 0
    movement = 0
    for record in records:
        if type(record["performed"]) is not bool:
            raise ValueError("Unknown attempt cannot count as completed")
        amount = nonnegative(record["movement_minutes"])
        if record["performed"]:
            if record["return_confirmed"] is not True or amount != 8:
                raise ValueError(
                    "Completed Lian case outing must retain its actual return and dose"
                )
            done += 1
            movement += amount
        elif amount:
            raise ValueError("Unperformed case outing cannot contain completed movement")
    return done, len(records), movement


class IdentityAndSourceTests(unittest.TestCase):
    def test_active_contract_is_valid_and_source_scoped(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertIsInstance(contract["batch"]["id"], str)
        self.assertTrue(all(isinstance(item, str) for item in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-HEALTH-STEWARDSHIP-SIX":
            self.assertIn("data/**", contract["scope"]["forbidden_paths"])
            self.assertIn(".github/**", contract["scope"]["forbidden_paths"])

    def test_exact_six_folder_identity(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)

    def test_selection_is_next_pending_after_prior_companions(self):
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        covered = set(contract["implemented_competency_ids"])
        for path in (ROOT / "docs/authoring").glob("*/cohort.json"):
            if path.parent != SOURCE:
                covered.update(json.loads(path.read_text()).get("ids", []))
        pending = [f"12.{n:02}" for n in range(1, 17) if f"12.{n:02}" not in covered]
        self.assertEqual(pending[:6], IDS)

    def test_complete_canonical_entries_equal_input(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        domain = next(d for d in catalog["curriculum"]["domains"] if d["id"] == "12")
        self.assertEqual(COHORT["entries"], [e for e in domain["competencies"] if e["id"] in IDS])

    def test_byte_pinned_inputs_and_frozen_boundary(self):
        for path, digest in COHORT["input_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_runtime_and_simulation_accounting(self):
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertTrue(COHORT["source_only"])
        self.assertTrue(FIX["synthetic"])
        self.assertFalse(FIX["runtime_evidence"])

    def test_exact_learning_files_and_three_fresh_checks(self):
        names = {
            "learner-guide.md",
            "later-packet.md",
            "check-prompts.md",
            "check-answers.md",
            "SCOPE-MAP.md",
        }
        for competency in IDS:
            self.assertEqual({p.name for p in (SOURCE / competency).iterdir()}, names)
            for name in ("check-prompts.md", "check-answers.md"):
                self.assertEqual(
                    re.findall(r"^(\d)\. ", document(competency, name), re.M), ["1", "2", "3"]
                )

    def test_learning_links_resolve(self):
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target:
                    self.assertTrue(
                        (path.parent / target.split("#")[0]).resolve().is_file(),
                        f"{path}: {target}",
                    )

    def test_scope_and_measurement_exact_in_maps(self):
        for entry in COHORT["entries"]:
            scope = document(entry["id"], "SCOPE-MAP.md")
            for key in ("name", "scope", "evidence_of_progress", "professional_boundary"):
                self.assertIn(entry[key], scope)
            self.assertIn(entry["measurement"]["minimum_standard"], scope)

    def test_later_reveal_and_all_four_outcomes(self):
        for competency in IDS:
            guide = document(competency)
            self.assertIn("before", guide)
            self.assertIn("later-packet.md", guide)
            for outcome in ("Supportive", "Mixed", "Contradictory", "Inconclusive"):
                self.assertIn(f"**{outcome}:**", guide)

    def test_individual_case_identities_and_distinct_operations(self):
        cases = {
            "12.09": "Ellis",
            "12.10": "Jules",
            "12.11": "Remy",
            "12.12": "Sasha",
            "12.13": "Amari",
            "12.14": "Lian",
        }
        for competency, person in cases.items():
            self.assertIn(person, document(competency))
            for other in set(cases.values()) - {person}:
                self.assertNotRegex(document(competency), rf"\b{other}\b")


class CompositionTests(unittest.TestCase):
    def test_source_table_matches_task_and_unknowns(self):
        table = {r[0]: r[1:] for r in rows("12.09")[1:]}
        tasks = FIX["composition"]["tasks"]
        self.assertEqual(
            table["Book-group task"][:2], [f"{t['seconds']} seconds" for t in tasks[:2]]
        )
        self.assertEqual(table["Muscle/fat composition"][:2], ["not measured"] * 2)
        self.assertEqual(table["Waist"][:2], ["not recorded"] * 2)

    def test_comparable_task_has_twenty_second_change(self):
        a, b, _ = FIX["composition"]["tasks"]
        self.assertEqual(task_comparison(a, b), {"seconds_quicker": 20, "comparable": True})

    def test_helper_and_load_change_breaks_same_task_trend(self):
        _, b, c = FIX["composition"]["tasks"]
        self.assertEqual(task_comparison(b, c), {"seconds_quicker": 5, "comparable": False})
        self.assertIn("95 seconds", document("12.09", "later-packet.md"))
        self.assertIn("helper carries one", document("12.09", "later-packet.md"))

    def test_unchanged_total_does_not_supply_tissues(self):
        case = FIX["composition"]
        self.assertEqual(case["scale"], "unchanged")
        self.assertFalse(case["tissue_measured"])
        self.assertFalse(case["waist_measured"])
        self.assertTrue(case["garment_stretched"])

    def test_negative_and_zero_attempts_rejected(self):
        a, b, _ = FIX["composition"]["tasks"]
        for changes in ({"seconds": -1}, {"seconds": 0}, {"seconds": True}, {"books": 0}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                task_comparison(a, dict(b, **changes))

    def test_unknown_conditions_and_worse_time_remain_possible(self):
        a, b, _ = FIX["composition"]["tasks"]
        changed = dict(b, route=None, seconds=140)
        self.assertEqual(task_comparison(a, changed), {"seconds_quicker": -20, "comparable": False})

    def test_booked_and_attended_care_branches_separate(self):
        self.assertNotIn("review_attended", FIX["composition"]["care_main"])
        self.assertIn("review_attended", FIX["composition"]["care_alternative"])
        self.assertNotIn("followup_attended", FIX["composition"]["care_alternative"])
        self.assertIn("next review has not occurred", document("12.09", "later-packet.md"))

    def test_fresh_comparison_keys_keep_both_twenty_second_differences(self):
        self.assertEqual((150 - 130, 130 - 110), (20, 20))
        key = document("12.09", "check-answers.md")
        self.assertIn("Both successive differences are 20 seconds", key)
        self.assertIn("not attended or interpreted", key)


class RecoveryTests(unittest.TestCase):
    def test_source_duration_frequency_match_fixture(self):
        table = {r[0]: r[1:] for r in rows("12.10")[1:]}
        for column, key in enumerate(("previous", "changed")):
            duration, count = FIX["recovery"][key]
            self.assertEqual(table["Session duration"][column], f"{duration} minutes")
            self.assertEqual(table["Sessions performed"][column], str(count))

    def test_weekly_minutes_double_without_intensity_claim(self):
        case = FIX["recovery"]
        old, new = (weekly_minutes(*case[k]) for k in ("previous", "changed"))
        self.assertEqual((old, new, new - old), (60, 120, 60))
        self.assertEqual((new - old) * 100 / old, 100)
        self.assertIsNone(case["intensity"])

    def test_zero_sessions_are_not_completed_work(self):
        self.assertEqual(weekly_minutes(30, 0), 0)

    def test_malformed_load_rejected(self):
        for duration, count in ((-1, 3), (20, -1), (True, 3), (None, 3), (20, 2.5)):
            with self.assertRaises(ValueError):
                weekly_minutes(duration, count)

    def test_better_fatigue_does_not_override_different_function(self):
        record = FIX["recovery"]["main"]
        self.assertEqual(record["fatigue"], "less")
        self.assertEqual(return_status(record), "unresolved_no_return_claim")

    def test_received_plan_is_not_performed_return(self):
        record = FIX["recovery"]["alternative"]
        self.assertEqual(return_status(record), "planned_inside_received_guidance")
        self.assertFalse(record["return_performed"])

    def test_missing_advice_or_function_withholds_planned_return(self):
        for key in ("advice", "function"):
            record = dict(FIX["recovery"]["alternative"], **{key: None})
            self.assertEqual(return_status(record), "unresolved_no_return_claim")

    def test_unrecognized_status_not_favorable(self):
        for key, value in (
            ("function", "good"),
            ("advice", "probably fine"),
            ("return_performed", None),
        ):
            with self.assertRaises(ValueError):
                return_status(dict(FIX["recovery"]["main"], **{key: value}))

    def test_fresh_fifty_to_ninety_calculation_matches_key(self):
        old, new = weekly_minutes(25, 2), weekly_minutes(30, 3)
        self.assertEqual((old, new, new - old, (new - old) * 100 / old), (50, 90, 40, 80))
        self.assertIn("40 minutes or 80%", document("12.10", "check-answers.md"))


class SubstanceTests(unittest.TestCase):
    def test_all_five_categories_present(self):
        category_rows = rows("12.11")[:6]
        self.assertEqual(
            [r[0] for r in category_rows[1:]],
            [
                "Alcohol",
                "Nicotine",
                "Recreational substances",
                "Performance drugs",
                "Prescription/nonprescription medicines",
            ],
        )

    def test_only_confirmed_suitable_affordable_ride_fits(self):
        case = FIX["substances"]
        fits = [
            k
            for k, option in case["options"].items()
            if ride_fits(option, case["now"], case["wait_end"], case["funds"])
        ]
        self.assertEqual(fits, ["C"])

    def test_pickup_and_arrival_match_source(self):
        case = FIX["substances"]
        pickup = minute(case["options"]["C"]["pickup"])
        self.assertEqual(minute(case["wait_end"]) - pickup, 10)
        self.assertEqual(pickup + case["journey_minutes"], minute("21:00"))
        self.assertIn("confirmed 20:50 pickup", document("12.11"))
        self.assertIn("arrival is confirmed at 21:00", document("12.11", "later-packet.md"))

    def test_late_pickup_breaks_waiting_plan(self):
        case = FIX["substances"]
        late = dict(case["options"]["C"], pickup=case["delay_pickup"])
        self.assertFalse(ride_fits(late, case["now"], case["wait_end"], case["funds"]))
        self.assertEqual(minute(late["pickup"]) - minute(case["wait_end"]), 10)

    def test_no_alcohol_does_not_erase_current_impairment(self):
        self.assertFalse(FIX["substances"]["alcohol_consumed"])
        self.assertTrue(FIX["substances"]["impaired"])
        self.assertFalse(FIX["substances"]["qualified_reply"])

    def test_unknown_confirmation_suitability_or_access_fails(self):
        case = FIX["substances"]
        for key in ("confirmed", "driver_suitable", "accessible"):
            option = dict(case["options"]["C"], **{key: None})
            self.assertFalse(ride_fits(option, case["now"], case["wait_end"], 0))

    def test_wait_boundary_and_funds_are_not_guessed(self):
        case = FIX["substances"]
        option = dict(case["options"]["C"], pickup="21:00")
        self.assertTrue(ride_fits(option, "20:30", "21:00", 0))
        self.assertFalse(ride_fits(dict(option, pickup="21:01"), "20:30", "21:00", 0))
        self.assertFalse(ride_fits(dict(option, cost=1), "20:30", "21:00", 0))
        with self.assertRaises(ValueError):
            ride_fits(option, "20:30", "21:00", None)

    def test_dependence_and_emergency_routes_preserved(self):
        key = document("12.11", "check-answers.md")
        self.assertIn("medical support before a sudden reduction or stop", key)
        self.assertIn("emergency care", key)
        self.assertIn("do not test the product", key)

    def test_fresh_pickup_gap_and_arrival(self):
        self.assertEqual(minute("20:10") - minute("20:00"), 10)
        self.assertEqual(minute("20:10") + 15, minute("20:25"))
        self.assertIn("20:25", document("12.11", "check-answers.md"))


class ConsentTests(unittest.TestCase):
    def test_starting_choices_include_unknown_and_reciprocal_no(self):
        table = rows("12.12")[1:]
        self.assertEqual([r[0] for r in table], ["W", "U", "T"])
        self.assertIn("No touch permission", table[1][2])
        self.assertIn("no-touch boundary stands", table[2][2])

    def test_withdrawal_and_unclear_photo_end_with_no_touch_or_photo(self):
        result = permission_trace(FIX["consent"]["A"])
        self.assertFalse(any(result.values()))

    def test_earlier_yes_exists_but_does_not_persist_after_withdrawal(self):
        events = FIX["consent"]["A"]
        self.assertTrue(permission_trace(events[:1])["handshake"])
        self.assertFalse(permission_trace(events[:2])["handshake"])

    def test_private_photo_does_not_transfer_to_publication(self):
        result = permission_trace([{"time": "10:00", "action": "photo", "choice": "yes"}])
        self.assertTrue(result["photo"])
        self.assertFalse(result["publish"])
        self.assertFalse(result["share_reason"])

    def test_unknown_or_no_are_never_yes(self):
        for choice in ("no", "unknown", "withdraw"):
            result = permission_trace([{"time": "10:00", "action": "handshake", "choice": choice}])
            self.assertFalse(result["handshake"])

    def test_backdated_unknown_scope_and_bad_choice_fail(self):
        cases = [
            list(reversed(FIX["consent"]["A"])),
            [{"time": "10:00", "action": "all", "choice": "yes"}],
            [{"time": "10:00", "action": "photo", "choice": True}],
        ]
        for events in cases:
            with self.assertRaises(ValueError):
                permission_trace(events)

    def test_overstep_and_repair_do_not_invent_forgiveness(self):
        branch = FIX["consent"]["B"]
        self.assertTrue(branch["overstep"])
        self.assertTrue(branch["stopped"] and branch["space_respected"])
        self.assertIsNone(branch["forgiveness"])
        self.assertFalse(branch["renewed_permission"])
        self.assertIn("overstep occurred", document("12.12", "later-packet.md"))

    def test_supported_communication_preserves_scope(self):
        branch = FIX["consent"]["C"]
        self.assertTrue(branch["read_card_permission"])
        self.assertFalse(branch["share_reason_permission"])
        self.assertIn("no permission to share why", document("12.12", "later-packet.md"))

    def test_medical_questions_and_frozen_runtime_are_separate(self):
        guide = document("12.12")
        self.assertIn("produce four questions", guide)
        self.assertIn("frozen 11.10 boundary protocol", guide)
        self.assertIn("does not determine medical capacity", document("12.12", "check-answers.md"))


class PresentationTests(unittest.TestCase):
    def test_all_item_options_are_inspectable(self):
        table = rows("12.13")[:7]
        self.assertEqual([r[0].split(",")[0] for r in table[1:]], ["A", "B", "C", "D", "L", "I"])
        self.assertIn("30-minute wash", table[3][1])

    def test_actual_timetable_matches_fixture(self):
        times = [
            r
            for r in rows("12.13")
            if re.fullmatch(r"[0-9]{2}:[0-9]{2}\u2013[0-9]{2}:[0-9]{2}", r[0])
        ]
        actual = [[*r[0].split("\u2013"), int(r[2])] for r in times]
        self.assertEqual(actual, FIX["presentation"]["tasks"])
        self.assertEqual(schedule_minutes(actual), 20)

    def test_reserve_consumed_once_and_harder_delay_preserved(self):
        case = FIX["presentation"]
        self.assertEqual(case["reserve"] - case["correction"], 0)
        self.assertEqual(case["harder_correction"] - case["reserve"], 1)
        self.assertEqual(minute("13:53") + case["travel"], minute("14:01"))

    def test_layer_removed_while_identity_and_aid_retained(self):
        case = FIX["presentation"]
        self.assertEqual(set(case["initial_items"]) - set(case["final_items"]), {"L"})
        self.assertIn("I", case["final_items"])
        self.assertTrue(case["aid_retained"])
        self.assertFalse(case["layer_reach"])
        self.assertTrue(case["shirt_reach"])

    def test_movement_and_warmth_are_separate_followup_facts(self):
        self.assertTrue(FIX["presentation"]["warm_seat_confirmed"])
        later = document("12.13", "later-packet.md")
        self.assertIn("room feels cooler", later)
        self.assertIn("warmer accessible seat", later)
        self.assertIn("No compliment is recorded", later)

    def test_long_wash_does_not_fit_predeparture_time(self):
        available = minute("13:52") - minute("13:40")
        self.assertEqual(available, 12)
        self.assertGreater(FIX["presentation"]["wash_C"], available)
        self.assertEqual(FIX["presentation"]["cost"], 0)

    def test_overlap_gap_or_wrong_duration_rejected(self):
        for index, value in ((0, "13:47"), (0, "13:49"), (2, 2)):
            tasks = copy.deepcopy(FIX["presentation"]["tasks"])
            tasks[3][index] = value
            with self.assertRaises(ValueError):
                schedule_minutes(tasks)

    def test_clock_rejects_invalid_or_unicode_digits(self):
        for value in ("24:00", "12:60", "2:00", None, "\uff11\uff13:00"):
            with self.assertRaises(ValueError):
                minute(value)

    def test_fresh_reserve_correction_and_requirement_key(self):
        self.assertEqual(3 - 2, 1)
        key = document("12.13", "check-answers.md")
        self.assertIn("adds 1 minute", key)
        self.assertIn("Neither added scent nor brand is a verified requirement", key)


class LifelongMovementTests(unittest.TestCase):
    def test_whole_function_map_matches_fixture(self):
        self.assertEqual([r[0] for r in rows("12.14")[1:]], FIX["lifelong"]["functions"])

    def test_round_trip_fits_but_waiting_is_not_movement(self):
        case = FIX["lifelong"]
        movement = case["outbound_movement"] + case["return_movement"]
        self.assertEqual(movement, case["limit"])
        self.assertEqual(movement + case["conversation"] + case["wait"], 30)
        self.assertEqual(minute("10:00") + 30, minute(case["pickup"]))

    def test_transfer_time_and_boarding_are_explicit(self):
        guide = document("12.14")
        later = document("12.14", "later-packet.md")
        self.assertIn("Each four-minute segment includes", guide)
        self.assertIn("Each four-minute segment includes", later)
        self.assertIn("not silently assigned zero physical effort", guide)
        self.assertIn("before pickup begins", later)

    def test_main_branch_one_performed_of_two_planned(self):
        case = FIX["lifelong"]
        self.assertEqual(count_opportunities([case["first"], case["second"]]), (1, 2, 8))

    def test_supportive_branch_two_only_with_second_actual_opportunity(self):
        first = FIX["lifelong"]["first"]
        self.assertEqual(count_opportunities([first, dict(first)]), (2, 2, 16))
        self.assertIn("replace opportunity 2", document("12.14", "later-packet.md"))

    def test_cancelled_return_is_not_completed_outing(self):
        second = dict(FIX["lifelong"]["second"], performed=True, movement_minutes=8)
        with self.assertRaises(ValueError):
            count_opportunities([second])

    def test_unperformed_or_unknown_cannot_gain_minutes(self):
        for changes in ({"movement_minutes": 8}, {"performed": None}, {"movement_minutes": True}):
            with self.assertRaises(ValueError):
                count_opportunities([dict(FIX["lifelong"]["second"], **changes)])

    def test_home_alternative_not_agreed_or_completed(self):
        self.assertEqual(FIX["lifelong"]["home_alternative"], "proposed")
        later = document("12.14", "later-packet.md")
        self.assertIn("no time is agreed", later)
        self.assertIn("no conversation has occurred", later)

    def test_recurrence_preserves_earlier_change_trigger(self):
        guide = document("12.14")
        self.assertIn("Review in one month or sooner", guide)
        self.assertIn("health, ordinary function, recovery, transport, environment", guide)
        self.assertIn("No movement is needed for the default", guide)

    def test_fresh_return_shortfall_not_cancelled_by_sitting(self):
        self.assertEqual(6 + 6 - 10, 2)
        key = document("12.14", "check-answers.md")
        self.assertIn("exceeding the limit by 2", key)
        self.assertIn("not negative movement time", key)


if __name__ == "__main__":
    unittest.main()
