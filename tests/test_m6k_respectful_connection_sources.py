"""Source integrity and case regressions only; these checks never grade learners."""

import hashlib
import json
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/respectful-connection"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"16.{i:02}" for i in range(14, 19)] + [f"17.{i:02}" for i in range(1, 8)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


def minutes(start, end):
    return int(
        (datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60
    )


def arrive(start, walk):
    return (datetime.strptime(start, "%H:%M") + timedelta(minutes=walk)).strftime("%H:%M")


class IntegrityTests(unittest.TestCase):
    def test_exact_ids_and_separate_source_counts(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 81)
        self.assertEqual(COHORT["additional_companions_after"], 93)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertTrue(COHORT["source_only"])

    def test_canonical_entries_and_seven_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        entries = [
            e for d in catalog["curriculum"]["domains"] for e in d["competencies"] if e["id"] in IDS
        ]
        self.assertEqual(entries, COHORT["entries"])
        self.assertEqual(len(COHORT["input_sha256"]), 7)
        for path, digest in COHORT["input_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_current_recovery_identity_for_both_domains(self):
        for domain in ("16", "17"):
            self.assertEqual(
                (ROOT / f"docs/authoring/exercises/{domain}.yaml").read_bytes(),
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_bytes(),
            )

    def test_sequence_and_legacy_membership(self):
        previous = json.loads(
            (ROOT / "docs/authoring/communication-influence/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "16.13")
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        self.assertFalse(set(IDS) & set(contract["implemented_competency_ids"]))
        self.assertEqual(set(IDS) & set(contract["retained_legacy_competency_ids"]), {"17.03"})
        self.assertEqual(COHORT["legacy_companion_ids"], ["17.03"])

    def test_five_files_and_three_separate_checks(self):
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

    def test_canonical_scope_classification_and_measurement(self):
        for e in COHORT["entries"]:
            scope = doc(e["id"], "SCOPE-MAP.md")
            for field in ("name", "scope", "evidence_of_progress"):
                self.assertIn(e[field], scope)
            for key in ("applicability", "normative_status"):
                self.assertIn(e["classification"][key], scope)
            for mode in e["classification"]["formation_modes"]:
                self.assertIn(mode, scope)
            self.assertIn(e["measurement"]["minimum_standard"], scope)
            self.assertIn("not a new exercise scoring rule", scope)
            self.assertIn("Human dignity is never scored", scope)

    def test_local_links_and_anchors_resolve(self):
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target:
                    continue
                name, _, anchor = target.partition("#")
                dest = (path.parent / name).resolve()
                self.assertTrue(dest.is_file(), f"{path}: {target}")
                if anchor:
                    self.assertRegex(dest.read_text(), rf"(?mi)^## {re.escape(anchor)}$")

    def test_primary_source_coverage_and_read_limits(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 16)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["sections"])
            self.assertTrue(s["limits"])
        for sid in ("S06", "S11", "S13"):
            s = next(s for s in sources if s["id"] == sid)
            self.assertIn("abstract", s["limits"].lower())
        self.assertIn("selected pages", next(s for s in sources if s["id"] == "S14")["type"])

    def test_fiction_and_formal_review_boundaries(self):
        self.assertTrue(FIX["all_responses_supplied_fiction"])
        self.assertFalse(FIX["actual_participant_evidence"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        for cid in IDS:
            self.assertIn("not actual participant evidence", doc(cid, "later-packet.md"))
            self.assertIn("remain pending", doc(cid, "SCOPE-MAP.md"))
        self.assertIn("not a content-acceptance receipt", (SOURCE / "README.md").read_text())

    def test_current_contract_scope_and_ci_boundary(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        if contract["batch"]["id"] == "M6K-RESPECTFUL-CONNECTION-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/communication-influence/**",
                "tests/test_m6k_communication_influence_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])
        self.assertTrue(all(isinstance(x, str) for x in contract["acceptance"]))

    def test_legacy_actions_fields_and_completion_unchanged(self):
        legacy = yaml.safe_load(
            (ROOT / "data/practices/protocols/17/PRACTICE-FRIENDSHIP-01.yaml").read_text()
        )
        self.assertEqual(legacy["intervention"]["duration_days"], 14)
        actions = legacy["intervention"]["actions"]
        self.assertEqual(
            [a["stable_id"] for a in actions],
            [f"PRACTICE-FRIENDSHIP-01-A{i}" for i in range(1, 4)],
        )
        self.assertIn("at least ten minutes primarily listening", actions[0]["instructions"])
        self.assertEqual(actions[2]["due_within_days"], 7)
        self.assertEqual(
            actions[1]["evidence_rules"]["primary_markers"], ["future_interaction_scheduled"]
        )
        self.assertEqual(
            legacy["completion_and_review"]["completion_rules"]["minimum_completed"], 2
        )
        self.assertEqual(
            legacy["evidence_and_scoring"]["check_in_fields"],
            [
                "user_initiated",
                "moved_beyond_transactional",
                "follow_up_question_asked",
                "meaningful_information_shared",
                "future_interaction_scheduled",
                "follow_up_within_seven_days",
                "internal_resistance",
                "expected_reciprocity",
                "observed_reciprocity",
            ],
        )
        self.assertIn("app's original fields", doc("17.03"))

    def test_verification_hashes_cover_exact_source_set(self):
        verification = json.loads((SOURCE / "verification.json").read_text())
        expected = {
            str(p.relative_to(ROOT))
            for p in SOURCE.rglob("*")
            if p.is_file() and p.name != "verification.json"
        }
        self.assertEqual(set(verification["source_sha256"]), expected)
        for path, digest in verification["source_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        test_file = Path(__file__)
        self.assertEqual(
            hashlib.sha256(test_file.read_bytes()).hexdigest(),
            verification["focused_test_sha256"],
        )


class CaseTests(unittest.TestCase):
    def test_courtesy_arrival_and_delayed_repair(self):
        f = FIX["courtesy"]
        self.assertEqual(arrive(f["bus"], f["walk"]), "13:48")
        self.assertEqual(minutes("13:48", f["doors"]), 2)
        late = arrive(f["delayed_bus"], f["walk"])
        self.assertEqual(late, "14:04")
        self.assertEqual(minutes(f["start"], late), f["delay_minutes"])
        self.assertIn(late, doc("16.14", "later-packet.md"))
        self.assertIn("helper will open it", doc("16.14", "later-packet.md"))

    def test_courtesy_access_and_permission_not_inferred(self):
        self.assertIsNone(FIX["courtesy"]["photo_permission_received"])
        self.assertFalse(FIX["courtesy"]["access_fully_verified"])
        self.assertIn("communication aid", doc("16.14"))
        self.assertIn("acknowledges the update", doc("16.14", "later-packet.md"))

    def test_pressure_demand_does_not_create_agreement(self):
        f = FIX["pressure"]
        self.assertIsNone(f["gift_terms"])
        self.assertTrue(f["shift_voluntary"])
        self.assertFalse(f["shift_accepted"])
        self.assertFalse(f["others_opinions_verified"])
        self.assertIsNone(f["motive"])
        self.assertIn("leave the shift unaccepted", doc("16.15", "later-packet.md"))

    def test_all_seven_pressure_mechanisms_and_safety_stop(self):
        text = doc("16.15").lower()
        for mechanism in (
            "guilt",
            "intimidation",
            "gaslighting",
            "love-bombing",
            "false urgency",
            "triangulation",
            "exploitative reciprocity",
        ):
            self.assertIn(mechanism, text)
        self.assertEqual(
            FIX["pressure"]["monitoring_threat_branch"], "stop_confrontation_rehearsal"
        )
        self.assertIn("End the confrontation rehearsal", doc("16.15"))
        self.assertIn("genuine deadlines", text)

    def test_indirect_disconfirmation_and_authority(self):
        f = FIX["indirect"]
        self.assertIsNone(f["Ari_initial_disposition"])
        self.assertEqual(f["Ari_later_disposition"], "declined")
        self.assertFalse(f["Ari_authority_for_others"])
        self.assertIsNone(f["others_participation"])
        self.assertIn("not Ari's volunteered disposition", doc("16.16", "later-packet.md"))

    def test_indirect_privacy_and_silence(self):
        self.assertFalse(FIX["indirect"]["reason_disclosed"])
        self.assertFalse(FIX["indirect"]["silence_is_consent"])
        self.assertIn("No personal reason is then disclosed", doc("16.16", "later-packet.md"))
        self.assertIn("unconfirmed", doc("16.16", "later-packet.md"))

    def test_adaptation_material_facts_and_consultation_conflict(self):
        f = FIX["adaptation"]
        self.assertEqual(minutes(f["start"], f["end"]), 60)
        self.assertEqual(
            (
                datetime.fromisoformat(f["committee_meeting"])
                - datetime.fromisoformat(f["reply_date"])
            ).days,
            1,
        )
        self.assertEqual(datetime.fromisoformat(f["date"]).strftime("%A"), "Saturday")
        self.assertEqual(f["places"], 12)
        self.assertEqual(f["cost"], 0)
        self.assertTrue(f["optional"])
        self.assertFalse(f["volunteer_commitment"])
        self.assertIn("one day after", doc("16.17", "later-packet.md"))

    def test_adaptation_seven_dimensions_and_unchanged_limits(self):
        for facet in (
            "Directness",
            "Hierarchy",
            "Turn-taking",
            "Emotion",
            "Time",
            "Privacy",
            "Formality",
        ):
            self.assertIn(facet, doc("16.17"))
        for key in ("second_session_confirmed", "phone_sharing_permission", "deadline_extended"):
            self.assertFalse(FIX["adaptation"][key])
        self.assertIn("Do not say the deadline has moved", doc("16.17", "later-packet.md"))

    def test_access_understanding_is_not_submission(self):
        f = FIX["access"]
        self.assertTrue(f["comprehension"])
        self.assertFalse(f["submission_received"])
        self.assertEqual(f["timeout_seconds"], 30)
        self.assertIsNone(f["retest"])
        self.assertIn("thirty seconds", doc("16.18", "later-packet.md"))
        self.assertIn("submission as failed", doc("16.18", "later-packet.md"))

    def test_access_helper_cannot_replace_choice_or_unknowns(self):
        f = FIX["access"]
        self.assertNotEqual(f["choice"], f["helper_choice"])
        self.assertIsNone(f["noise_level"])
        self.assertFalse(f["real_participation"])
        for facet in (
            "interpreter",
            "Plain language",
            "Captions",
            "AAC",
            "Written follow-up",
            "Accessible formats",
        ):
            self.assertIn(facet, doc("16.18"))
        self.assertIn("Do not replace them", doc("16.18", "later-packet.md"))

    def test_initiation_permission_is_bounded(self):
        f = FIX["initiation"]
        self.assertTrue(f["shared_table_allowed"])
        self.assertTrue(f["quiet_requested"])
        self.assertFalse(f["continued_personal_questions_welcome"])
        self.assertFalse(f["future_contact_agreed"])
        self.assertFalse(f["rejection_inferred"])
        self.assertIn(
            "not an invitation to continue personal questions", doc("17.01", "later-packet.md")
        )

    def test_initiation_contexts_and_rehearsal_boundary(self):
        for context in ("stranger", "acquaintance", "coworker", "neighbor", "peer"):
            self.assertIn(f"**{context}**", doc("17.01"))
        self.assertIn("real initiation not attempted", doc("17.01", "check-answers.md"))

    def test_selection_observations_do_not_create_shared_time(self):
        f = FIX["selection"]
        self.assertEqual(f["observations"], 3)
        self.assertNotEqual(f["proposed_time"], f["offered_time"])
        self.assertFalse(f["shared_time_agreed"])
        self.assertFalse(f["indoor_room_confirmed"])
        self.assertIn("not a scheduled activity", doc("17.02", "later-packet.md"))

    def test_selection_one_repair_and_four_directions(self):
        self.assertTrue(FIX["selection"]["one_interruption_correction"])
        self.assertFalse(FIX["selection"]["future_conduct_known"])
        for direction in ("Deepen", "Remain limited", "Repair", "End"):
            self.assertIn(f"**{direction}**", doc("17.02"))
        self.assertIn(
            "not evidence that interruptions can never recur", doc("17.02", "later-packet.md")
        )

    def test_maintenance_actual_listening_and_declined_invitation(self):
        f = FIX["maintenance"]
        self.assertGreaterEqual(f["primarily_listening_minutes"], f["listening_minimum"])
        self.assertEqual(f["duration_days"], 14)
        self.assertFalse(f["activity_scheduled"])
        self.assertIn("not mutually scheduled", doc("17.03", "later-packet.md"))

    def test_maintenance_six_day_followup_does_not_require_project_success(self):
        f = FIX["maintenance"]
        days = (
            datetime.fromisoformat(f["followup"]) - datetime.fromisoformat(f["conversation"])
        ).days
        self.assertEqual(days, 6)
        self.assertLessEqual(days, f["followup_limit_days"])
        self.assertFalse(f["project_completed"])
        self.assertIn("six days", doc("17.03", "later-packet.md"))
        self.assertIn("does not require a completed drawing", doc("17.03", "later-packet.md"))

    def test_support_original_round_trip_and_margin(self):
        f = FIX["support"]
        total = f["outward"] + f["deposit"] + f["back"]
        self.assertEqual(total, 35)
        self.assertEqual(minutes(f["original_start"], f["return_by"]) - total, 10)
        self.assertTrue(f["book_handed_over"])
        self.assertIn("thirty-five minutes", doc("17.04"))

    def test_support_changed_window_includes_return_journey(self):
        f = FIX["support"]
        available = minutes(f["changed_start"], f["return_by"])
        self.assertEqual(available, 20)
        self.assertEqual(f["outward"] + f["deposit"] + f["back"] - available, 15)
        self.assertFalse(f["renegotiated"])
        self.assertFalse(f["errand_completed"])
        self.assertIn("fifteen minutes short", doc("17.04", "later-packet.md"))

    def test_reciprocity_agreed_help_and_extra_offer(self):
        f = FIX["reciprocity"]
        self.assertEqual(f["agreed_minutes"], 5)
        self.assertTrue(f["review_received"])
        self.assertEqual(f["room_verified"], "Room F")
        self.assertEqual(f["extra_offer_minutes"], 40)
        self.assertFalse(f["extra_accepted"])
        self.assertFalse(f["extra_performed"])
        self.assertIn("offered, not accepted or performed", doc("17.05", "later-packet.md"))

    def test_reciprocity_does_not_invent_repayment_or_longitudinal_proof(self):
        f = FIX["reciprocity"]
        self.assertFalse(f["reciprocal_task_agreed"])
        self.assertFalse(f["durable_mutuality_established"])
        self.assertIn("numerical inequality", doc("17.05", "check-prompts.md"))
        self.assertIn("does not determine dignity", doc("17.05", "check-answers.md"))

    def test_boundaries_action_promise_and_unknown_conduct(self):
        f = FIX["boundaries"]
        for key in ("left_exchange", "host_contacted", "host_promise"):
            self.assertTrue(f[key])
        self.assertIsNone(f["host_followthrough"])
        self.assertIsNone(f["Jules_changed_conduct"])
        self.assertIn(
            "changed behavior by Jules is not established", doc("17.06", "later-packet.md")
        )

    def test_boundaries_threat_dependency_changes_route(self):
        f = FIX["boundaries"]
        self.assertTrue(f["safe_exit_in_ordinary_case"])
        self.assertEqual(f["threat_dependency_branch"], "individualized_support")
        self.assertFalse(f["actual_exit_evidence"])
        self.assertIn("not a confrontation", doc("17.06", "later-packet.md"))
        self.assertIn("temporarily", doc("17.06"))
        self.assertIn("not consent to harm", doc("17.06"))

    def test_hospitality_partial_success_and_pending_rule_retest(self):
        f = FIX["hospitality"]
        self.assertTrue(f["music_off"])
        self.assertTrue(f["reported_conversation_easier"])
        self.assertTrue(f["watch_choice_respected"])
        self.assertFalse(f["rules_understood"])
        self.assertFalse(f["rules_repair_retested"])
        self.assertIn("repair has not yet been tested", doc("17.07", "later-packet.md"))

    def test_hospitality_food_and_universal_claim_limits(self):
        self.assertFalse(FIX["hospitality"]["allergen_free_guarantee"])
        self.assertFalse(FIX["hospitality"]["universal_access"])
        self.assertIn("cannot guarantee freedom from allergens", doc("17.07"))
        self.assertIn(
            "Do not turn a partial success into universal accessibility",
            doc("17.07", "check-answers.md"),
        )

    def test_fresh_arrival_window(self):
        f = FIX["fresh"]
        arrival = arrive(f["courtesy_bus"], f["courtesy_walk"])
        self.assertEqual(arrival, "09:54")
        self.assertEqual(minutes(f["courtesy_doors"], arrival), 4)
        self.assertEqual(minutes(arrival, f["courtesy_start"]), 6)
        self.assertIn(arrival, doc("16.14", "check-answers.md"))

    def test_fresh_legacy_short_listening_and_late_followup(self):
        f = FIX["fresh"]
        self.assertEqual(f["listening"] + f["logistics"], 15)
        self.assertLess(f["listening"], FIX["maintenance"]["listening_minimum"])
        days = (
            datetime.fromisoformat(f["late_followup"])
            - datetime.fromisoformat(FIX["maintenance"]["conversation"])
        ).days
        self.assertEqual(days, 8)
        self.assertGreater(days, FIX["maintenance"]["followup_limit_days"])
        self.assertIn("Eight days elapsed", doc("17.03", "check-answers.md"))

    def test_fresh_support_shortfall(self):
        f = FIX["fresh"]
        self.assertEqual(
            f["errand_outward"] + f["errand_task"] + f["errand_back"] - f["errand_available"], 3
        )
        self.assertIn("three more than available", doc("17.04", "check-answers.md"))


if __name__ == "__main__":
    unittest.main()
