"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/work-delivery-voice"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"21.{i:02}" for i in range(8, 20)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 153)
        self.assertEqual(COHORT["additional_companions_after"], 165)
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

    def test_selected_current_recovery_entries_match(self):
        for domain in ("21",):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads(
            (ROOT / "docs/authoring/civic-work-foundations/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "21.07")
        self.assertEqual(previous["additional_companions_after"], 153)
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

    def test_context_sensitive_and_absent_canonical_boundary(self):
        for e in COHORT["entries"]:
            self.assertEqual(e["classification"]["applicability"], "context_sensitive")
            self.assertEqual(
                e["classification"]["normative_status"], "cross_tradition_core_or_broadly_recurrent"
            )
            self.assertNotIn("professional_boundary", e)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn(
                    "canonical record has no professional_boundary field", doc(e["id"], name)
                )
            self.assertIn("Fiction and no attempt are legitimate", doc(e["id"]))
        self.assertEqual(COHORT["skipped_implemented_ids"], [])
        self.assertNotIn("21.03", IDS)

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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 15)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-24")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        by_id = {source["id"]: source for source in sources}
        self.assertIn("February 2, 2026", by_id["S08"]["limits"])
        self.assertIn(
            "Live service availability was not independently verified", by_id["S08"]["limits"]
        )
        self.assertIn("not inspected", by_id["S09"]["limits"])
        self.assertIn("2008-amendments notice", by_id["S13"]["limits"])
        self.assertIn("not adopted as current law", by_id["S13"]["limits"])

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
        if contract["batch"]["id"] == "M6K-WORK-DELIVERY-VOICE-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/civic-work-foundations/**",
                "tests/test_m6k_civic_work_foundations_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 153))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 273, 110))
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


def minutes(a, b):
    return int((datetime.strptime(b, "%H:%M") - datetime.strptime(a, "%H:%M")).total_seconds() / 60)


class CaseTests(unittest.TestCase):
    def test_project_functional_acceptance_retains_failed_first_version(self):
        f = FIX["project"]
        self.assertLess(f["first_answers"], f["criteria"])
        self.assertEqual(f["second_answers"], f["criteria"])
        self.assertFalse(f["first_accepted"])
        self.assertTrue(f["essential_route_kept"] and f["second_accepted"])
        self.assertEqual(minutes(f["accepted"], f["deadline"]), 30)
        self.assertIn("Asha does not accept v1", doc("21.08", "later-packet.md"))

    def test_project_effort_and_future_upkeep_do_not_become_other_outcomes(self):
        f = FIX["project"]
        self.assertEqual(f["actual"] - f["estimate"], 8)
        self.assertEqual(f["capacity"] - f["actual"], 7)
        self.assertTrue(f["maintenance_accepted"])
        self.assertFalse(f["maintenance_done"] or f["event_occurred"])
        self.assertIn("not measured saved time", doc("21.08", "later-packet.md"))

    def test_team_time_difference_is_not_a_schedule_error(self):
        f = FIX["team"]
        self.assertEqual(minutes(f["arrival"], f["start"]), 10)
        self.assertEqual(minutes(f["start"], f["end"]), sum(f["agenda"]))
        self.assertTrue(f["initial_start_correct"])
        self.assertFalse(f["accusation_shared"])
        self.assertIn("no start-time correction was needed", doc("21.09", "later-packet.md"))

    def test_team_credit_and_handoff_do_not_create_sending_or_efficiency(self):
        f = FIX["team"]
        self.assertTrue(f["receiver_ready"])
        self.assertIn("coordination", f["credit"]["Sora"])
        self.assertIn("wording", f["credit"]["Kai"])
        self.assertFalse(f["sent"] or f["rework_measured"])
        self.assertIn("Nothing is actually sent", doc("21.09", "later-packet.md"))

    def test_innovation_reduced_checking_does_not_hide_wrong_selection(self):
        f = FIX["innovation"]
        self.assertEqual(sum(f["correct"][:2]), 2)
        self.assertEqual(sum(f["correct"][2:]), 1)
        self.assertEqual([sum(f["openings"][:2]), sum(f["openings"][2:])], [7, 0])
        self.assertNotEqual(f["d_selected"], f["d_approved"])
        self.assertEqual(f["candidates_each"], 5)
        self.assertIn("D-v3-draft, v3", doc("21.10"))

    def test_innovation_burden_and_untested_proposal_limit_adoption_claim(self):
        f = FIX["innovation"]
        self.assertEqual(f["setup"] + f["reconcile"], 8)
        self.assertTrue(f["baseline_first"] and f["register_review_agreed"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "elapsed_time_measured",
                    "separate_marker_adopted",
                    "register_tested",
                    "register_adopted",
                )
            )
        )
        self.assertIn("not to adopt or deploy it", doc("21.10", "later-packet.md"))

    def test_career_transfer_preserves_on_hand_and_available_meanings(self):
        f = FIX["career"]
        for case in ("a", "b"):
            start, received, issued, reserved = f[case]
            self.assertEqual(start + received - issued, f[case + "_on_hand"])
            self.assertEqual(start + received - issued - reserved, f[case + "_available"])
        self.assertTrue(f["initial_heading_wrong"] and f["heading_repaired"])
        self.assertEqual(f["final_criteria_met"], f["criteria"])
        self.assertIn("27 as", doc("21.11", "later-packet.md"))

    def test_career_fictional_signals_and_sample_do_not_become_market_evidence(self):
        f = FIX["career"]
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "tool_required_a",
                    "tool_required_b",
                    "signals_actual",
                    "physical_count_verified",
                    "credential_awarded",
                    "hiring_outcome",
                )
            )
        )
        for phrase in (
            "1 September 2026",
            "12 September 2026",
            "18 September 2026",
            "PAPER-STOCK-B",
        ):
            self.assertIn(phrase, doc("21.11"))

    def test_contribution_correct_output_requires_understandable_authority(self):
        f = FIX["contribution"]
        self.assertEqual(minutes(f["original_start"], f["approved_start"]), 30)
        self.assertFalse(f["initial_authority_clear"])
        self.assertTrue(f["superseded_marked"] and f["update_owner_accepted"])
        self.assertEqual(f["reader_answers"], f["reader_criteria"])
        self.assertEqual(f["known_copies"], 2)
        self.assertIn("SUPERSEDED", doc("21.12", "later-packet.md"))

    def test_contribution_interpretation_does_not_prove_attendance_or_ethics(self):
        f = FIX["contribution"]
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "attendance_observed",
                    "missed_meetings_reduced",
                    "maintenance_done",
                    "wider_ethics_resolved",
                )
            )
        )
        self.assertIn("moral absolution", doc("21.12"))

    def test_documentation_exception_retry_does_not_reuse_old_authority(self):
        f = FIX["documentation"]
        self.assertNotEqual(f["first_room_copied"], f["n1_approved_room"])
        self.assertNotEqual(f["n1_approved_room"], f["n2_approved_room"])
        self.assertTrue(f["first_assisted"] and f["fresh_hold_without_hint"])
        self.assertEqual(f["fields"], 5)
        self.assertIn("with the author silent", doc("21.13", "later-packet.md"))

    def test_documentation_maintenance_and_draft_do_not_create_release(self):
        f = FIX["documentation"]
        self.assertTrue(f["shared_editable_access"] and f["maintenance_accepted"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "maintenance_done",
                    "release_approved",
                    "published",
                    "owner_dependencies_removed",
                )
            )
        )
        self.assertIn("Approval and publication remain pending", doc("21.13", "later-packet.md"))

    def test_quality_time_boundary_cannot_waive_essential_readiness(self):
        f = FIX["quality"]
        self.assertFalse(f["ready_at_budget"] or f["optional_done"])
        self.assertEqual(f["first_budget"] + f["additional"], f["total"])
        self.assertEqual(minutes(f["entrance_open"], f["event_start"]), 15)
        self.assertEqual(f["answers"], f["criteria"])
        self.assertIn("DRAFT", doc("21.14", "later-packet.md"))

    def test_quality_harmless_success_does_not_lower_consequential_assurance(self):
        f = FIX["quality"]
        self.assertFalse(
            f["hazardous_task_performed"] or f["public_release"] or f["safety_certified"]
        )
        self.assertTrue(f["upkeep_accepted"])
        self.assertIn("do not write, test or execute an operating procedure", doc("21.14"))

    def test_rights_new_record_narrows_discrepancy_without_damages_ruling(self):
        f = FIX["rights"]
        self.assertEqual(f["periods"] * f["minutes_each"], f["initial_minutes"])
        self.assertEqual(f["included_periods"] * f["minutes_each"], f["included_minutes"])
        self.assertEqual(f["initial_minutes"] - f["included_minutes"], f["unexplained_minutes"])
        self.assertEqual(len(f["areas"]), 8)
        self.assertEqual(set(f["relevant"] + f["clarify"] + f["not_indicated"]), set(f["areas"]))
        for area in f["areas"]:
            self.assertIn(area, doc("21.15").lower())
        self.assertFalse(f["amount_owed_known"])

    def test_rights_directory_warning_and_unsent_inquiry_do_not_resolve_process(self):
        f = FIX["rights"]
        self.assertEqual(f["directory_last_update"], "2026-02-02")
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "jurisdiction_resolved",
                    "coverage_resolved",
                    "deadline_known",
                    "inquiry_sent",
                    "charge_filed",
                    "official_reply",
                    "live_service_verified",
                )
            )
        )
        self.assertIn("deadline unknown", doc("21.15"))
        self.assertIn("not sent", doc("21.15", "later-packet.md"))

    def test_power_comparison_retains_refusal_and_dependency_differences(self):
        f = FIX["power"]
        self.assertTrue(f["agreed_compensation_paid_a"] and f["further_extension_declined_a"])
        self.assertFalse(f["refusal_threat_a"])
        self.assertTrue(f["housing_threat_b"])
        self.assertEqual((f["unpaid_units_b"], f["weeks_unpaid_b"]), (200, 3))
        self.assertIn("Possible outcomes differ by problem and authority", doc("21.16"))

    def test_power_conversation_is_not_housing_or_delivered_remedy(self):
        f = FIX["power"]
        self.assertTrue(f["friend_talk"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "friend_housing",
                    "friend_money",
                    "alternative_housing",
                    "inquiry_sent",
                    "resigned",
                    "report_filed",
                    "legal_finding",
                    "remedy_delivered",
                )
            )
        )
        self.assertIn("no accepted housing alternative", doc("21.16", "later-packet.md"))

    def test_voice_limited_mandate_and_known_burden_do_not_represent_everyone(self):
        f = FIX["voice"]
        self.assertEqual(f["workers"] - f["inquiry_agreements"], 5)
        self.assertEqual(
            f["inquiry_agreements"] * f["joint_minutes_each"], f["joint_person_minutes"]
        )
        self.assertEqual(
            f["proposed_representatives"] * f["committee_meeting_each"],
            f["committee_person_minutes"],
        )
        self.assertFalse(f["other_views_known"])
        self.assertEqual(f["actual_dues"], 0)
        self.assertIn("not counted as opposed or represented", doc("21.17", "later-packet.md"))

    def test_voice_municipal_update_changes_route_not_all_rights(self):
        f = FIX["voice"]
        self.assertEqual(f["later_sector"], "municipal department")
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "initial_sector_confirmed",
                    "automatic_nlra_coverage",
                    "other_rights_absent",
                    "committee_formed",
                    "workers_contacted",
                    "schedule_changed",
                )
            )
        )
        self.assertIn(
            "No conclusion that the workers have no rights follows", doc("21.17", "later-packet.md")
        )

    def test_access_platform_block_is_not_zero_accuracy(self):
        f = FIX["access"]
        self.assertLess(f["a_fact_categories_met"], f["categories"])
        self.assertTrue(f["a_clarification_correct"] and f["platform_blocked"])
        self.assertIsNone(f["platform_accuracy"])
        self.assertTrue(f["mode_revised_to_paper"])
        self.assertIn("unobserved", doc("21.18", "later-packet.md"))

    def test_access_fresh_retry_preserves_criteria_without_diagnosis_or_policy_change(self):
        f = FIX["access"]
        self.assertEqual(f["b_fact_categories_met"], f["categories"])
        self.assertEqual(f["clarifications"], 1)
        self.assertTrue(f["b_clarification_correct"] and f["criteria_unchanged"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "answer_coached",
                    "diagnosis_requested",
                    "actual_policy_changed",
                    "universal_access_proven",
                )
            )
        )
        self.assertIn("2008 amendments", doc("21.18"))

    def test_boundary_capacity_coverage_and_next_day_commitment_are_explicit(self):
        f = FIX["boundary"]
        self.assertLess(minutes(f["request"], f["closing"]), f["estimated_minutes"])
        self.assertTrue(f["jo_accepted"] and f["coverage_preaccepted"])
        self.assertEqual(minutes(f["next_start"], f["next_finish"]), f["estimated_minutes"])
        self.assertGreater(minutes(f["next_accepted"], f["review"]), 0)
        self.assertFalse(f["urgent_incident"] or f["hidden_work"])

    def test_boundary_interrupted_time_does_not_become_uninterrupted_rest(self):
        f = FIX["boundary"]
        interrupted = sum(minutes(a, b) for a, b in f["checks"])
        self.assertEqual(interrupted, 7)
        self.assertEqual(f["planned_rest"] - interrupted, f["drawing_minutes"])
        segments = [minutes("17:00", "17:05"), minutes("17:09", "17:20"), minutes("17:23", "17:30")]
        self.assertEqual(sum(segments), f["drawing_minutes"])
        self.assertEqual(max(segments), f["longest_segment"])
        self.assertFalse(f["adjustment_tested"] or f["health_outcome"])
        self.assertIn("not thirty uninterrupted minutes", doc("21.19", "later-packet.md"))
