"""Regress source-case facts and boundaries; never assess learner competence."""

import hashlib
import json
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/resilience-community-listening"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"15.{i:02}" for i in range(4, 15)] + ["16.01"]


def doc(cid, filename="learner-guide.md"):
    return (SOURCE / cid / filename).read_text()


def minutes(start, end):
    return int(
        (datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60
    )


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_coverage_counts(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertEqual(COHORT["additional_companions_before"], 57)
        self.assertEqual(COHORT["additional_companions_after"], 69)
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )

    def test_full_canonical_entries_and_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        entries = [
            e for d in catalog["curriculum"]["domains"] for e in d["competencies"] if e["id"] in IDS
        ]
        self.assertEqual(COHORT["entries"], entries)
        for path, digest in COHORT["input_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_previous_endpoint_and_runtime_nonselection(self):
        previous = json.loads(
            (ROOT / "docs/authoring/digital-judgment-preparedness/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "15.03")
        implemented = yaml.safe_load(
            (ROOT / "contracts/tailored-practice-authoring.yaml").read_text()
        )["implemented_competency_ids"]
        self.assertFalse(set(IDS) & set(implemented))

    def test_complete_packages_and_three_separate_checks(self):
        for cid in IDS:
            for name in (
                "learner-guide.md",
                "later-packet.md",
                "check-prompts.md",
                "check-answers.md",
                "SCOPE-MAP.md",
            ):
                self.assertTrue((SOURCE / cid / name).is_file())
            for name in ("check-prompts.md", "check-answers.md"):
                self.assertEqual(re.findall(r"^(\d)\. ", doc(cid, name), re.M), ["1", "2", "3"])
            self.assertNotEqual(doc(cid, "check-prompts.md"), doc(cid, "check-answers.md"))

    def test_local_links_resolve(self):
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target:
                    self.assertTrue(
                        (path.parent / target.split("#")[0]).resolve().is_file(),
                        f"{path}: {target}",
                    )

    def test_exact_scope_and_measurement_boundaries(self):
        for e in COHORT["entries"]:
            scope = doc(e["id"], "SCOPE-MAP.md")
            for field in ("name", "scope", "evidence_of_progress"):
                self.assertIn(e[field], scope)
            self.assertIn(e["measurement"]["minimum_standard"], scope)
            if e.get("professional_boundary"):
                self.assertIn(e["professional_boundary"], scope)
            self.assertIn("not a formal M6K A/B/C receipt", scope)

    def test_sources_cover_every_id_and_preserve_inspection_limits(self):
        registry = json.loads((SOURCE / "sources.json").read_text())
        self.assertEqual(registry["inspected_on"], "2026-09-23")
        rows = registry["sources"]
        self.assertEqual(len({r["id"] for r in rows}), len(rows))
        self.assertEqual({r["competency_id"] for r in rows}, set(IDS))
        for r in rows:
            self.assertTrue(r["claim"] and r["limit"] and r["date_or_extent"])
            self.assertIn(r["url"], (SOURCE / "SOURCES.md").read_text())
        self.assertIn("Only landing abstract used", rows[11]["limit"])
        self.assertIn("Abstract evidence only", rows[18]["limit"])

    def test_successor_contract_and_simulation_boundary(self):
        self.assertTrue(FIX["synthetic"])
        self.assertFalse(FIX["runtime_evidence"])
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertTrue(all(isinstance(a, str) for a in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-RESILIENCE-COMMUNITY-LISTENING-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                "growth/**",
                ".github/**",
                "docs/authoring/digital-judgment-preparedness/**",
                "tests/test_m6k_digital_judgment_preparedness_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


class SafetyAndTrainingTests(unittest.TestCase):
    def test_exit_changes_when_help_unavailable(self):
        x = FIX["exit"]
        self.assertNotEqual(x["initial_endpoint"], x["changed_endpoint"])
        self.assertNotEqual(x["changed_endpoint"], x["rejected_endpoint"])
        self.assertIn("north staff member is unavailable", doc("15.04"))
        self.assertIn("east lobby", doc("15.04", "later-packet.md"))
        self.assertFalse(x["actual_deescalation_observed"])

    def test_credential_scope_does_not_become_physical_skill(self):
        a = FIX["providers"]["A"]
        self.assertTrue(a["introduction_credential_confirmed_in_later"])
        self.assertIsNone(a["physical_qualification_confirmed"])
        self.assertFalse(a["learner_skill_assessed"])
        self.assertIn("noncontact safety education", doc("15.05", "later-packet.md"))

    def test_no_stop_and_universal_legal_claim_remain_disqualifying(self):
        b = FIX["providers"]["B"]
        self.assertFalse(b["stop_allowed"])
        self.assertTrue(b["universal_legal_claim"])
        self.assertFalse(FIX["providers"]["C"]["self_protection_scope"])
        self.assertIn("home-intruder", (SOURCE / "SOURCES.md").read_text())

    def test_all_seven_outdoor_priorities_have_work(self):
        for priority in FIX["outdoor"]["priorities"]:
            self.assertIn(priority, doc("15.06").lower())
        self.assertFalse(FIX["outdoor"]["fire_authorized"])
        self.assertFalse(FIX["outdoor"]["stream_drinkable_established"])
        self.assertIn("not authorized", doc("15.06"))

    def test_outdoor_turnaround_and_return_arithmetic(self):
        x = FIX["outdoor"]
        self.assertGreater(minutes(x["continuation_cutoff"], x["checkpoint"]), 0)
        expected = datetime.strptime(x["checkpoint"], "%H:%M") + timedelta(
            minutes=x["return_minutes"]
        )
        self.assertEqual(expected.strftime("%H:%M"), x["expected_return"])
        self.assertIn(x["expected_return"], doc("15.06", "later-packet.md"))

    def test_fresh_outdoor_case_uses_different_times(self):
        x = FIX["fresh_checks"]["outdoor"]
        self.assertEqual(minutes(x["checkpoint"], x["expected_return"]), x["return_minutes"])
        self.assertIn(x["expected_return"], doc("15.06", "check-answers.md"))

    def test_water_assistance_is_not_removed_by_orientation_gain(self):
        x = FIX["water"]
        self.assertTrue(x["float_aid"] and x["swim_aid"] and x["exit_assisted"])
        self.assertFalse(x["tread_assessed"])
        self.assertIn("Update orientation only", doc("15.07", "later-packet.md"))
        self.assertIn("20 seconds", doc("15.07"))
        self.assertEqual(x["swim_metres"], 8)

    def test_water_environment_and_dryland_limits(self):
        self.assertFalse(FIX["water"]["river_competence_established"])
        self.assertFalse(FIX["water"]["actual_aquatic_assessment"])
        self.assertIn("cannot establish demonstrated aquatic skill", doc("15.07"))
        self.assertIn("stable safe position", doc("15.07"))


class TravelAndCyberTests(unittest.TestCase):
    def test_initial_lodging_is_over_budget_with_reserve(self):
        x = FIX["travel"]
        self.assertEqual(x["initial_room"] + x["fare"], x["initial_cost"])
        self.assertEqual(x["initial_cost"] - (x["funds"] - x["reserve"]), x["initial_shortfall"])
        self.assertIn("short by 3", doc("15.08", "later-packet.md"))

    def test_later_lodging_preserves_reserve(self):
        x = FIX["travel"]
        self.assertEqual(x["later_room"] + x["fare"], x["later_cost"])
        self.assertEqual(x["funds"] - x["later_cost"], x["later_remainder"])
        self.assertEqual(x["later_remainder"] - x["reserve"], x["later_above_reserve"])
        self.assertIn("17 remains", doc("15.08", "later-packet.md"))

    def test_timetable_and_recovery_do_not_clear_medicine(self):
        x = FIX["travel"]
        self.assertGreater(minutes(x["last_bus"], x["arrival"]), 0)
        self.assertGreater(minutes(x["arrival"], x["desk_closes"]), 0)
        self.assertIsNone(x["medicine_permission"])
        self.assertFalse(x["mobile_voice_tested"])
        self.assertIn(
            "Medicine import permission is still unresolved", doc("15.08", "later-packet.md")
        )

    def test_fresh_travel_budget(self):
        x = FIX["fresh_checks"]["travel"]
        self.assertEqual(x["room"] + x["fare"] - (x["funds"] - x["reserve"]), x["shortfall"])
        self.assertIn("short by 5", doc("15.08", "check-answers.md"))

    def test_cyber_signal_rows_match_independent_domains(self):
        self.assertEqual(re.findall(r"^\| (M\d) \|", doc("15.09"), re.M), FIX["cyber"]["signals"])
        self.assertFalse(FIX["cyber"]["code_disclosed"])
        self.assertTrue(FIX["cyber"]["document_exposed"])
        self.assertIsNone(FIX["cyber"]["later_identity_misuse"])

    def test_containment_does_not_close_payment_or_work_incident(self):
        x = FIX["cyber"]
        self.assertEqual(len(x["personal_actions"]), 4)
        self.assertEqual(x["posted_payment"], 46)
        self.assertIsNone(x["refund"])
        self.assertTrue(x["it_acknowledged"])
        self.assertIsNone(x["work_resolution"])
        self.assertIn("46-unit payment still unresolved", doc("15.09", "later-packet.md"))

    def test_fresh_partial_refund_keeps_unresolved_balance(self):
        x = FIX["fresh_checks"]["cyber"]
        self.assertEqual(x["payment"] - x["refunded"], x["unresolved"])
        self.assertIn("50 units remain unresolved", doc("15.09", "check-answers.md"))


class CapacityAndCommunityTests(unittest.TestCase):
    def test_initial_reserve_covers_minimum_not_full_session(self):
        x = FIX["contingency"]
        available = minutes(x["starts"], x["initial_end"])
        self.assertEqual(available - x["minimum_minutes"], x["initial_spare"])
        self.assertLess(available, x["full_minutes"])
        self.assertIn("10 minutes spare", doc("15.10", "later-packet.md"))

    def test_changed_reserve_requires_cancel_and_agreed_handback(self):
        x = FIX["contingency"]
        self.assertEqual(
            x["minimum_minutes"] - minutes(x["starts"], x["later_end"]), x["later_shortfall"]
        )
        self.assertEqual(x["later_decision"], "cancel")
        self.assertTrue(x["handback_requires_agreement"])
        self.assertIn("ownership is unresolved", doc("15.10", "later-packet.md"))

    def test_fresh_capacity_shortfall(self):
        x = FIX["fresh_checks"]["contingency"]
        self.assertEqual(x["minimum"] - x["available"], x["shortfall"])
        self.assertIn("5-minute shortfall", doc("15.10", "check-answers.md"))

    def test_stock_and_transport_are_separate_capacities(self):
        x = FIX["community"]
        self.assertEqual(x["stock"] - sum(x["requests"].values()), x["remaining"])
        self.assertIsNone(x["B_transport_suitable"])
        self.assertFalse(x["Ren_available_later"])
        self.assertTrue(x["Mara_acknowledged_gap"])
        self.assertFalse(x["transport_fulfilled"])
        self.assertIn("one unallocated", doc("15.11", "later-packet.md"))

    def test_consent_no_response_and_task_acceptance_limits(self):
        x = FIX["community"]
        self.assertFalse(x["C_contact_consent"])
        self.assertIsNone(x["B_response"])
        self.assertTrue(x["Jo_task_accepted"])
        self.assertIsNone(x["Jo_task_completed"])
        self.assertFalse(x["actual_participation"])
        self.assertIn(x["checkin_deadline"], doc("15.11"))

    def test_fresh_stock_shortfall(self):
        x = FIX["fresh_checks"]["community"]
        self.assertEqual(sum(x["requests"]) - x["stock"], x["shortfall"])
        self.assertIn("one pack is short", doc("15.11", "check-answers.md"))


class HealthBystanderWorkListeningTests(unittest.TestCase):
    def test_notice_chronology_changes_air_action_not_diagnosis(self):
        x = FIX["health"]
        self.assertLess(x["notices"][0]["day"], x["notices"][1]["day"])
        self.assertNotEqual(x["notices"][0]["hazard"], x["notices"][1]["hazard"])
        self.assertIsNone(x["in_person_arrangement_confirmed"])
        self.assertFalse(x["real_outbreak_claim"])
        self.assertIsNone(x["fixed_isolation_days"])
        self.assertIn("Day 2 at 12:00", doc("15.12", "later-packet.md"))

    def test_access_does_not_require_diagnosis(self):
        x = FIX["health"]
        self.assertEqual(x["telephone_capacity"], x["participants"])
        self.assertFalse(x["diagnosis_required"])
        self.assertIn(
            "available to everyone without health disclosure", doc("15.12", "later-packet.md")
        )

    def test_fresh_recipient_confirmation_not_whole_group(self):
        x = FIX["fresh_checks"]["health"]
        self.assertEqual(x["recipients"] - x["confirmed"], x["unconfirmed"])
        self.assertIn("other nine remain unconfirmed", doc("15.12", "check-answers.md"))

    def test_five_strategies_and_refusal_are_not_forced_escalation(self):
        for strategy in FIX["bystander"]["strategies"]:
            self.assertIn(strategy, doc("15.13").lower())
        self.assertFalse(FIX["bystander"]["company_consent"])
        self.assertFalse(FIX["bystander"]["publication_consent"])
        self.assertIn("Accept the answer and allow space", doc("15.13", "later-packet.md"))

    def test_delegation_acknowledgment_is_not_outcome(self):
        self.assertTrue(FIX["bystander"]["steward_received"])
        self.assertIsNone(FIX["bystander"]["support_outcome"])
        self.assertFalse(FIX["bystander"]["actual_victim_consent"])
        self.assertIn("No outcome", doc("15.13", "later-packet.md"))

    def test_work_cases_include_authority_and_isolation_gap(self):
        self.assertEqual(re.findall(r"^\| (W\d) \|", doc("15.14"), re.M), FIX["work"]["cards"])
        self.assertTrue(FIX["work"]["machine_switched_off"])
        self.assertFalse(FIX["work"]["isolation_verified"])
        self.assertFalse(FIX["work"]["learner_maintenance_authorized"])
        self.assertIsNone(FIX["work"]["cabinet_repaired"])

    def test_work_substitution_rechecks_exit_and_no_physical_machine_task(self):
        self.assertEqual(FIX["work"]["physical_practice"], "ordinary sheets only")
        self.assertIn("blocks the exit", doc("15.14", "later-packet.md"))
        self.assertIn("Do not operate any real controls", doc("15.14"))

    def test_listening_correction_preserves_interest_and_time_limit(self):
        x = FIX["listening"]
        self.assertTrue(x["timed_ticket_acceptable"])
        self.assertIn(x["corrected_deadline"], doc("16.01", "later-packet.md"))
        self.assertIn(x["later_choice"], doc("16.01", "later-packet.md"))
        self.assertEqual(x["requested_suggestions"], 1)

    def test_listening_fictional_confirmation_is_not_observer_evidence(self):
        self.assertFalse(FIX["listening"]["actual_speaker_confirmation"])
        self.assertEqual(FIX["listening"]["confirmation"], "supplied fictional response")
        self.assertIn("never observer evidence", doc("16.01", "later-packet.md"))
        self.assertIn("understanding is not clearly confirmed", doc("16.01", "check-answers.md"))


class RetrievalTests(unittest.TestCase):
    def test_actual_temporary_copy_and_retrieval_of_both_harmless_cards(self):
        cards = {
            "15.08/materials/station-card.txt": (
                "21:00",
                "95 tokens",
                "Preserve 10",
                "voice untested",
            ),
            "15.10/materials/fallback-card.txt": (
                "17:40",
                "17:50",
                "Minimum session 30",
                "until 18:40",
                "may use paper agenda and cancel",
            ),
        }
        for relative, answers in cards.items():
            original = SOURCE / relative
            before = hashlib.sha256(original.read_bytes()).hexdigest()
            with tempfile.TemporaryDirectory() as temp:
                copied = Path(temp) / original.name
                shutil.copyfile(original, copied)
                del copied
                retrieved = (Path(temp) / original.name).read_text()
                for answer in answers:
                    self.assertIn(answer, retrieved)
                self.assertIn("FICTIONAL", retrieved)
            self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
