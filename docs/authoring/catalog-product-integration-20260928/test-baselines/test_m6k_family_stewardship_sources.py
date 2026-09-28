"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/family-stewardship"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"19.{i:02}" for i in range(4, 16)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


def minutes(start, end):
    return int(
        (datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60
    )


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 117)
        self.assertEqual(COHORT["additional_companions_after"], 129)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )

    def test_exact_canonical_entries_and_four_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        entries = [
            e for d in catalog["curriculum"]["domains"] for e in d["competencies"] if e["id"] in IDS
        ]
        self.assertEqual(entries, COHORT["entries"])
        self.assertEqual(len(COHORT["input_sha256"]), 4)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_current_recovery_identity(self):
        for domain in ("19",):
            self.assertEqual(
                (ROOT / f"docs/authoring/exercises/{domain}.yaml").read_bytes(),
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_bytes(),
            )

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads((ROOT / "docs/authoring/partnership-family/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "19.03")
        self.assertEqual(previous["additional_companions_after"], 117)
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
            self.assertIn("No reproductive, parenting or care role is compulsory", doc(e["id"]))
            if e["id"] in ("19.07", "19.09", "19.10", "19.11", "19.13", "19.15"):
                self.assertIn("authorized", doc(e["id"]).lower())

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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 19)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["sections"])
            self.assertTrue(s["limits"])
            for cid in s["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{s['id']}", doc(cid))
        by_id = {s["id"]: s for s in sources}
        self.assertIn("not individual-care guidance", by_id["S02"]["limits"])
        self.assertIn("Direct DCS page body was blocked", by_id["S07"]["limits"])
        self.assertIn("care/custody/control", by_id["S08"]["limits"])
        self.assertIn("United Kingdom contact routes are not transferred", by_id["S09"]["limits"])
        self.assertIn("correction_url", by_id["S11"])
        self.assertIn("England and Wales", by_id["S13"]["limits"])
        self.assertIn("attempted refresh failed", by_id["S14"]["limits"])
        self.assertIn("Landing page only", by_id["S17"]["limits"])

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
        if contract["batch"]["id"] == "M6K-FAMILY-STEWARDSHIP-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/partnership-family/**",
                "tests/test_m6k_partnership_family_sources.py",
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
    def test_reproductive_rehearsal_access_and_transport_are_distinct(self):
        f = FIX["reproductive"]
        self.assertFalse(f["mara_contacted"])
        self.assertTrue(f["elise_access_reply"] and f["transport_offered"])
        self.assertFalse(f["elise_booked"] or f["elise_pregnancy_known"])
        self.assertFalse(f["transport_accepted"] or f["transport_done"])
        self.assertIn("Transport remains only an offer", doc("19.04", "later-packet.md"))

    def test_reproductive_booking_is_not_assessment_or_population_cutoff(self):
        f = FIX["reproductive"]
        self.assertTrue(f["omar_ren_contacted"] and f["consultation_booked"])
        self.assertEqual(f["consultation_date"], "2026-10-22")
        self.assertFalse(f["assessment_done"] or f["prognosis_known"])
        self.assertTrue(f["birthday_rule_withdrawn"])
        self.assertIn("No clinician has assessed", doc("19.04", "later-packet.md"))
        self.assertIn("individual circumstances", doc("19.04", "check-answers.md"))

    def test_postpartum_accepted_task_does_not_expand_care_authority(self):
        f = FIX["postpartum"]
        self.assertLess(f["cancelled"], f["original_meal"])
        self.assertEqual(minutes(f["original_meal"], f["actual_meal"]), 15)
        self.assertEqual(f["accepted_meal"], f["actual_meal"])
        self.assertTrue(f["dev_specific_task_accepted"])
        self.assertFalse(f["dev_entered"] or f["dev_infant_care"])
        self.assertIn("does not enter or provide infant care", doc("19.05", "later-packet.md"))

    def test_postpartum_handoff_and_tabletop_cannot_prove_recovery(self):
        f = FIX["postpartum"]
        self.assertEqual(minutes(f["care_start"], f["care_return"]), 60)
        self.assertTrue(
            f["sal_competent_authorized"] and f["start_acknowledged"] and f["return_acknowledged"]
        )
        self.assertFalse(f["tabletop_real_call"] or f["tabletop_actual_symptom"])
        self.assertTrue(f["quiet_useful_report"])
        self.assertFalse(f["next_day_coverage"] or f["clinical_recovery_assessed"])
        self.assertIn(
            "no medical recovery or mental-health assessment", doc("19.05", "later-packet.md")
        )

    def test_grief_refusal_and_kept_practical_promise_coexist(self):
        f = FIX["grief"]
        self.assertLess(f["disclosure"], f["meal"])
        self.assertTrue(f["call_declined"] and f["meal_accepted"] and f["delivery_done"])
        self.assertEqual(f["agreed_time"], f["delivered_time"])
        self.assertFalse(f["pregnancy_known"] or f["grief_reduced_known"])
        self.assertIn("without waiting for conversation", doc("19.06", "later-packet.md"))

    def test_grief_space_does_not_authorize_future_contact_or_partner_disclosure(self):
        f = FIX["grief"]
        self.assertEqual(f["space_requested_weeks"], 2)
        self.assertTrue(f["future_message_drafted"])
        self.assertFalse(
            f["future_message_sent"] or f["future_message_scheduled"] or f["ash_offer_made"]
        )
        self.assertIn("not an agreed follow-up", doc("19.06", "later-packet.md"))
        self.assertIn("Ash's experience remains unknown", doc("19.06", "later-packet.md"))

    def test_belonging_preserves_private_origin_and_revisable_labels(self):
        f = FIX["belonging"]
        self.assertTrue(
            f["kit_private_keepsake"] and f["rowan_chosen_name"] and f["name_card_removed"]
        )
        self.assertFalse(f["public_explanation"] or f["forced_parent_title"] or f["loyalty_debate"])
        self.assertIn("removed without a loyalty discussion", doc("19.07", "later-packet.md"))

    def test_belonging_unknown_permission_does_not_create_contact_or_powers(self):
        f = FIX["belonging"]
        self.assertFalse(f["image_permission_known"] or f["image_used"] or f["new_contact"])
        self.assertTrue(f["neutral_symbol_used"])
        self.assertFalse(f["ari_legal_powers_granted"] or f["attachment_assessed"])
        self.assertIn("no care or legal authority changes", doc("19.07", "later-packet.md"))
        self.assertIn("not themselves confer legal powers", doc("19.07", "check-answers.md"))

    def test_safeguarding_route_retains_exact_jurisdiction_and_circumstances(self):
        f = FIX["safeguarding"]
        self.assertEqual(f["jurisdiction"], "Arizona, United States")
        self.assertTrue(
            f["outside_indian_reservation"] and f["alleged_person_care_custody_control"]
        )
        self.assertEqual(f["role"], "school personnel")
        self.assertIn(f["receiving_phone"], doc("19.08"))
        self.assertEqual(f["emergency"], "911")
        self.assertFalse(f["information_page_is_report"])
        self.assertIn("without care, custody or control", doc("19.08"))
        self.assertIn("not itself a reporting form", doc("19.08"))

    def test_safeguarding_corrected_outline_is_not_report_or_safety_outcome(self):
        f = FIX["safeguarding"]
        self.assertTrue(f["outline_corrected"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "secrecy_promised",
                    "investigation_first",
                    "internal_delay_accepted",
                    "real_call",
                    "submitted",
                    "acknowledgment",
                    "safety_outcome_known",
                )
            )
        )
        self.assertIn(
            "No call, portal submission, agency acknowledgment", doc("19.08", "later-packet.md")
        )
        self.assertIn("Do not delay a required report", doc("19.08", "check-answers.md"))

    def test_discipline_adult_model_does_not_double_count_books(self):
        f = FIX["discipline"]
        a, b = f["first"], f["second"]
        self.assertEqual(
            a["adult_model_moved_books"] + a["child_returned"] + a["adult_returned"], f["books"]
        )
        self.assertEqual(b["shared_returned"] + b["child_independent_returned"], f["books"])
        self.assertEqual(a["child_returned"], 1)
        self.assertEqual(b["child_independent_returned"], 0)
        self.assertIn("without moving a book", doc("19.09", "later-packet.md"))

    def test_discipline_changed_conditions_and_help_do_not_justify_escalation(self):
        f = FIX["discipline"]
        self.assertTrue(f["first"]["help_requested"] and f["second"]["tired"])
        self.assertTrue(f["first"]["picture_cue"] and f["second"]["picture_cue"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "alphabetic_order_required",
                    "essentials_withheld",
                    "affection_withheld",
                    "task_increased",
                    "general_independence",
                )
            )
        )
        self.assertIn("does not establish regression", doc("19.09", "later-packet.md"))
        self.assertIn(
            "Essentials and affection are not compliance rewards", doc("19.09", "check-answers.md")
        )

    def test_teaching_owner_authority_and_missing_location_govern_retry(self):
        f = FIX["teaching"]
        self.assertTrue(f["owner_instruction_known"])
        self.assertFalse(
            f["forwarded_authority_known"]
            or f["forwarded_instruction_followed"]
            or f["second_location_known"]
        )
        self.assertTrue(f["second_clarification_rehearsed"])
        self.assertFalse(f["actual_owner_contacted"] or f["real_return"])
        self.assertIn(
            "does not leave the book outside or invent a destination",
            doc("19.10", "later-packet.md"),
        )

    def test_teaching_own_words_access_and_feedback_are_not_global_independence(self):
        f = FIX["teaching"]
        self.assertTrue(f["own_thanks_used"] and f["picture_support_retained"])
        self.assertTrue(
            f["learner_feedback_supplied_fiction"]
            and f["instruction_revised"]
            and f["revised_explanation_retried"]
        )
        self.assertFalse(f["global_independence"])
        self.assertIn(
            "mixed the required damage report with an optional greeting",
            doc("19.10", "later-packet.md"),
        )
        self.assertIn("without forcing belief", doc("19.10", "check-answers.md"))

    def test_elder_observation_does_not_establish_diagnosis_capacity_or_authority(self):
        f = FIX["elder"]
        self.assertEqual(f["missed_reminders"], 2)
        self.assertTrue(f["ruth_chooses_alex"] and f["large_print_accepted"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "clinical_assessment",
                    "dementia_diagnosed",
                    "capacity_determined",
                    "takeover_authorized",
                    "legal_guidance_obtained",
                )
            )
        )
        self.assertIn(
            "no authority over communications, care or finances is granted",
            doc("19.11", "later-packet.md"),
        )

    def test_elder_successful_call_and_admin_inquiry_leave_coverage_and_clinical_gaps(self):
        f = FIX["elder"]
        self.assertEqual(f["weekly_call_limit"], 1)
        self.assertTrue(f["call_done"] and f["admin_inquiry"])
        self.assertFalse(
            f["appointment_attended_known"] or f["respite_contacted"] or f["backup_accepted"]
        )
        self.assertIn("one-call weekly limit remains", doc("19.11", "later-packet.md"))
        self.assertIn(
            "An administrative reply is not clinical advice", doc("19.11", "check-answers.md")
        )

    def test_labor_whole_unit_transfer_and_resource_account(self):
        f = FIX["labor"]
        self.assertTrue(f["unit_accepted"] and f["unit_completed"] and f["access_correct"])
        self.assertEqual(f["budget"] - f["spent"], 4)
        self.assertEqual(f["reminders"], 0)
        self.assertFalse(f["rescue"])
        self.assertIn("Four units remain unspent", doc("19.12", "later-packet.md"))

    def test_labor_optional_redo_and_unaccepted_other_work_remain_visible(self):
        f = FIX["labor"]
        self.assertEqual(f["redo_minutes"], 12)
        self.assertFalse(f["redo_required"])
        self.assertTrue(f["next_unit_accepted"])
        self.assertFalse(
            f["next_unit_done"]
            or f["other_redistribution_accepted"]
            or f["whole_family_fairness_established"]
        )
        self.assertIn(
            "personal preference, not an agreed completion condition",
            doc("19.12", "later-packet.md"),
        )

    def test_restructuring_no_unapproved_substitution_or_child_messenger(self):
        f = FIX["restructuring"]
        self.assertLess(f["delay_report"], f["original"])
        self.assertFalse(f["ellis_approved"] or f["ellis_collected"] or f["child_messenger"])
        self.assertTrue(f["fallback_maintained"] and f["morgan_authorized"])
        self.assertIn("Ellis does not collect", doc("19.13", "later-packet.md"))
        self.assertIn(
            "authorized protected channel or intermediary", doc("19.13", "check-answers.md")
        )

    def test_restructuring_actual_handoff_not_revised_arrival_or_new_agreement(self):
        f = FIX["restructuring"]
        self.assertTrue(f["transfer_completed"])
        self.assertEqual(minutes(f["original"], f["actual"]), 25)
        self.assertEqual(minutes(f["revised"], f["actual"]), 5)
        self.assertFalse(f["standing_change_agreed"] or f["conflict_resolved"])
        self.assertIn("transfer and confirmation occur then", doc("19.13", "later-packet.md"))

    def test_heritage_revised_form_is_transmitted_in_fiction(self):
        f = FIX["heritage"]
        self.assertTrue(
            all(
                f[k]
                for k in (
                    "story_told",
                    "word_translated",
                    "safe_gesture",
                    "hurtful_joke_removed",
                    "wording_revised",
                    "revised_telling_done",
                    "alternative_memory_allowed",
                )
            )
        )
        self.assertIn("gives the brief telling again", doc("19.14", "later-packet.md"))
        self.assertFalse(
            f["actual_participant_feedback"] or f["whole_family_belonging_established"]
        )

    def test_heritage_optout_and_recording_permissions_remain_specific(self):
        f = FIX["heritage"]
        self.assertTrue(f["optout_respected"])
        self.assertFalse(f["photo_permission_known"] or f["photo_used"] or f["recording"])
        self.assertIn("No audio or video is recorded", doc("19.14", "later-packet.md"))
        self.assertIn("separate appropriate agreement", doc("19.14", "check-answers.md"))

    def test_respite_actual_handoff_preserves_care_and_limits_coverage(self):
        f = FIX["respite"]
        self.assertTrue(
            all(
                f[k]
                for k in (
                    "coverage_accepted",
                    "competent_authorized",
                    "teachback",
                    "start_acknowledged",
                    "return_acknowledged",
                )
            )
        )
        self.assertLess(f["arrival"], f["actual_start"])
        self.assertEqual(minutes(f["scheduled_start"], f["scheduled_end"]), 120)
        self.assertEqual(minutes(f["actual_start"], f["actual_return"]), 105)
        self.assertFalse(f["essential_gap"])
        self.assertIn("There is no uncovered interval", doc("19.15", "later-packet.md"))

    def test_respite_rest_is_not_booked_slot_or_resolved_burnout(self):
        f = FIX["respite"]
        coverage = minutes(f["actual_start"], f["actual_return"])
        self.assertEqual(coverage - f["optional_monitoring_minutes"], f["reported_rest_minutes"])
        self.assertEqual(f["reported_rest_minutes"], 95)
        self.assertFalse(
            f["recurring_accepted"] or f["service_contacted"] or f["burnout_resolved_known"]
        )
        self.assertIn("has not accepted a recurring commitment", doc("19.15", "later-packet.md"))
        self.assertIn("not a diagnosis or cure", doc("19.15", "check-answers.md"))


if __name__ == "__main__":
    unittest.main()
