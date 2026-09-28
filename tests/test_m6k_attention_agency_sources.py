"""Integrity and supplied-case checks; these do not grade learners or runtime evidence."""

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

import yaml

from tests.m6k_historical_inputs import historical_input_path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/attention-agency"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
CASES = FIX["cases"]
IDS = ["07.13", "07.14", *[f"08.{i:02}" for i in range(1, 12)]]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


def minute(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        raise ValueError("Expected HH:MM")
    hour, mins = map(int, value.split(":"))
    if hour > 23 or mins > 59:
        raise ValueError("Invalid clock time")
    return hour * 60 + mins


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
        self.assertEqual(COHORT["reporting_cadence"], 13)

    def test_canonical_entries_and_eight_input_hashes(self):
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
        self.assertEqual(len(COHORT["input_sha256"]), 8)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(
                hashlib.sha256(historical_input_path(ROOT / path).read_bytes()).hexdigest(), digest
            )

    def test_current_recovery_inputs_remain_equal(self):
        for domain in ("07", "08"):
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

    def test_domain_specific_modes_and_professional_boundaries(self):
        for entry in COHORT["entries"]:
            clinical = entry["id"].startswith("07.")
            expected = ["agency", "receptivity"]
            if clinical:
                expected.append("interdependence")
            self.assertEqual(entry["classification"]["formation_modes"], expected)
            self.assertEqual(entry["classification"]["applicability"], "cross_context_core")
            self.assertEqual(
                entry["classification"]["normative_status"],
                "cross_tradition_core_or_broadly_recurrent",
            )
            self.assertEqual("professional_boundary" in entry, clinical)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                if clinical:
                    self.assertIn(entry["professional_boundary"], doc(entry["id"], name))
                else:
                    (self.assertNotIn if name == "learner-guide.md" else self.assertIn)(
                        "no professional_boundary field", doc(entry["id"], name)
                    )
            expected_evidence = (
                ["self_report", "behavioral_adherence", "observer_feedback", "longitudinal_review"]
                if clinical
                else [
                    "behavioral_adherence",
                    "artifact",
                    "objective_indicator",
                    "longitudinal_review",
                ]
            )
            self.assertEqual(entry["measurement"]["preferred_evidence_types"], expected_evidence)

    def test_source_coverage_is_disjoint_and_complete(self):
        cov = COHORT["source_coverage"]
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        canonical = {e["id"] for d in catalog["curriculum"]["domains"] for e in d["competencies"]}
        contract = yaml.safe_load(
            (
                ROOT / "docs/authoring/catalog-product-integration-20260928/"
                "authoring-selection-baseline.yaml"
            ).read_text()
        )
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
        self.assertEqual(len(prior), 262)
        self.assertEqual(sorted(prior), cov["prior_companion_ids"])
        self.assertEqual(sorted(implemented), cov["implemented_ids"])
        self.assertFalse(implemented & set(prior))
        self.assertFalse((implemented | set(prior)) & set(IDS))
        covered = implemented | set(prior) | set(IDS)
        self.assertEqual(len(covered), 383)
        self.assertEqual(cov["covered_count"], 383)
        self.assertEqual(sorted(canonical - covered), cov["remaining_ids"])
        self.assertEqual(cov["remaining_count"], 0)
        self.assertEqual(dict(Counter(cid[:2] for cid in canonical - covered)), {})
        self.assertEqual(cov["remaining_by_domain"], {})
        self.assertEqual(COHORT["additional_companions_after"], 275)
        self.assertEqual(cov["remaining_ids"], [])
        self.assertEqual(covered, canonical)

    def test_predecessor_and_exact_legacy_companion(self):
        old = json.loads((ROOT / "docs/authoring/emotional-foundations/cohort.json").read_text())
        self.assertEqual(old["ids"][-1], "27.15")
        self.assertEqual(old["additional_companions_after"], COHORT["additional_companions_before"])
        contract = yaml.safe_load(
            (
                ROOT / "docs/authoring/catalog-product-integration-20260928/"
                "authoring-selection-baseline.yaml"
            ).read_text()
        )
        self.assertEqual(set(IDS) & set(contract["retained_legacy_competency_ids"]), {"08.02"})
        self.assertEqual(COHORT["legacy_companion_ids"], ["08.02"])

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

    def test_seven_inspected_sources_and_excluded_routes(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 8)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-27")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        self.assertIn("returned 403", (SOURCE / "SOURCES.md").read_text())

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
            self.assertEqual(
                hashlib.sha256(historical_input_path(ROOT / path).read_bytes()).hexdigest(), digest
            )
        self.assertEqual(
            hashlib.sha256(historical_input_path(Path(__file__)).read_bytes()).hexdigest(),
            verification["focused_test_sha256"],
        )

    def test_active_contract_valid_and_scoped(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertTrue(all(isinstance(x, str) for x in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-ATTENTION-AGENCY-FINAL-THIRTEEN":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/emotional-foundations/**",
                "tests/test_m6k_emotional_foundations_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


class IndividualCaseTests(unittest.TestCase):
    def test_help_booking_is_not_assessment_or_resolved_access(self):
        f = CASES["07.13"]
        self.assertTrue(f["request_sent"] and f["appointment_booked"])
        self.assertFalse(f["assessment_attended"] or f["transport_confirmed"])
        self.assertIsNone(f["diagnosis"])
        self.assertIn("No assessment has yet occurred", doc("07.13", "later-packet.md"))
        self.assertIn("not a waiting requirement", doc("07.13"))
        self.assertIn("location-bound", doc("07.13", "check-answers.md"))

    def test_generalization_separates_stopped_from_unavailable(self):
        f = CASES["07.14"]
        self.assertEqual(
            f["complete_answers"] + f["stopped_attempts"] + f["unavailable"], f["opportunities"]
        )
        self.assertEqual((f["contexts"], f["strategies_used"]), (2, 2))
        self.assertFalse(f["revision_tested"])
        self.assertIn("unavailable, not attempted unsuccessfully", doc("07.14", "later-packet.md"))
        self.assertIn("increases agitation", doc("07.14", "later-packet.md"))

    def test_attention_descriptive_difference_retains_nonstudy_time(self):
        f = CASES["08.01"]
        self.assertEqual(sum(f["usual_reading"]), 7)
        self.assertEqual(sum(f["changed_reading"]), 13)
        self.assertEqual(sum(f["changed_reading"]) - sum(f["usual_reading"]), 6)
        self.assertEqual(
            [a + b for a, b in zip(f["changed_reading"], f["changed_other"], strict=True)], [10, 10]
        )
        self.assertFalse(f["causal_effect_established"] or f["whole_day_observed"])
        self.assertIn("five answering a necessary call", doc("08.01", "later-packet.md"))

    def test_presence_actual_repeat_interval_and_accessible_variant(self):
        f = CASES["08.02"]
        self.assertEqual(sum(f["window_minutes"]), 45)
        self.assertEqual(f["days"][-1] - f["days"][0], 6)
        self.assertEqual((f["attempted"], f["completed"]), (3, 3))
        self.assertTrue(f["comparison"] and f["final_review"])
        self.assertFalse(f["submitted_checkins"])
        self.assertIn("October 7, 10:00\u201310:15", doc("08.02", "later-packet.md"))
        self.assertIn("consistently shortened windows", doc("08.02"))
        self.assertIn("record that limitation", doc("08.02"))

    def test_impulse_pre_action_and_late_return_are_distinct(self):
        f = CASES["08.03"]
        self.assertLessEqual(f["pause_seconds"], f["max_pause"])
        self.assertEqual(f["pre_action_pauses"] + f["post_action_returns"], f["opportunities"])
        self.assertEqual(f["prevented_openings"], 1)
        self.assertIn("not a second prevented opening", doc("08.03", "later-packet.md"))
        self.assertIn("Address the urgent need", doc("08.03", "check-answers.md"))

    def test_desire_keeps_agreement_and_uncertain_reward(self):
        f = CASES["08.04"]
        self.assertEqual(minute(f["proposed_start"]) + f["video_minutes"] - minute(f["call"]), 6)
        self.assertEqual(minute(f["actual_video_end"]) - minute(f["actual_video_start"]), 8)
        self.assertTrue(f["call_kept"])
        self.assertFalse(f["desire_disappeared"])
        self.assertIn("wanting another one", doc("08.04", "later-packet.md"))

    def test_discomfort_partial_attempt_and_uncertain_paper(self):
        f = CASES["08.05"]
        self.assertEqual(sum(f["attempt_seconds"]), 160)
        self.assertEqual(f["completed_windows"], 1)
        self.assertEqual(f["assignments"].count("UNSURE"), 1)
        self.assertFalse(f["pain_training"])
        self.assertIn(
            "new wrist pain after forty seconds and stops", doc("08.05", "later-packet.md")
        )
        self.assertIn("160 seconds", doc("08.05", "later-packet.md"))

    def test_start_deferral_is_not_second_start_or_failed_attempt(self):
        f = CASES["08.06"]
        self.assertEqual(len(f["actual_start_minutes"]), f["known_starts"])
        self.assertEqual(f["known_starts"] + f["deferred_windows"], 2)
        self.assertTrue(all(2 <= n <= 5 for n in f["actual_start_minutes"]))
        self.assertFalse(f["cue_tested"] or f["practice_completed"])
        self.assertIn("no test of whether the cue helps", doc("08.06", "later-packet.md"))
        self.assertIn("reduced duration", doc("08.06"))

    def test_habit_design_preserves_cost_and_untested_revision(self):
        f = CASES["08.07"]
        self.assertEqual((f["opportunities"], f["reminders_written"]), (2, 1))
        self.assertTrue(f["access_cost"])
        self.assertFalse(f["revision_tested"] or f["folder_returned"])
        self.assertIn("obstructs the comfortable writing area", doc("08.07", "later-packet.md"))
        self.assertIn("have not occurred", doc("08.07", "later-packet.md"))

    def test_minimum_actual_learning_and_care_pause(self):
        f = CASES["08.08"]
        self.assertEqual(sum(f["minutes"]), 12)
        self.assertEqual((f["normal_sessions"], f["minimum_sessions"], f["care_pauses"]), (1, 1, 1))
        self.assertNotEqual(f["initial_minimum_answer"], f["mappings"]["NERI"])
        self.assertEqual(f["corrected_minimum_answer"], f["mappings"]["NERI"])
        self.assertFalse(f["later_recall_tested"])
        self.assertIn("pause is not an attempt", doc("08.08", "later-packet.md"))

    def test_restraint_ceiling_not_target_and_support_retained(self):
        f = CASES["08.09"]
        self.assertLess(f["actual_minutes"], f["ceiling_minutes"])
        self.assertTrue(f["support_sound_kept"])
        self.assertFalse(f["gratitude_reported"] or f["escalation"])
        self.assertIn("six minutes", doc("08.09", "later-packet.md"))
        self.assertIn("not an endurance target", doc("08.09", "check-answers.md"))

    def test_completion_uses_existing_done_and_actual_check(self):
        f = CASES["08.10"]
        self.assertEqual(sum(f["work_minutes"]), 14)
        self.assertTrue(all(n <= f["limit_per_window"] for n in f["work_minutes"]))
        self.assertEqual(f["paragraphs"], 3)
        self.assertTrue(f["reopen_checked"] and f["border_ended"])
        self.assertFalse(f["sunday_review_done"])
        for instruction in (
            "Use the east entrance.",
            "The reading table is beside the window.",
            "Return shared pencils to the marked cup.",
        ):
            self.assertIn(instruction, doc("08.10"))
            self.assertIn(instruction, doc("08.10", "later-packet.md"))

    def test_rule_revision_retains_failed_retrieval_and_missing_opportunity(self):
        f = CASES["08.11"]
        self.assertTrue(f["rough_saved"])
        self.assertFalse(f["retrieval_succeeded"] or f["revision_tested"] or f["library_inquiry"])
        self.assertIn("no new note need has arisen", doc("08.11", "later-packet.md"))
        self.assertIn("shared duties", doc("08.11", "check-answers.md"))


class PreservationTests(unittest.TestCase):
    def package(self, name):
        return COHORT["preserved_protocols"][f"data/practices/protocols/08/{name}.yaml"]

    def test_both_original_packages_equal_the_pinned_source_stage(self):
        self.assertEqual(len(COHORT["preserved_protocols"]), 2)
        for path, snapshot in COHORT["preserved_protocols"].items():
            self.assertEqual(
                snapshot, yaml.safe_load(historical_input_path(ROOT / path).read_text())
            )
            self.assertIn(path, COHORT["input_sha256"])

    def test_legacy_actions_fields_rules_and_adaptation(self):
        p = self.package("PRACTICE-PRESENCE-01")
        a = p["intervention"]["actions"]
        self.assertEqual(
            [x["stable_id"] for x in a], [f"PRACTICE-PRESENCE-01-A{i}" for i in range(1, 4)]
        )
        self.assertEqual([x["due_within_days"] for x in a], [3, None, 7])
        self.assertEqual(
            p["evidence_and_scoring"]["check_in_fields"],
            [
                "user_initiated",
                "moved_beyond_transactional",
                "follow_up_question_asked",
                "meaningful_information_shared",
                "follow_up_within_seven_days",
                "internal_resistance",
            ],
        )
        self.assertEqual(
            p["completion_and_review"]["completion_rules"],
            {
                "minimum_completed": 2,
                "substantive_markers": [
                    "meaningful_information_shared",
                    "follow_up_within_seven_days",
                ],
                "marker_mode": "all",
            },
        )
        self.assertIn(
            "Shorten windows consistently", p["intervention"]["adaptations"]["resource_variants"][0]
        )
        self.assertIn("consistently shortened", doc("08.02", "SCOPE-MAP.md"))

    def test_typed_start_fields_normalizers_roles_and_completion(self):
        p = self.package("PRACTICE-MOTIVATION-INDEPENDENT-START-01")
        actions = p["intervention"]["actions"]
        self.assertEqual([a["due_within_days"] for a in actions], [3, 6, 7])
        measures = {
            m["measurement_id"]: m for a in actions for m in a["evidence_rules"]["measurements"]
        }
        self.assertEqual(set(measures), set(p["evidence_and_scoring"]["check_in_fields"]))
        self.assertEqual(len(measures), 9)
        for a in actions:
            rule = a["evidence_rules"]
            self.assertEqual(rule["schema_version"], "typed-evidence-rules-v1")
            self.assertEqual(rule["max_age_days"], 30)
            self.assertEqual(rule["transfer_disposition"], "context_bound")
            self.assertEqual(
                [m["role"] for m in rule["measurements"]], ["primary", "supporting", "adverse"]
            )
        duration = measures["baseline_scope_respected"]
        self.assertEqual([duration[k] for k in ("minimum", "target", "maximum")], ["0", "5", "15"])
        count = measures["chosen_start_count"]
        self.assertEqual([count[k] for k in ("minimum", "target", "maximum")], ["0", "2", "2"])
        self.assertEqual(
            measures["comparison_boundaries_present"]["criteria"],
            ["two_windows_distinguished", "defer_preserved", "capacity_not_scored"],
        )
        self.assertEqual(
            p["completion_and_review"]["completion_rules"],
            {
                "minimum_completed": 2,
                "substantive_markers": [
                    "baseline_start_occurred",
                    "cued_start_occurred",
                    "chosen_start_count",
                ],
                "marker_mode": "any",
            },
        )

    def test_final_partition_has_no_unauthored_id_or_duplicate(self):
        cov = COHORT["source_coverage"]
        groups = [
            set(cov[k])
            for k in (
                "implemented_ids",
                "prior_companion_ids",
                "new_companion_ids",
                "remaining_ids",
            )
        ]
        self.assertEqual(sum(map(len, groups)), 383)
        self.assertEqual(len(set.union(*groups)), 383)
        self.assertEqual(cov["remaining_ids"], [])
        self.assertEqual(COHORT["continuation_order"], IDS)
        self.assertIn("Zero source IDs remain", (SOURCE / "README.md").read_text())

    def test_clock_parser_rejects_invalid_values(self):
        for value in (None, True, 900, "9:00", "24:00", "09:60", "-1:00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                minute(value)


if __name__ == "__main__":
    unittest.main()
