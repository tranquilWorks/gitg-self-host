"""Integrity and supplied-case checks; these do not grade learners or runtime evidence."""

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/life-integration"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
CASES = FIX["cases"]
IDS = [f"27.{i:02}" for i in range(3, 15)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


def minute(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        raise ValueError("Expected HH:MM")
    hour, mins = map(int, value.split(":"))
    if hour > 23 or mins > 59:
        raise ValueError("Invalid clock time")
    return hour * 60 + mins


def table(cid):
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in doc(cid).splitlines()
        if line.startswith("|") and "---" not in line
    ][1:]


class IntegrityTests(unittest.TestCase):
    def test_exact_ids_files_and_runtime_boundary(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        for cid in IDS:
            self.assertEqual(
                {p.name for p in (SOURCE / cid).iterdir()},
                {
                    "learner-guide.md",
                    "later-packet.md",
                    "check-prompts.md",
                    "check-answers.md",
                    "SCOPE-MAP.md",
                },
            )
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(COHORT["reporting_cadence"], 12)

    def test_canonical_entries_and_four_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        self.assertEqual(
            COHORT["entries"],
            [
                e
                for d in catalog["curriculum"]["domains"]
                for e in d["competencies"]
                if e["id"] in IDS
            ],
        )
        self.assertEqual(len(COHORT["input_sha256"]), 4)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_current_recovery_inputs_remain_equal(self):
        for domain in ("27",):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            self.assertEqual(current, recovery)
            for cid in (x for x in IDS if x.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_individual_scope_maps_preserve_metadata(self):
        for entry in COHORT["entries"]:
            scope = doc(entry["id"], "SCOPE-MAP.md")
            for key in ("name", "scope", "evidence_of_progress"):
                self.assertIn(entry[key], scope)
            for value in entry["classification"].values():
                for item in value if isinstance(value, list) else [value]:
                    self.assertIn(item, scope)
            for item in entry["measurement"]["preferred_evidence_types"]:
                self.assertIn(item, scope)
            self.assertIn(entry["measurement"]["minimum_standard"], scope)
            self.assertIn("not a new exercise scoring rule", scope)
            self.assertIn("Human dignity is never scored", scope)

    def test_classification_modes_and_absent_boundary(self):
        for entry in COHORT["entries"]:
            self.assertNotIn("professional_boundary", entry)
            self.assertEqual(entry["classification"]["applicability"], "cross_context_core")
            self.assertEqual(
                entry["classification"]["normative_status"],
                "cross_tradition_core_or_broadly_recurrent",
            )
            expected = (
                ["receptivity", "interdependence", "transcendence"]
                if entry["id"].startswith("26.")
                else ["agency", "receptivity", "interdependence", "stewardship"]
            )
            self.assertEqual(entry["classification"]["formation_modes"], expected)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                (self.assertNotIn if name == "learner-guide.md" else self.assertIn)(
                    "no professional_boundary field", doc(entry["id"], name)
                )

    def test_source_coverage_is_disjoint_and_complete(self):
        cov = COHORT["source_coverage"]
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        canonical = {e["id"] for d in catalog["curriculum"]["domains"] for e in d["competencies"]}
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        implemented = set(contract["implemented_competency_ids"])
        paths = cov["prior_companion_guides"]
        directories = {str(Path(p).parent.parent) for p in paths}
        actual = {
            str(p.relative_to(ROOT))
            for d in directories
            for p in (ROOT / d).glob("*/learner-guide.md")
        }
        self.assertEqual(set(paths), actual)
        prior = [Path(p).parent.name for p in paths]
        self.assertEqual(len(prior), len(set(prior)))
        self.assertEqual(len(prior), 237)
        self.assertEqual(sorted(prior), cov["prior_companion_ids"])
        self.assertEqual(sorted(implemented), cov["implemented_ids"])
        self.assertFalse(implemented & set(prior))
        self.assertFalse((implemented | set(prior)) & set(IDS))
        covered = implemented | set(prior) | set(IDS)
        self.assertEqual(len(covered), 357)
        self.assertEqual(cov["covered_count"], 357)
        self.assertEqual(sorted(canonical - covered), cov["remaining_ids"])
        self.assertEqual(cov["remaining_count"], 26)
        self.assertEqual(
            dict(Counter(cid[:2] for cid in canonical - covered)), {"07": 14, "08": 11, "27": 1}
        )
        self.assertEqual(cov["remaining_by_domain"], {"07": 14, "08": 11, "27": 1})
        self.assertEqual(COHORT["additional_companions_after"], 249)
        self.assertIn("08.02", cov["remaining_ids"])
        self.assertIn("27.15", cov["remaining_ids"])

    def test_predecessor_and_no_new_legacy_selection(self):
        old = json.loads((ROOT / "docs/authoring/leisure-life-design/cohort.json").read_text())
        self.assertEqual(old["ids"][-1], "27.02")
        self.assertEqual(old["additional_companions_after"], COHORT["additional_companions_before"])
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        self.assertFalse(set(IDS) & set(contract["retained_legacy_competency_ids"]))
        self.assertEqual(COHORT["legacy_companion_ids"], [])

    def test_checks_have_three_separate_answers(self):
        for cid in IDS:
            for name in ("check-prompts.md", "check-answers.md"):
                self.assertEqual(re.findall(r"^(\d)\. ", doc(cid, name), re.M), ["1", "2", "3"])
            self.assertNotEqual(doc(cid, "check-prompts.md"), doc(cid, "check-answers.md"))

    def test_local_links_and_source_anchors(self):
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target:
                    continue
                name, _, anchor = target.partition("#")
                dest = (path.parent / name).resolve()
                self.assertTrue(dest.is_file(), f"{path}: {target}")
                if anchor:
                    self.assertRegex(dest.read_text(), rf"(?mi)^## {re.escape(anchor)}$")

    def test_six_inspected_sources_and_excluded_routes(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 7)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-26")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        self.assertIn("Original referenced books not inspected", sources[5]["limits"])
        self.assertIn("returned 403", (SOURCE / "SOURCES.md").read_text())
        self.assertIn("retrieval errors", (SOURCE / "SOURCES.md").read_text())

    def test_fiction_and_formal_review_boundaries(self):
        self.assertTrue(FIX["all_responses_supplied_fiction"])
        self.assertFalse(FIX["actual_participant_evidence"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        self.assertEqual(set(CASES), set(IDS))
        for cid in IDS:
            self.assertIn("Supplied fiction", doc(cid, "later-packet.md"))
            self.assertIn("remain pending", doc(cid, "SCOPE-MAP.md"))
            self.assertIn(f"## {cid}", (SOURCE / "QUALITY-REVIEW.md").read_text())

    def test_verification_exact_source_and_test_bytes(self):
        verification = json.loads((SOURCE / "verification.json").read_text())
        expected = {
            str(p.relative_to(ROOT))
            for p in SOURCE.rglob("*")
            if p.is_file() and p.name != "verification.json"
        }
        self.assertEqual(set(verification["source_sha256"]), expected)
        for path, digest in verification["source_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        self.assertEqual(
            hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            verification["focused_test_sha256"],
        )

    def test_active_contract_valid_and_scoped(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertTrue(all(isinstance(x, str) for x in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-LIFE-INTEGRATION-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/leisure-life-design/**",
                "tests/test_m6k_leisure_life_design_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


class IndividualCaseTests(unittest.TestCase):
    def test_2703_weekly_capacity_and_changed_visits(self):
        f = CASES["27.03"]
        self.assertEqual(f["original_weekly"] - sum(f["visits"]), 150)
        self.assertEqual(
            f["original_weekly"] - sum(f["visits"]) - f["note_once"] - f["quiet_weekly"],
            f["week1_unallocated"],
        )
        self.assertEqual(f["original_weekly"] - 2 * 60, 120)
        self.assertIn("120 minutes remain", doc("27.03", "check-answers.md"))
        self.assertIn("one hundred", doc("27.03"))

    def test_2703_protection_and_handoff_not_assumed(self):
        f = CASES["27.03"]
        self.assertEqual(f["actual_quiet_periods"], 1)
        self.assertFalse(f["visit_takeover"])
        self.assertIsNone(f["support_reply"])
        self.assertIsNone(f["season_end"])
        self.assertIn("no replacement quiet period occurs", doc("27.03", "later-packet.md"))
        self.assertIn("nobody has agreed to take one over", doc("27.03", "later-packet.md"))

    def test_2704_work_and_renewal_timeline(self):
        f = CASES["27.04"]
        self.assertEqual(minute(f["work_end"]) - minute(f["work_start"]), f["correction_minutes"])
        self.assertLess(minute(f["work_end"]), minute(f["deadline"]))
        self.assertLess(minute(f["renewal_end"]), minute(f["renewal_ack"]))
        for k in ("work_start", "work_end", "renewal_start", "renewal_end", "renewal_ack"):
            self.assertIn(f[k], doc("27.04", "later-packet.md"))

    def test_2704_roles_retained_and_repair_performed(self):
        f = CASES["27.04"]
        self.assertEqual(len(table("27.04")), f["roles"])
        self.assertFalse(f["caregiver_held"] or f["colleague_takeover"])
        self.assertEqual(minute(f["call_end"]) - minute(f["call_start"]), 10)
        self.assertLess(minute(f["key_return"]), minute(f["key_deadline"]))
        self.assertIn("actually occurs", doc("27.04", "later-packet.md"))
        self.assertIn("existing responsibility", doc("27.04", "check-answers.md"))

    def test_2705_review_cost_no_double_count(self):
        f = CASES["27.05"]
        self.assertEqual(sum(f["review1_parts"]), f["review1"])
        self.assertEqual(f["review1"] + f["review2"], 27)
        self.assertEqual(f["review1"] + f["review2"] + f["call"], 37)
        self.assertIn("37 minutes", doc("27.05", "check-answers.md"))
        self.assertEqual(len(table("27.05")), f["headings"])

    def test_2705_late_accepted_and_unknown_cost(self):
        f = CASES["27.05"]
        self.assertTrue(f["form_late"] and f["form_accepted"])
        self.assertIsNone(f["transport_cost"])
        self.assertIn(f["form_submitted"], doc("27.05", "later-packet.md"))
        self.assertIn("no reply is supplied", doc("27.05", "later-packet.md"))
        self.assertIn("not clinical evidence", doc("27.05", "check-answers.md"))

    def test_2706_missed_session_and_actual_budget(self):
        f = CASES["27.06"]
        self.assertEqual(sum(f["planned_sessions"]) + f["reader_check"], 50)
        self.assertEqual(sum(f["actual_sessions"]) + f["reader_check"], f["actual_total"])
        self.assertEqual(f["actual_total"], 32)
        self.assertIn("Session 3 is missed", doc("27.06", "later-packet.md"))
        self.assertIn("32 minutes", doc("27.06", "later-packet.md"))

    def test_2706_duplicate_precedence_and_unmet_condition(self):
        f = CASES["27.06"]
        self.assertEqual(
            [k for k in f["fresh_actual"] if f["fresh_actual"][k] != f["fresh_expected"][k]], ["F"]
        )
        self.assertEqual(f["fresh_expected"]["F"], f["practice"]["C"])
        self.assertFalse(f["continue_condition_met"] or f["retest_performed"])
        self.assertIn("BLUE rather than GREY", doc("27.06", "later-packet.md"))
        self.assertIn("GREY: exact-duplicate precedence", doc("27.06", "check-answers.md"))

    def test_2707_arrival_and_delayed_return_math(self):
        f = CASES["27.07"]
        self.assertEqual(
            minute(f["morning_arrival"]) + f["corridor_minutes"], minute(f["room_arrival"])
        )
        self.assertEqual(minute(f["start"]) - minute(f["room_arrival"]), 15)
        self.assertEqual(minute(f["home_arrival"]) + f["delay"], minute(f["delayed_home"]))
        self.assertEqual(minute(f["delayed_home"]) - minute(f["household_duty"]), 10)
        self.assertIn(f["delayed_home"], doc("27.07", "check-answers.md"))

    def test_2707_confirmation_not_lived_transition(self):
        f = CASES["27.07"]
        self.assertTrue(f["main_confirmed"] and f["goodbye_sent"])
        self.assertFalse(f["fallback_confirmed"] or f["first_day_occurred"])
        self.assertIn("first day has not occurred", doc("27.07", "later-packet.md"))
        self.assertIn("fallback is not confirmed", doc("27.07", "later-packet.md"))
        self.assertIn("No future group meeting", doc("27.07", "later-packet.md"))

    def test_2708_check_inside_twenty_minute_period(self):
        f = CASES["27.08"]
        self.assertEqual(sum(f["second_parts"]), 20)
        self.assertEqual(f["first_work"] + sum(f["second_parts"]), 40)
        self.assertEqual(minute(f["second_start"]) + sum(f["second_parts"]), minute(f["stop"]))
        self.assertIn("12 + 3 + 5 = 20", doc("27.08", "check-answers.md"))

    def test_2708_function_rest_and_emotion_distinct(self):
        f = CASES["27.08"]
        self.assertTrue(f["reader_next_actions"] and f["quiet_started"])
        self.assertFalse(f["actual_borrow_return"])
        self.assertIsNone(f["contented_mood"])
        self.assertIn("not actually borrowed or returned", doc("27.08", "later-packet.md"))
        self.assertIn(
            "does not report a grateful or contented mood", doc("27.08", "later-packet.md")
        )
        self.assertIn("Tell the room steward if pieces are missing", doc("27.08"))

    def test_2709_ordinary_success_and_direct_deadline_miss(self):
        f = CASES["27.09"]
        self.assertLessEqual(minute(f["ordinary_window"][0]), minute(f["ordinary_answer"]))
        self.assertLessEqual(minute(f["ordinary_answer"]), minute(f["ordinary_window"][1]))
        self.assertLess(minute(f["direct_ack"]), minute(f["direct_deadline"]))
        self.assertEqual(minute(f["direct_answer"]) - minute(f["direct_deadline"]), 10)
        for k in ("ordinary_answer", "direct_ack", "direct_deadline", "direct_answer"):
            self.assertIn(f[k], doc("27.09", "later-packet.md"))

    def test_2709_revision_without_erasing_unknowns(self):
        f = CASES["27.09"]
        self.assertIsNone(f["repair_reply"])
        self.assertIsNone(f["interruptions_reduction"])
        self.assertFalse(f["next_trial_occurred"])
        self.assertIn("next trial has not occurred", doc("27.09", "later-packet.md"))
        self.assertIn("principle, old method, evidence for/against, alternative", doc("27.09"))
        self.assertIn("unsupported number", doc("27.09", "check-answers.md"))

    def test_2710_actual_hint_and_access_support_distinguished(self):
        f = CASES["27.10"]
        self.assertFalse(f["first_independent"])
        self.assertTrue(f["second_independent"])
        self.assertFalse(f["second_hint"])
        self.assertEqual(f["second_access"], "text-to-speech")
        later = doc("27.10", "later-packet.md")
        self.assertIn("only after the teacher asks", later)
        self.assertIn("no instructional hint", later)
        self.assertIn("text-to-speech", later)

    def test_2710_new_notice_and_limited_followthrough(self):
        f = CASES["27.10"]
        self.assertEqual(sum(f["contact_minutes"]), 30)
        self.assertEqual(f["delay_days"], 8)
        self.assertEqual(f["second_choice"], "listening")
        self.assertFalse(f["event_attended"])
        self.assertIsNone(f["sustained_generativity"])
        self.assertIn("eight days later", doc("27.10", "later-packet.md"))
        self.assertIn("Read the supplied one-paragraph route description first", doc("27.10"))
        self.assertIn("The entrance is south of the hall", doc("27.10"))

    def test_2711_notice_repair_and_specific_revision(self):
        f = CASES["27.11"]
        self.assertTrue(f["notice_ack"])
        self.assertLess(minute(f["wrong_notice"]), minute(f["corrected_notice"]))
        later = doc("27.11", "later-packet.md")
        for k in ("wrong_notice", "corrected_notice", "first_test_confusion"):
            self.assertIn(f[k], later)
        self.assertIn("same staffed desk, before 12:00", later)

    def test_2711_willing_owner_not_founder_dependency(self):
        f = CASES["27.11"]
        self.assertTrue(f["maintenance_accepted"])
        self.assertFalse(f["pat_maintenance_accepted"] or f["founder_approval_required"])
        self.assertIsNone(f["future_benefit"])
        self.assertIn("Lee explicitly accepts maintaining", doc("27.11", "later-packet.md"))
        self.assertIn("without Noor's permission", doc("27.11", "later-packet.md"))
        self.assertIn("withdraw if no one can verify", doc("27.11"))

    def test_2712_dated_record_and_unknown_months(self):
        f = CASES["27.12"]
        self.assertEqual(len(table("27.12")), f["records"])
        self.assertEqual(len(f["missing_months"]), 4)
        for month in f["missing_months"]:
            self.assertIn(month, doc("27.12"))
        self.assertIn("unknown, not empty or bad", doc("27.12"))
        self.assertIn("becoming; served; harm or neglect; changed; received", doc("27.12"))

    def test_2712_first_action_and_open_repair_review(self):
        f = CASES["27.12"]
        self.assertLessEqual(f["first_minutes"], f["capacity"])
        self.assertLessEqual(f["renewed_commitments"], 3)
        self.assertIsNone(f["repair_reply"])
        self.assertFalse(f["review_occurred"])
        later = doc("27.12", "later-packet.md")
        for k in ("repair_offer_sent", "release_performed", "first_check", "review_date"):
            self.assertIn(f[k], later)
        self.assertIn("has not occurred", later)

    def test_2713_five_roles_and_optional_decline(self):
        f = CASES["27.13"]
        self.assertEqual(len(table("27.13")), f["cards"])
        self.assertFalse(f["workshop_registered"] or f["workshop_attended"])
        self.assertEqual(f["leadership"], "exploring")
        self.assertIn(
            "endorsed preference rather than a scheduling barrier", doc("27.13", "later-packet.md")
        )
        self.assertIn(
            "A constraint and an endorsed preference are different",
            doc("27.13", "check-answers.md"),
        )

    def test_2713_duties_and_runtime_preserved(self):
        f = CASES["27.13"]
        self.assertTrue(f["briefing_performed"] and f["existing_work_retained"])
        self.assertFalse(f["runtime_applicability_changed"])
        self.assertEqual(f["briefing_minutes"], 10)
        self.assertIn(
            "gives the promised ten-minute team briefing", doc("27.13", "later-packet.md")
        )
        self.assertIn("No disclosure of intimate reasons", doc("27.13"))
        self.assertIn("changing a role label does not erase it", doc("27.13", "check-answers.md"))

    def test_2714_authorized_route_receipt_and_purpose(self):
        f = CASES["27.14"]
        self.assertLess(minute(f["submitted"]), minute(f["acknowledged"]))
        self.assertLess(minute(f["acknowledged"]), minute(f["deadline"]))
        self.assertTrue(f["agenda_included"])
        self.assertEqual(f["purpose_checks"], 3)
        for k in ("submitted", "acknowledged", "deadline"):
            self.assertIn(f[k], doc("27.14", "later-packet.md"))
        self.assertIn("three bounded checks", doc("27.14", "later-packet.md"))

    def test_2714_unsent_barrier_and_qualification_limits(self):
        f = CASES["27.14"]
        for k in (
            "spoken_exchange",
            "decision_occurred",
            "unsent_contribution",
            "qualification_established",
        ):
            self.assertFalse(f[k])
        self.assertEqual(f["rejected_case"], "access barrier")
        self.assertIn("preparation but not contribution", doc("27.14", "later-packet.md"))
        self.assertIn("access barrier", doc("27.14", "later-packet.md"))
        self.assertIn(
            "qualification, safety requirement or live dialogue skill",
            doc("27.14", "check-answers.md"),
        )


class FreshCaseRegressionTests(unittest.TestCase):
    def test_late_start_cannot_meet_work_deadline(self):
        self.assertEqual(minute("09:50") + 12, minute("10:02"))
        self.assertIn("10:02", doc("27.04", "check-answers.md"))

    def test_transport_fallback_requires_changed_morning(self):
        self.assertEqual(minute("07:50") + 10, minute("08:00"))
        self.assertGreater(minute("08:00"), minute("07:30"))
        self.assertEqual(minute("08:10") + 10, minute("08:20"))
        self.assertIn("different morning arrangement which is not yet confirmed", doc("27.07"))

    def test_no_overlap_between_implemented_prior_new_and_remaining(self):
        cov = COHORT["source_coverage"]
        parts = [
            set(cov[k])
            for k in (
                "implemented_ids",
                "prior_companion_ids",
                "new_companion_ids",
                "remaining_ids",
            )
        ]
        self.assertEqual(sum(map(len, parts)), 383)
        self.assertEqual(len(set.union(*parts)), 383)
        self.assertEqual([i for i in cov["remaining_ids"] if i.startswith("27.")], ["27.15"])

    def test_clock_parser_rejects_malformed_inputs(self):
        for value in (None, True, 900, "9:00", "24:00", "09:60", "-1:00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                minute(value)


if __name__ == "__main__":
    unittest.main()
