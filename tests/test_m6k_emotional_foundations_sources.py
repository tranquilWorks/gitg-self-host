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
SOURCE = ROOT / "docs/authoring/emotional-foundations"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
CASES = FIX["cases"]
IDS = [f"07.{i:02}" for i in range(1, 13)] + ["27.15"]


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
        self.assertEqual(COHORT["reporting_cadence"], 13)

    def test_canonical_entries_and_six_input_hashes(self):
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
        self.assertEqual(len(COHORT["input_sha256"]), 6)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(
                hashlib.sha256(historical_input_path(ROOT / path).read_bytes()).hexdigest(), digest
            )

    def test_current_recovery_inputs_remain_equal(self):
        for domain in ("07", "27"):
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
            expected = ["agency", "receptivity", "interdependence"]
            if not clinical:
                expected.append("stewardship")
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
                else ["artifact", "observer_feedback", "longitudinal_review", "outcome_indicator"]
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
        self.assertEqual(len(prior), 249)
        self.assertEqual(sorted(prior), cov["prior_companion_ids"])
        self.assertEqual(sorted(implemented), cov["implemented_ids"])
        self.assertFalse(implemented & set(prior))
        self.assertFalse((implemented | set(prior)) & set(IDS))
        covered = implemented | set(prior) | set(IDS)
        self.assertEqual(len(covered), 370)
        self.assertEqual(cov["covered_count"], 370)
        self.assertEqual(sorted(canonical - covered), cov["remaining_ids"])
        self.assertEqual(cov["remaining_count"], 13)
        self.assertEqual(dict(Counter(cid[:2] for cid in canonical - covered)), {"07": 2, "08": 11})
        self.assertEqual(cov["remaining_by_domain"], {"07": 2, "08": 11})
        self.assertEqual(COHORT["additional_companions_after"], 262)
        self.assertIn("08.02", cov["remaining_ids"])
        self.assertIn("07.13", cov["remaining_ids"])

    def test_predecessor_and_no_new_legacy_selection(self):
        old = json.loads((ROOT / "docs/authoring/life-integration/cohort.json").read_text())
        self.assertEqual(old["ids"][-1], "27.14")
        self.assertEqual(old["additional_companions_after"], COHORT["additional_companions_before"])
        contract = yaml.safe_load(
            (
                ROOT / "docs/authoring/catalog-product-integration-20260928/"
                "authoring-selection-baseline.yaml"
            ).read_text()
        )
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

    def test_eight_inspected_sources_and_excluded_routes(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 9)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-27")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        self.assertIn("Linked workbook modules were not read", sources[5]["limits"])
        self.assertIn("returned 403", (SOURCE / "SOURCES.md").read_text())
        self.assertIn("timed out", (SOURCE / "SOURCES.md").read_text())

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
        if contract["batch"]["id"] == "M6K-EMOTIONAL-FOUNDATIONS-THIRTEEN":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/life-integration/**",
                "tests/test_m6k_life_integration_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


def second(value):
    h, m, s = map(int, value.split(":"))
    return h * 3600 + m * 60 + s


class IndividualCaseTests(unittest.TestCase):
    def test_0701_event_time_and_provisional_labels(self):
        f = CASES["07.01"]
        self.assertEqual(minute(f["planned_walk"]) - minute(f["message"]), 40)
        guide = doc("07.01")
        for label in (
            "anger",
            "hurt",
            "shame",
            "fear",
            "envy",
            "grief",
            "disappointment",
            "exhaustion",
        ):
            self.assertIn(label, guide.lower())
        self.assertIn("one fitting feature and one limitation", guide)
        self.assertIn("hot face, tight jaw and low energy", guide)

    def test_0701_rating_change_not_isolated_cause(self):
        f = CASES["07.01"]
        self.assertEqual(f["initial_intensity"] - f["later_intensity"], 2)
        self.assertFalse(
            f["rest_isolated_cause"] or f["saturday_accepted"] or f["friend_motive_verified"]
        )
        self.assertIn("their individual effects are unknown", doc("07.01", "later-packet.md"))
        self.assertIn("not independently verified motive evidence", doc("07.01", "later-packet.md"))

    def test_0702_three_cue_timelines(self):
        f = CASES["07.02"]
        self.assertEqual(second(f["tuesday_typing"]) - second(f["tuesday_cue"]), 15)
        self.assertEqual(second(f["thursday_typing"]) - second(f["thursday_cue"]), 12)
        self.assertEqual(second(f["friday_response"]) - second(f["friday_cue"]), 3)
        self.assertEqual(second(f["friday_typing"]) - second(f["friday_response"]), 21)
        for k in ("friday_cue", "friday_response", "friday_typing", "friday_sent"):
            self.assertIn(f[k], doc("07.02", "later-packet.md"))

    def test_0702_pain_and_missing_signals_not_diagnosed(self):
        f = CASES["07.02"]
        self.assertFalse(f["pain_changed"] or f["calm_established"])
        self.assertIsNone(f["diagnosis"])
        self.assertEqual(len(table("07.02")), 3)
        self.assertIn("Jaw not noticeably changed", doc("07.02"))
        self.assertIn("still reports feeling hurried", doc("07.02", "later-packet.md"))
        self.assertIn("not a medical assessment", doc("07.02", "check-answers.md"))

    def test_0703_two_deadlines_are_not_collapsed(self):
        f = CASES["07.03"]
        self.assertEqual(minute(f["actual"]) - minute(f["promised"]), 5)
        self.assertLess(minute(f["actual"]), minute(f["external_deadline"]))
        self.assertFalse(f["return_met"])
        self.assertTrue(f["external_met"])
        for k in ("actual", "promised", "external_deadline"):
            self.assertIn(f[k], doc("07.03", "later-packet.md"))

    def test_0703_rehearsal_and_safety_exception(self):
        f = CASES["07.03"]
        self.assertEqual(f["pause_seconds"], 90)
        self.assertFalse(f["accusation_sent"] or f["next_trial"])
        self.assertIn("authoritative record says 16:30", doc("07.03"))
        self.assertIn("immediate danger or urgent safety duty", doc("07.03"))
        self.assertIn("Not sending during a simulation", doc("07.03", "check-answers.md"))

    def test_0704_repeated_step_retains_partial_feared_outcome(self):
        f = CASES["07.04"]
        self.assertEqual(f["attempts_completed"], 2)
        self.assertEqual(sum(f["attempt_minutes"]), 10)
        self.assertEqual(f["peaks"], [f["local_ceiling"]] * 2)
        self.assertEqual(f["critical_remarks"], [False, True])
        self.assertIn("distress did not decrease", doc("07.04", "later-packet.md"))
        self.assertIn("That was in the notice", doc("07.04", "later-packet.md"))

    def test_0704_ceiling_never_overrides_threat_or_access(self):
        f = CASES["07.04"]
        self.assertTrue(f["supports_preserved"])
        self.assertFalse(f["clinical_exposure"] or f["automatic_escalation"])
        self.assertIn("not a general safety threshold", doc("07.04"))
        self.assertIn("stop whenever desired", doc("07.04"))
        self.assertIn("Clinical exposure needs an appropriate qualified plan", doc("07.04"))
        self.assertIn("prescribed supports", doc("07.04", "check-answers.md"))

    def test_0705_explanation_not_retroactive_return_agreement(self):
        f = CASES["07.05"]
        self.assertLess(minute(f["left_windowsill"]), minute(f["due"]))
        self.assertGreater(minute(f["returned"]), minute(f["due"]))
        self.assertEqual(f["search_minutes"], 6)
        for k in ("left_windowsill", "returned"):
            self.assertIn(f[k], doc("07.05", "later-packet.md"))
        self.assertIn(
            "does not make the wrong-place return an agreed one", doc("07.05", "later-packet.md")
        )

    def test_0705_declined_request_and_owner_authority(self):
        f = CASES["07.05"]
        self.assertEqual(f["item_owner"], "Quinn")
        self.assertFalse(f["future_shelf_promise"] or f["future_plan_agreed"] or f["new_loan"])
        self.assertIn("community-owned", doc("07.05"))
        self.assertIn("no authority to restrict lending", doc("07.05"))
        self.assertIn("No new return plan", doc("07.05", "later-packet.md"))

    def test_0706_support_and_continued_living_actual(self):
        f = CASES["07.06"]
        self.assertTrue(f["support_occurred"])
        self.assertEqual(f["support_minutes"], 10)
        for k in ("final_date", "meal_time"):
            self.assertIn(f[k], doc("07.06", "later-packet.md"))
        self.assertIn("call actually occurs", doc("07.06", "later-packet.md"))
        self.assertIn("removes future Sketch Circle reminders", doc("07.06", "later-packet.md"))

    def test_0706_unchanged_sadness_and_unconfirmed_replacement(self):
        f = CASES["07.06"]
        self.assertEqual(f["initial_sadness"], f["later_sadness"])
        self.assertFalse(f["new_class_confirmed"] or f["closure_established"])
        self.assertIn("no required order", doc("07.06"))
        self.assertIn("No names", (SOURCE / "QUALITY-REVIEW.md").read_text())
        self.assertIn("not been attended", doc("07.06", "later-packet.md"))

    def test_0707_responsibility_declined_repair_and_no_forgiveness_claim(self):
        f = CASES["07.07"]
        self.assertEqual(f["replacement_minutes"], 12)
        self.assertFalse(
            f["repair_accepted"] or f["repeat_apology"] or f["printer_blame_established"]
        )
        self.assertIsNone(f["forgiveness"])
        self.assertIn("declines the next-label offer", doc("07.07", "later-packet.md"))
        self.assertIn("no evidence Ari caused it", doc("07.07"))

    def test_0707_later_standard_actually_kept(self):
        f = CASES["07.07"]
        self.assertLess(minute(f["later_sent"]), minute(f["later_ack"]))
        self.assertLess(minute(f["later_ack"]), minute(f["later_deadline"]))
        for k in ("later_sent", "later_ack", "later_deadline"):
            self.assertIn(f[k], doc("07.07", "later-packet.md"))
        self.assertIn("forgiveness is not reported", doc("07.07", "later-packet.md"))

    def test_0708_learning_rule_is_complete_and_not_selection(self):
        f = CASES["07.08"]
        self.assertEqual(f["feature_slots"], 1)
        self.assertEqual(f["open_table_places"], 4)
        self.assertEqual(
            f["classifications"],
            {"April 13": "NEXT", "April 12": "TODAY", "April 10": "PAST", "missing": "ASK"},
        )
        for date in ("April 13", "April 12", "April 10"):
            self.assertIn(date, doc("07.08"))
        self.assertIn("If the date is missing, ask the organizer", doc("07.08"))

    def test_0708_pending_place_and_private_relationship_unknown(self):
        f = CASES["07.08"]
        self.assertTrue(f["request_received"])
        self.assertFalse(f["place_assigned"] or f["surveillance"])
        self.assertIsNone(f["relationship_reassurance"])
        self.assertIn("has not assigned a place", doc("07.08", "later-packet.md"))
        self.assertIn(
            "does not inspect the collaborator's messages", doc("07.08", "later-packet.md")
        )

    def test_0709_missed_portion_and_bounded_consented_exchange(self):
        f = CASES["07.09"]
        self.assertEqual(
            minute(f["original_lunch"]) - minute(f["changed_lunch"]), f["missed_minutes"]
        )
        self.assertLessEqual(f["exchange_minutes"], f["time_limit"])
        self.assertTrue(f["listening_consent"])
        self.assertIn("exchange lasts eight minutes", doc("07.09", "later-packet.md"))
        self.assertIn("ask what Jo understood", doc("07.09"))

    def test_0709_request_declined_alternative_not_yet_tested(self):
        f = CASES["07.09"]
        self.assertFalse(f["direct_note_promise"] or f["future_change_occurred"])
        self.assertTrue(f["notifications_enabled"])
        self.assertIn("declines to promise", doc("07.09", "later-packet.md"))
        self.assertIn("turns on notifications", doc("07.09", "later-packet.md"))
        self.assertIn("relationship repair remain untested", doc("07.09", "later-packet.md"))

    def test_0710_renewal_timeline_and_smaller_consequence(self):
        f = CASES["07.10"]
        times = [
            minute(f[k])
            for k in ("update", "consent", "work_start", "work_end", "sent", "ack", "deadline")
        ]
        self.assertEqual(times, sorted(times))
        self.assertEqual(minute(f["work_end"]) - minute(f["work_start"]), 18)
        self.assertLess(18, f["window_minutes"])
        self.assertEqual(f["practice_before"] - f["practice_after"], 15)
        for k in ("update", "consent", "work_start", "work_end", "sent", "ack", "deadline"):
            self.assertIn(f[k], doc("07.10", "later-packet.md"))

    def test_0710_care_and_complete_task_preserve_causal_limits(self):
        f = CASES["07.10"]
        self.assertFalse(f["care_conditional"] or f["isolated_cause"])
        self.assertEqual(f["classifications"]["missing"], "ASK")
        for text in ("May 11 → NEXT", "May 10 → TODAY", "no date → ASK"):
            self.assertIn(text, doc("07.10"))
        self.assertIn("does not isolate which factor", doc("07.10", "later-packet.md"))
        self.assertIn("basic care available", doc("07.10", "check-answers.md"))

    def test_0711_refusal_then_bounded_fallback(self):
        f = CASES["07.11"]
        times = [minute(f[k]) for k in ("proposal", "refusal", "fallback", "stop")]
        self.assertEqual(times, sorted(times))
        for k in ("proposal", "refusal", "fallback", "stop"):
            self.assertIn(f[k], doc("07.11", "later-packet.md"))
        self.assertFalse(f["approval"])
        self.assertIsNone(f["new_date"])

    def test_0711_neutral_good_does_not_erase_hardship(self):
        f = CASES["07.11"]
        self.assertEqual(f["present_good_minutes"], 10)
        self.assertFalse(f["joy_reported"])
        self.assertIn("useful nourishment, with no reported joy", doc("07.11", "later-packet.md"))
        self.assertIn("Lunch does not meet the missed deadline", doc("07.11"))
        self.assertIn("No revised date", doc("07.11", "check-answers.md"))

    def test_0712_interruption_and_uncontrolled_comparison(self):
        f = CASES["07.12"]
        self.assertEqual(f["first_window"] - f["interruption"], f["first_active"])
        self.assertEqual(f["restart_active"] - f["first_active"], 8)
        self.assertLessEqual(f["restart_active"], f["restart_limit"])
        self.assertTrue(f["scope_changed"])
        self.assertFalse(f["conditions_identical"] or f["isolated_cause"])
        self.assertIn(
            "eighteen active minutes now versus ten before", doc("07.12", "later-packet.md")
        )

    def test_0712_ownership_and_displaced_cost_retained(self):
        f = CASES["07.12"]
        self.assertEqual(f["known_moved"] + f["unknown_retained"], f["items"])
        self.assertTrue(f["tray_crowded"])
        self.assertFalse(f["envelope_opened"] or f["shelf_changed"] or f["next_check_occurred"])
        self.assertIn("sealed envelope", doc("07.12"))
        self.assertIn("owner is still unknown", doc("07.12", "later-packet.md"))
        self.assertIn("asks that future moves wait", doc("07.12", "later-packet.md"))

    def test_2715_help_quiet_and_card_return(self):
        f = CASES["27.15"]
        self.assertEqual(minute(f["help_end"]) - minute(f["help_start"]), 8)
        self.assertLessEqual(8, f["help_offer"])
        self.assertEqual(minute(f["quiet_end"]) - minute(f["quiet_start"]), 5)
        self.assertLess(minute(f["card_return"]), minute(f["card_deadline"]))
        self.assertEqual(len(table("27.15")), 3)
        for k in (
            "help_start",
            "help_end",
            "quiet_start",
            "quiet_end",
            "card_return",
            "card_deadline",
        ):
            self.assertIn(f[k], doc("27.15", "later-packet.md"))

    def test_2715_no_publication_debt_or_forced_gratitude(self):
        f = CASES["27.15"]
        for k in (
            "publication_offer_accepted",
            "return_favor_promised",
            "gratitude_reported",
            "history_repair_established",
        ):
            self.assertFalse(f[k])
        self.assertIn("declines Ren's publication condition", doc("27.15", "later-packet.md"))
        self.assertIn("no return favor promised", doc("27.15", "later-packet.md"))
        self.assertIn("exclusionary history remains acknowledged", doc("27.15", "later-packet.md"))


class FreshCaseRegressionTests(unittest.TestCase):
    def test_next_thirteen_are_exactly_partitioned(self):
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
        self.assertEqual(
            cov["remaining_ids"], ["07.13", "07.14"] + [f"08.{i:02}" for i in range(1, 12)]
        )
        self.assertEqual(COHORT["continuation_order"], ["27.15", *IDS[:-1]])

    def test_brief_pause_still_too_long_for_thirty_second_deadline(self):
        self.assertGreater(CASES["07.03"]["pause_seconds"], 30)
        self.assertIn("ninety-second action does not fit", doc("07.03"))

    def test_anxiety_source_limits_are_explicit(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertIn("not adopted", sources[2]["limits"])
        self.assertIn("not clinical validation or safety clearance", sources[2]["limits"])
        self.assertIn("stop this exercise if risk changes", doc("07.04"))
        self.assertIn(
            "no requirement to stay until fear halves", (SOURCE / "SOURCES.md").read_text()
        )

    def test_clock_parser_rejects_malformed_inputs(self):
        for value in (None, True, 900, "9:00", "24:00", "09:60", "-1:00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                minute(value)


if __name__ == "__main__":
    unittest.main()
