"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/civic-participation"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"20.{i:02}" for i in range(1, 13)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 129)
        self.assertEqual(COHORT["additional_companions_after"], 141)
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
        for domain in ("20",):
            self.assertEqual(
                (ROOT / f"docs/authoring/exercises/{domain}.yaml").read_bytes(),
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_bytes(),
            )

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads((ROOT / "docs/authoring/family-stewardship/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "19.15")
        self.assertEqual(previous["additional_companions_after"], 129)
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

    def test_cross_context_classification_and_exact_domain_boundary(self):
        for e in COHORT["entries"]:
            self.assertEqual(e["classification"]["applicability"], "cross_context_core")
            self.assertEqual(
                e["classification"]["normative_status"], "cross_tradition_core_or_broadly_recurrent"
            )
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn(e["professional_boundary"], doc(e["id"], name))
            self.assertIn("fiction", doc(e["id"]).lower())
            self.assertIn("does not compel a belief", doc(e["id"]))

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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 17)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["sections"])
            self.assertTrue(s["limits"])
            for cid in s["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{s['id']}", doc(cid))
        by_id = {s["id"]: s for s in sources}
        self.assertIn("linked manifesto PDF not inspected", by_id["S01"]["limits"])
        self.assertIn("U.S. federal context only", by_id["S02"]["limits"])
        self.assertIn("Council of Europe reproduction", by_id["S05"]["limits"])
        self.assertIn("England context", by_id["S08"]["limits"])
        self.assertIn("Article only", by_id["S11"]["limits"])
        self.assertIn("Overview only", by_id["S12"]["limits"])
        self.assertIn("not legally enforceable", by_id["S15"]["limits"])
        self.assertIn("April 2021 version", by_id["S16"]["limits"])

    def test_fiction_and_human_review_boundaries(self):
        self.assertTrue(FIX["all_responses_supplied_fiction"])
        self.assertFalse(FIX["actual_participant_evidence"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        for cid in IDS:
            self.assertIn("Supplied fiction", doc(cid, "later-packet.md"))
            self.assertIn("remain pending", doc(cid, "SCOPE-MAP.md"))
        self.assertIn("not a content-acceptance receipt", (SOURCE / "README.md").read_text())

    def test_successor_contract_preserves_protected_paths(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        if contract["batch"]["id"] == "M6K-CIVIC-PARTICIPATION-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/family-stewardship/**",
                "tests/test_m6k_family_stewardship_sources.py",
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

    def test_exact_coverage_partition_and_remaining_backlog(self):
        coverage = COHORT["source_coverage"]
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        canonical = {e["id"] for d in catalog["curriculum"]["domains"] for e in d["competencies"]}
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        implemented = set(contract["implemented_competency_ids"])
        paths = coverage["prior_companion_guides"]
        # Freeze predecessor directories: later cohorts must not rewrite this historical partition.
        directories = {str(Path(p).parent.parent) for p in paths}
        actual_paths = {
            str(p.relative_to(ROOT))
            for directory in directories
            for p in (ROOT / directory).glob("*/learner-guide.md")
        }
        self.assertEqual(set(paths), actual_paths)
        prior = {Path(p).parent.name for p in paths}
        self.assertEqual(len(paths), len(prior))
        self.assertEqual((len(implemented), len(prior)), (108, 129))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 249, 134))
        self.assertEqual(coverage["remaining_count"], len(remaining))
        self.assertEqual(coverage["remaining_before"], len(remaining) + len(IDS))
        self.assertEqual(coverage["additional_after"], len(prior) + len(IDS))
        self.assertEqual(coverage["covered_unique_count"], len(covered))
        self.assertEqual(coverage["remaining_by_domain"], dict(Counter(x[:2] for x in remaining)))
        earlier = sorted(x for x in remaining if x[:2] in {"07", "08"})
        self.assertEqual(coverage["earlier_domains_07_08_remaining"], earlier)
        self.assertEqual(len(earlier), 25)
        legacy_pending = set(contract["retained_legacy_competency_ids"]) - prior - set(IDS)
        self.assertEqual(legacy_pending, {"08.02", "26.01"})
        self.assertEqual(set(coverage["legacy_without_new_companion"]), legacy_pending)
        self.assertTrue(legacy_pending <= remaining)


class CaseTests(unittest.TestCase):
    def test_interdependence_timely_return_does_not_equal_repair(self):
        f = FIX["interdependence"]
        self.assertEqual((date.fromisoformat(f["due"]) - date.fromisoformat(f["returned"])).days, 1)
        self.assertTrue(f["return_accepted"] and f["damage_logged"])
        self.assertFalse(f["repair_done_known"] or f["unsolicited_donation"])
        self.assertIn("No repair", doc("20.01", "later-packet.md"))
        self.assertIn("return and report were accepted", doc("20.01", "check-answers.md"))

    def test_interdependence_six_branches_preserve_unknown_inputs(self):
        f = FIX["interdependence"]
        for facet in (
            "Infrastructure",
            "Labor",
            "Law",
            "Knowledge",
            "Environment",
            "Inherited institutions",
        ):
            self.assertIn(facet, doc("20.01"))
        self.assertTrue(f["catalog_maintenance"])
        self.assertFalse(f["pay_known"] or f["energy_known"])
        self.assertIn("unlimited debt", doc("20.01", "later-packet.md"))

    def test_authority_operator_advisor_and_budget_powers_are_distinct(self):
        f = FIX["authority"]
        self.assertEqual(f["policy"], f["budget"])
        self.assertNotEqual(f["ordinary_schedule"], f["budget"])
        self.assertNotEqual(f["advisory"], f["budget"])
        self.assertIn("cannot itself appropriate funds", doc("20.02"))
        self.assertIn("not a description of Pima County", doc("20.02"))

    def test_authority_inquiry_reply_and_unsent_policy_draft_are_distinct(self):
        f = FIX["authority"]
        self.assertTrue(f["operational_inquiry_sent"] and f["manager_reply"] and f["clerk_draft"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "clerk_sent",
                    "election_details_verified",
                    "complaint_scope_verified",
                    "hours_changed",
                    "budget_changed",
                )
            )
        )
        self.assertIn("not sent", doc("20.02", "later-packet.md"))
        self.assertIn("Courts are not the default", doc("20.02"))

    def test_rights_identity_swap_restores_equal_separate_capacity(self):
        f = FIX["rights"]
        self.assertLess(f["b_initial_cap"], f["b_requested"])
        self.assertTrue(f["identity_swap"] and f["biased_cap_removed"] and f["separate_times"])
        self.assertEqual(f["capacity"] - f["a_requested"], 6)
        self.assertEqual(f["capacity"] - f["b_requested"], 6)
        self.assertIn("not a joint forty-eight-person event", doc("20.03", "later-packet.md"))

    def test_rights_relevant_threat_does_not_invent_a_final_ruling(self):
        f = FIX["rights"]
        self.assertTrue(f["c_confirmed_threat"] and f["c_referred"])
        self.assertFalse(f["c_final_assessment"] or f["c_permanent_exclusion"] or f["actual_event"])
        self.assertIn("No final risk assessment", doc("20.03", "later-packet.md"))
        self.assertIn("way to challenge factual error", doc("20.03", "later-packet.md"))

    def test_structure_attendance_difference_is_percentage_points(self):
        f = FIX["structure"]
        before = 100 * f["before_attended"] / f["before_interested"]
        after = 100 * f["after_attended"] / f["after_interested"]
        self.assertEqual((before, after, after - before), (50, 70, 20))
        self.assertEqual(f["after_attended"] - f["before_attended"], 8)
        self.assertIn("twenty-percentage-point difference", doc("20.04", "later-packet.md"))

    def test_structure_confounds_and_access_report_do_not_prove_cause(self):
        f = FIX["structure"]
        self.assertTrue(
            f["stepfree_changed"] and f["reminder_changed"] and f["one_user_access_report"]
        )
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "same_people_known",
                    "demographic_data",
                    "causal_effect_established",
                    "transit_resolved",
                    "signup_resolved",
                )
            )
        )
        self.assertIn("does not isolate the room's effect", doc("20.04", "later-packet.md"))
        self.assertIn("Do not infer race, class, disability", doc("20.04"))

    def test_difference_corrected_representation_preserves_conviction(self):
        f = FIX["difference"]
        self.assertTrue(
            f["initial_caricature"] and f["corrected_summary"] and f["jo_accepts_summary"]
        )
        self.assertFalse(f["jo_conviction_changed"] or f["bea_conviction_changed"])
        self.assertIn("not an end to online information", doc("20.05", "later-packet.md"))
        self.assertIn("Neither is asked to adopt", doc("20.05", "later-packet.md"))

    def test_difference_accepted_files_do_not_become_posting_or_policy(self):
        f = FIX["difference"]
        self.assertTrue(f["roles_accepted"] and f["matching_files_accepted"])
        self.assertFalse(
            any(f[k] for k in ("printed", "posted", "attendance_known", "policy_changed"))
        )
        self.assertIn("No actual printing, posting", doc("20.05", "later-packet.md"))
        for fact in (
            "Reading Together",
            "18 October, 15:00\u201316:00",
            "Cedar Hall, Room B",
            "Event Desk at Cedar Hall",
        ):
            self.assertIn(fact, doc("20.05"))

    def test_service_rework_does_not_create_extra_output_or_erase_overrun(self):
        f = FIX["service"]
        self.assertEqual(f["first_initial_usable"] + f["first_corrected"], f["unit_size"])
        self.assertEqual(f["first_minutes"] + f["rework_minutes"] - f["offered_minutes"], 2)
        self.assertEqual(f["units_accepted"] * f["unit_size"], 20)
        self.assertLess(f["second_minutes"], f["offered_minutes"])
        self.assertIn("do not create twelve distinct notices", doc("20.06", "later-packet.md"))
        for fact in (
            "ten identical copies",
            "Repair Stories / 12 October, 14:00\u201315:00",
            "Local History Hour / 26 October, 14:00\u201315:00",
            "Hub Event Desk",
            "18-point",
        ):
            self.assertIn(fact, doc("20.06"))

    def test_service_two_units_and_known_review_leave_recurring_burden_open(self):
        f = FIX["service"]
        self.assertEqual(
            (date.fromisoformat(f["dates"][1]) - date.fromisoformat(f["dates"][0])).days, 14
        )
        self.assertEqual(f["first_review_minutes"] + f["second_review_minutes"], 10)
        self.assertFalse(
            f["other_support_minutes_known"]
            or f["third_unit_accepted"]
            or f["recurring_role_accepted"]
        )
        self.assertIn("no duration for any additional", doc("20.06", "later-packet.md"))
        self.assertIn(
            "no recurring role or third unit is accepted", doc("20.06", "later-packet.md")
        )

    def test_help_selected_support_leaves_submission_and_device_with_person(self):
        f = FIX["help"]
        self.assertTrue(
            all(
                f[k]
                for k in (
                    "large_print_requested",
                    "explanation_requested",
                    "copy_retained",
                    "contact_located",
                    "device_retained",
                    "draft_kept",
                )
            )
        )
        self.assertFalse(
            f["credentials_handled"]
            or f["submitted"]
            or f["seat_confirmed"]
            or f["capacity_determined"]
        )
        self.assertIn("Nothing is submitted, no seat is confirmed", doc("20.07", "later-packet.md"))

    def test_help_ongoing_support_is_allowed_but_offer_is_not_scheduling(self):
        f = FIX["help"]
        self.assertTrue(f["future_help_offered"])
        self.assertFalse(f["future_help_requested"] or f["future_help_scheduled"])
        self.assertIn(
            "Continuing chosen assistance can preserve agency", doc("20.07", "check-answers.md")
        )
        self.assertIn("Gratitude alone", doc("20.07", "later-packet.md"))

    def test_organizing_removals_preserve_unknown_notice_and_accepted_roles(self):
        f = FIX["organizing"]
        self.assertEqual(f["expired"] + f["current"] + f["undated"], f["total"])
        self.assertEqual(f["removed"], f["expired"])
        self.assertEqual(f["total"] - f["removed"], 9)
        self.assertTrue(f["roles_accepted"] and f["owner_approved"])
        self.assertFalse(f["undated_resolved"])
        self.assertIn("Nine remain: eight current and one undated", doc("20.08", "later-packet.md"))

    def test_organizing_retry_and_future_maintenance_have_bounded_evidence(self):
        f = FIX["organizing"]
        self.assertFalse(f["first_test_success"] or f["weekly_check_done"])
        self.assertTrue(
            f["heading_enlarged"]
            and f["retry_success"]
            and f["same_user"]
            and f["weekly_check_accepted"]
        )
        self.assertIn("familiarity could contribute", doc("20.08", "later-packet.md"))
        self.assertIn("Reading Circle, 16 October at 18:00", doc("20.08"))
        self.assertIn("Reading Circle at 18:00", doc("20.08", "later-packet.md"))
        self.assertIn("Leave the undated item in place", doc("20.08"))
        self.assertIn("future check has not happened", doc("20.08", "later-packet.md"))

    def test_information_copies_and_conditional_plan_are_not_observed_reopening(self):
        f = FIX["information"]
        self.assertEqual(f["copy_count"], 5)
        self.assertEqual(f["independent_observed_reopening"], 0)
        self.assertTrue(f["inspection_condition"])
        self.assertLess(f["original_date"], f["initial_closure"])
        self.assertEqual(f["planned_reopen"], f["extended_closure"])
        self.assertFalse(f["new_reopen_known"])
        self.assertIn("dependent repetitions", doc("20.09", "later-packet.md"))

    def test_information_correction_and_update_reach_original_fictional_audience(self):
        f = FIX["information"]
        self.assertEqual(f["original_audience"], f["correction_audience"])
        self.assertEqual(f["original_audience"], f["update_audience"])
        self.assertTrue(f["correction_sent_in_fiction"] and f["update_sent_in_fiction"])
        self.assertFalse(f["readership_known"])
        self.assertEqual(f["real_transmissions"], 0)
        self.assertIn("same three fictional recipients", doc("20.09", "later-packet.md"))
        self.assertIn("Sent does not mean read", doc("20.09", "check-answers.md"))

    def test_commons_whole_instruction_area_is_repaired_before_success_claim(self):
        f = FIX["commons"]
        self.assertTrue(
            f["first_label_covers_instruction"]
            and f["position_corrected"]
            and f["damage_instruction_found"]
        )
        self.assertEqual(f["later_correct"], f["later_returns"])
        self.assertEqual(f["other_users"] + int(f["first_user_retried"]), f["later_returns"])
        self.assertFalse(f["matched_baseline"])
        self.assertIn("no defensible before/after error rate", doc("20.10", "later-packet.md"))

    def test_commons_reuse_and_accepted_stewardship_do_not_measure_ecology(self):
        f = FIX["commons"]
        self.assertTrue(f["available_card_reused"] and f["weekly_accepted"])
        self.assertFalse(f["weekly_done"] or f["environment_measured"] or f["new_penalty"])
        self.assertIn(
            "no waste mass, emissions, ecological restoration", doc("20.10", "later-packet.md")
        )
        self.assertIn("Copying information need not consume the original", doc("20.10"))

    def test_pluralism_access_and_conduct_rules_do_not_require_conformity(self):
        f = FIX["pluralism"]
        self.assertTrue(
            f["ideological_condition_removed"]
            and f["equivalent_channel"]
            and f["common_deadline"]
            and f["dissent_retained"]
        )
        self.assertTrue(f["harassment_referred"])
        self.assertFalse(
            f["harassment_resolved"] or f["consensus"] or f["legal_compliance_established"]
        )
        self.assertIn("Targeted harassment still goes", doc("20.11", "later-packet.md"))
        self.assertIn("Silence is not consent", doc("20.11"))

    def test_pluralism_alternative_slot_and_paper_booking_do_not_invent_draw_or_use(self):
        f = FIX["pluralism"]
        self.assertTrue(f["alternative_slot_accepted"] and f["paper_booking"])
        self.assertFalse(f["random_draw_performed"] or f["actual_room_use"])
        self.assertIn("no draw is performed", doc("20.11", "later-packet.md"))
        self.assertIn("no actual room use", doc("20.11", "later-packet.md"))

    def test_institutions_response_denominators_do_not_make_nonresponse_negative(self):
        f = FIX["institutions"]
        self.assertEqual(100 * f["respondents"] / f["invited"], 25)
        self.assertEqual(100 * f["positive"] / f["respondents"], 80)
        self.assertEqual(100 * f["positive"] / f["invited"], 20)
        self.assertEqual(f["invited"] - f["respondents"], 150)
        self.assertEqual(f["respondents"] - f["positive"], 10)
        self.assertFalse(
            f["neutral_negative_breakdown_known"]
            or f["comparison_group"]
            or f["representative_city_estimate"]
        )
        self.assertIn("not established causal benefit", doc("20.12", "later-packet.md"))
        self.assertIn("150 nonrespondents' views remain unknown", doc("20.12", "later-packet.md"))

    def test_institutions_handoffs_and_correction_status_remain_separate(self):
        f = FIX["institutions"]
        self.assertEqual(
            (f["first_population_expansion"], f["causal_escalation"]), ("newspaper", "party")
        )
        self.assertTrue(
            f["agency_sponsor_disclosed"]
            and f["newsroom_draft"]
            and f["party_draft"]
            and f["university_draft"]
        )
        self.assertFalse(f["court_involved"] or f["platform_ranking_known"])
        self.assertEqual(f["requests_sent"] + f["acknowledgments"] + f["published_corrections"], 0)
        self.assertIn("Both remain unsent", doc("20.12", "later-packet.md"))
        self.assertIn("does not by itself establish fraud", doc("20.12", "later-packet.md"))
