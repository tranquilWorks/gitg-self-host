"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/partnership-family"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"18.{i:02}" for i in range(6, 15)] + [f"19.{i:02}" for i in range(1, 4)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


def minutes(start, end):
    return int(
        (datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60
    )


def arrive(start, duration):
    return (datetime.strptime(start, "%H:%M") + timedelta(minutes=duration)).strftime("%H:%M")


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 105)
        self.assertEqual(COHORT["additional_companions_after"], 117)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )

    def test_exact_canonical_entries_and_six_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        entries = [
            e for d in catalog["curriculum"]["domains"] for e in d["competencies"] if e["id"] in IDS
        ]
        self.assertEqual(entries, COHORT["entries"])
        self.assertEqual(len(COHORT["input_sha256"]), 6)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_current_recovery_identity(self):
        for domain in ("18", "19"):
            self.assertEqual(
                (ROOT / f"docs/authoring/exercises/{domain}.yaml").read_bytes(),
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_bytes(),
            )

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads(
            (ROOT / "docs/authoring/belonging-partnership/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "18.05")
        self.assertEqual(previous["additional_companions_after"], 105)
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        self.assertFalse(set(IDS) & set(contract["implemented_competency_ids"]))
        self.assertFalse(set(IDS) & set(contract["retained_legacy_competency_ids"]))
        self.assertEqual(COHORT["legacy_companion_ids"], [])

    def test_five_files_and_three_fresh_cases_each(self):
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
            for name in ("check-prompts.md", "check-answers.md"):
                self.assertEqual(re.findall(r"^(\d)\. ", doc(cid, name), re.M), ["1", "2", "3"])

    def test_canonical_scope_classification_and_measurement(self):
        for e in COHORT["entries"]:
            scope = doc(e["id"], "SCOPE-MAP.md")
            for key in ("name", "scope", "evidence_of_progress"):
                self.assertIn(e[key], scope)
            for key in ("applicability", "normative_status"):
                self.assertIn(e["classification"][key], scope)
            for mode in e["classification"]["formation_modes"]:
                self.assertIn(mode, scope)
            for kind in e["measurement"]["preferred_evidence_types"]:
                self.assertIn(kind, scope)
            self.assertIn(e["measurement"]["minimum_standard"], scope)
            self.assertTrue(e["measurement"]["not_proof_of_moral_worth"])
            self.assertIn("not a new exercise scoring rule", scope)
            self.assertIn("Human dignity is never scored", scope)

    def test_all_role_conditional_with_exact_domain_boundaries(self):
        for e in COHORT["entries"]:
            self.assertEqual(e["classification"]["applicability"], "role_conditional")
            self.assertEqual(e["classification"]["normative_status"], "role_conditional")
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn(e["professional_boundary"], doc(e["id"], name))
            self.assertIn("fiction", doc(e["id"]).lower())
            if e["id"].startswith("18."):
                self.assertIn("single life", doc(e["id"]).lower())
            elif e["id"] in ("19.02", "19.03"):
                self.assertIn("authorized", doc(e["id"]).lower())
            else:
                self.assertIn("within your own control", doc(e["id"]).lower())
                self.assertIn("Family contact is not compulsory", doc(e["id"]))

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

    def test_source_coverage_and_honest_inspection_limits(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 16)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["sections"])
            self.assertTrue(s["limits"])
            for cid in s["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{s['id']}", doc(cid))
        by_id = {s["id"]: s for s in sources}
        for sid in ("S01", "S02", "S03"):
            self.assertIn("abstract", by_id[sid]["limits"].lower())
        self.assertIn("England and Wales only", by_id["S08"]["limits"])
        self.assertIn("Theory", by_id["S11"]["limits"])
        self.assertIn("2015", by_id["S12"]["author"])
        self.assertIn("Clinical form fields", by_id["S13"]["limits"])

    def test_fiction_and_human_review_boundaries(self):
        self.assertTrue(FIX["all_responses_supplied_fiction"])
        self.assertFalse(FIX["actual_participant_evidence"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        for cid in IDS:
            self.assertIn("not actual participant evidence", doc(cid, "later-packet.md"))
            self.assertIn("remain pending", doc(cid, "SCOPE-MAP.md"))
        self.assertIn("not a content-acceptance receipt", (SOURCE / "README.md").read_text())

    def test_successor_contract_preserves_protected_paths(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        if contract["batch"]["id"] == "M6K-PARTNERSHIP-FAMILY-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/belonging-partnership/**",
                "tests/test_m6k_belonging_partnership_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])
        self.assertTrue(all(isinstance(x, str) for x in contract["acceptance"]))

    def test_verification_covers_exact_source_and_test_bytes(self):
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


class CaseTests(unittest.TestCase):
    def test_stages_actual_trial_and_review_order(self):
        f = FIX["stages"]
        self.assertEqual(minutes(f["start"], f["end"]), 20)
        self.assertEqual(f["completed_meetings"], len(f["trial_dates"]))
        self.assertLess(max(f["trial_dates"]), f["review"])
        self.assertLess(f["review"], f["work_end"])
        self.assertIn("both twenty-minute", doc("18.06", "later-packet.md"))

    def test_stages_conditional_outing_does_not_erase_breach(self):
        f = FIX["stages"]
        self.assertTrue(f["next_tuesday_agreed"])
        self.assertFalse(f["replacement_care_confirmed"])
        self.assertFalse(f["outing_occurred"])
        self.assertFalse(f["dinner_repair_completed"])
        self.assertIn("conditional proposal", doc("18.06", "later-packet.md"))
        self.assertIn("not all future needs or the unresolved repair", doc("18.06"))

    def test_labor_canceled_order_not_double_counted(self):
        f = FIX["labor"]
        spent = f["actual_purchase"] + (f["canceled_order"] if f["cancellation_charged"] else 0)
        self.assertEqual(spent, 9)
        self.assertEqual(f["budget"] - spent, 51)
        self.assertEqual(minutes(f["delivery_latest"], f["delivery_window_start"]), 60)
        self.assertIn("do not count 48 as spent", doc("18.07", "later-packet.md"))

    def test_labor_overrun_and_unknown_reminder_burden(self):
        f = FIX["labor"]
        self.assertEqual(f["actual_minutes"]["Dani"] - f["offered_minutes"]["Dani"], 10)
        self.assertEqual(f["reminders"], 2)
        self.assertIsNone(f["reminder_minutes"])
        self.assertTrue(f["meal_done"])
        self.assertFalse(f["next_cycle_done"])
        self.assertIn("Reminder", doc("18.07", "SCOPE-MAP.md"))

    def test_repair_wait_and_restitution_are_actual(self):
        f = FIX["repair"]
        self.assertEqual(minutes(f["pickup"], f["wait_end"]), 20)
        self.assertTrue(f["acknowledged"])
        self.assertEqual(f["restitution_paid"], f["taxi_cost"])
        self.assertIn("payment occurs", doc("18.08", "later-packet.md"))

    def test_repair_message_is_not_received_confirmation(self):
        f = FIX["repair"]
        self.assertLess(f["next_message"], f["departure"])
        self.assertLess(f["departure"], f["message_read"])
        self.assertFalse(f["confirmation_before_departure"])
        self.assertEqual(f["next_wait_minutes"], 0)
        self.assertFalse(f["trust_restored"])
        self.assertIn("reduced practical harm", doc("18.08", "later-packet.md"))

    def test_consent_specificity_withdrawal_and_no_contact(self):
        f = FIX["consent"]
        self.assertTrue(f["adult_fiction"] and f["no_contact"])
        self.assertTrue(f["A"]["handholding"])
        self.assertFalse(f["A"]["kissing"])
        self.assertTrue(f["A"]["renewed_pursuit"])
        self.assertTrue(all(f["B"].values()))
        self.assertIn("no-contact rehearsal", doc("18.09"))

    def test_consent_pressure_and_sleep_cannot_supply_permission(self):
        f = FIX["consent"]
        self.assertTrue(f["C"]["pressure"])
        self.assertFalse(f["C"]["freely_given_new_agreement"])
        self.assertTrue(f["D"]["asleep"])
        self.assertFalse(f["D"]["activity_started"] or f["D"]["later_conversation"])
        self.assertIn(
            "deleting one threatening sentence cannot establish freedom",
            doc("18.09", "later-packet.md"),
        )

    def test_communication_prevention_inquiry_not_clinical_answer(self):
        f = FIX["communication"]
        self.assertLess(f["inquiry"], f["appointment"])
        self.assertTrue(f["booked"])
        self.assertFalse(f["attended"] or f["clinical_question_answered"])
        self.assertIn("infection prevention", doc("18.10"))
        self.assertIn("does not answer the clinical question", doc("18.10", "later-packet.md"))

    def test_communication_agreement_not_used_practice_or_independent_report(self):
        f = FIX["communication"]
        self.assertLessEqual(f["conversation_minutes"], 20)
        self.assertTrue(f["jokes_boundary_agreed"] and f["aftercare_practice_agreed"])
        self.assertFalse(f["aftercare_practice_used"])
        self.assertEqual(f["later_joke_self_report_occasions"], 2)
        self.assertFalse(f["independent_later_feedback"])
        self.assertIn("no later intimacy", doc("18.10", "later-packet.md"))

    def test_fidelity_notification_precedes_declined_meeting(self):
        f = FIX["fidelity"]
        self.assertLess(f["invitation"], f["notification"])
        self.assertLess(f["notification"], f["proposed_meeting"])
        self.assertTrue(f["invitation_declined"])
        self.assertFalse(f["meeting_booked"] or f["password_agreed"])
        self.assertIn("before responding", doc("18.11", "later-packet.md"))

    def test_fidelity_proposed_expansion_not_an_operative_promise(self):
        f = FIX["fidelity"]
        self.assertTrue(f["all_messages_rule_proposed"])
        self.assertFalse(f["all_messages_rule_accepted"] or f["review_done"])
        self.assertFalse(f["prior_breach_supplied"])
        self.assertIn("unaccepted expansion", doc("18.11", "later-packet.md"))
        self.assertIn("retroactively", doc("18.11", "check-answers.md"))

    def test_endings_care_precedes_logistics_meeting(self):
        f = FIX["endings"]
        self.assertLess(f["inquiry"], f["care_visit"])
        self.assertLess(f["care_visit"], f["planning_conversation"])
        self.assertTrue(f["care_owner_accepted"] and f["care_visit_done"])
        self.assertFalse(f["planning_done"] or f["future_care_arranged"])
        self.assertIn("completes it on 8 October", doc("18.12", "later-packet.md"))

    def test_endings_acknowledgment_does_not_resolve_lease_or_property(self):
        f = FIX["endings"]
        self.assertTrue(f["acknowledgment"])
        self.assertFalse(f["substantive_lease_answer"] or f["table_allocated"])
        self.assertIn("no substantive lease advice", doc("18.12", "later-packet.md"))
        self.assertIn("England and Wales", doc("18.12"))

    def test_diversity_preserves_commitment_without_orientation_inference(self):
        f = FIX["diversity"]
        self.assertTrue(f["personal_exclusivity_retained"])
        self.assertFalse(f["orientation_implies_structure"])
        self.assertIn("orientation does not establish", doc("18.13", "later-packet.md"))
        self.assertIn("freely given agreement", doc("18.13", "check-answers.md"))

    def test_diversity_fictional_reader_not_actual_social_outcome(self):
        f = FIX["diversity"]
        self.assertTrue(f["fictional_reader_confirms_revision"])
        self.assertFalse(f["reply_sent"] or f["picnic_attended"] or f["actual_human_review"])
        self.assertIn("Rae has not received the reply", doc("18.13", "later-packet.md"))

    def test_intentions_distinct_wishes_and_bounded_authority(self):
        f = FIX["intentions"]
        self.assertNotEqual(f["asha"], f["luca"])
        self.assertFalse(f["shared_parenting_plan"] or f["records_access_authorized"])
        self.assertTrue(f["cost_task_accepted"])
        self.assertLessEqual(f["cost_research_actual_minutes"], f["cost_research_offered_minutes"])
        self.assertIn("does not authorize record access", doc("18.14", "later-packet.md"))

    def test_intentions_booking_not_fertility_or_cost_confirmation(self):
        f = FIX["intentions"]
        self.assertLess(f["inquiry"], f["appointment"])
        self.assertLess(f["appointment"], f["review"])
        self.assertTrue(f["booked"])
        self.assertFalse(f["attended"] or f["individual_cost_confirmed"] or f["review_done"])
        self.assertIn(
            "no consultation or individual clinical assessment", doc("18.14", "later-packet.md")
        )

    def test_patterns_two_observations_do_not_supply_family_history(self):
        f = FIX["patterns"]
        self.assertEqual(len(f["observed_dates"]), 2)
        self.assertLess(max(f["observed_dates"]), f["boundary_date"])
        self.assertTrue(f["direct_answer"] and f["new_invitation_sent"])
        self.assertIn("not a childhood history", doc("19.01"))
        self.assertFalse(f["whole_family_changed"])

    def test_patterns_recurrence_repaired_without_retracting_limit(self):
        f = FIX["patterns"]
        self.assertLess(f["boundary_date"], f["recurrence_date"])
        self.assertLess(f["recurrence_date"], f["meal_date"])
        self.assertTrue(f["unsupported_inference_corrected"] and f["insult_apologized"])
        self.assertFalse(f["limit_retracted"] or f["meal_occurred"])
        self.assertIn("does not retract", doc("19.01", "later-packet.md"))

    def test_parenting_item_account_does_not_credit_adult_work_to_child(self):
        f = FIX["parenting"]
        a, b = f["first"], f["second"]
        self.assertTrue(f["authorized_role"])
        self.assertEqual(
            a["books"] + a["toys"],
            a["adult_modeled"]
            + a["child_placed"]
            + a["adult_remaining_books"]
            + a["adult_remaining_toys"],
        )
        self.assertEqual(b["books"] + b["toys"], b["adult_modeled"] + b["child_placed"])
        self.assertEqual(a["child_placed"], b["child_placed"])
        self.assertIn("Do not credit all seven items", doc("19.02", "later-packet.md"))

    def test_parenting_changed_conditions_not_general_independence(self):
        f = FIX["parenting"]
        a, b = f["first"], f["second"]
        self.assertLess(b["verbal_reminders"], a["verbal_reminders"])
        self.assertTrue(b["picture_cue"] and a["story_kept"] and b["story_kept"])
        self.assertFalse(f["global_independence_established"] or f["attachment_assessed"])
        self.assertIn("does not isolate which adjustment", doc("19.02", "later-packet.md"))
        self.assertIn("Without that role, use the complete fiction only", doc("19.02"))

    def test_caregiving_late_backup_requires_actual_confirmation(self):
        f = FIX["caregiving"]
        self.assertEqual(arrive(f["original_pickup"], f["travel_minutes"]), "10:05")
        self.assertEqual(minutes("10:05", f["target"]), 10)
        self.assertLess(f["backup_trigger"], f["backup_accepted"])
        self.assertLess(f["backup_accepted"], f["replacement_pickup"])
        self.assertEqual(arrive(f["replacement_pickup"], f["travel_minutes"]), f["actual_arrival"])
        self.assertEqual(minutes(f["target"], f["actual_arrival"]), 5)
        self.assertTrue(f["clinic_confirms_late_checkin"] and f["recipient_accepts"])
        self.assertIn("five minutes after", doc("19.03", "later-packet.md"))

    def test_caregiving_cost_capacity_and_unknown_clinical_result(self):
        f = FIX["caregiving"]
        self.assertEqual(2 * f["fare_each_way"], f["actual_fare"])
        self.assertEqual(f["budget"] - f["actual_fare"], 20)
        self.assertEqual(f["helper_actual_minutes"] - f["helper_available_minutes"], 10)
        self.assertTrue(f["return_completed"] and f["recipient_voice_respected"])
        self.assertFalse(f["clinical_outcome_known"] or f["expanded_backup_implemented"])
        self.assertIn("No clinical answer is disclosed", doc("19.03", "later-packet.md"))


if __name__ == "__main__":
    unittest.main()
