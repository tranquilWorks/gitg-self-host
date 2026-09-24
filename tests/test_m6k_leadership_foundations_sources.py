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
SOURCE = ROOT / "docs/authoring/leadership-foundations"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"22.{i:02}" for i in range(1, 13)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 165)
        self.assertEqual(COHORT["additional_companions_after"], 177)
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
        for domain in ("22",):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads((ROOT / "docs/authoring/work-delivery-voice/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "21.19")
        self.assertEqual(previous["additional_companions_after"], 165)
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

    def test_role_conditional_and_absent_canonical_boundary(self):
        for e in COHORT["entries"]:
            self.assertEqual(e["classification"]["applicability"], "role_conditional")
            self.assertEqual(e["classification"]["normative_status"], "role_conditional")
            self.assertNotIn("professional_boundary", e)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn(
                    "canonical record has no professional_boundary field", doc(e["id"], name)
                )
            self.assertIn("Fiction and no attempt are legitimate", doc(e["id"]))
        self.assertEqual(COHORT["skipped_implemented_ids"], [])

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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 10)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-24")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        by_id = {source["id"]: source for source in sources}
        self.assertIn("England and Wales", by_id["S09"]["limits"])
        self.assertIn("not generalized", by_id["S09"]["limits"])
        self.assertIn("not the full CERC manual", by_id["S07"]["limits"])
        self.assertIn("templates were not inspected", by_id["S08"]["limits"])
        self.assertIn("No confidentiality guarantee", by_id["S06"]["limits"])

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
        if contract["batch"]["id"] == "M6K-LEADERSHIP-FOUNDATIONS-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/work-delivery-voice/**",
                "tests/test_m6k_work_delivery_voice_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 165))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 285, 98))
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
    def test_credibility_two_copy_repair_retains_late_completion(self):
        f = FIX["credibility"]
        self.assertEqual(sum(f["agenda"]), f["duration"])
        self.assertEqual(f["copies"], 2)
        self.assertGreater(minutes(f["first"], f["promised"]), 0)
        self.assertEqual(minutes(f["promised"], f["complete"]), 15)
        self.assertIn("15 minutes after", doc("22.01", "later-packet.md"))

    def test_credibility_conduct_repair_and_estimate_are_not_trust_measurement(self):
        f = FIX["credibility"]
        self.assertEqual(minutes(f["old_start"], f["new_start"]), 30)
        self.assertTrue(f["defensive_opening"] and f["conduct_repair"])
        self.assertFalse(f["attendance_confirmed"] or f["trust_measured"] or f["pattern_observed"])
        self.assertIn("Blaming you was unfair", doc("22.01", "later-packet.md"))

    def test_direction_capacity_requires_actual_scope_reduction(self):
        f = FIX["direction"]
        self.assertEqual(sum(f["initial"]), f["initial_capacity"])
        self.assertEqual(sum(f["revised"]), f["revised_capacity"])
        self.assertEqual(sum(f["initial"]) - sum(f["revised"]), 20)
        self.assertTrue(f["original_c_declined"] and f["reduced_c_accepted"])
        self.assertEqual(len(f["nonpriorities"]), 2)
        self.assertIn("broader welcome script", doc("22.02", "later-packet.md"))

    def test_direction_comprehension_does_not_erase_disagreement_or_create_delivery(self):
        f = FIX["direction"]
        self.assertTrue(f["misunderstanding_repaired"] and f["disagreement_retained"])
        self.assertFalse(f["work_completed"] or f["participation_observed"])
        self.assertIn("disagreement about sequencing", doc("22.02", "later-packet.md"))

    def test_power_recusal_and_willingness_precede_fair_access_tiebreak(self):
        f = FIX["power"]
        eligible = [p for p in f["slots"] if f["willing"][p] and f["ready_with_support"][p]]
        self.assertEqual(min(eligible, key=lambda p: f["slots"][p]), f["selected"])
        self.assertNotIn("Chen", eligible)
        self.assertEqual(len({f["selector"], f["reviewer"], f["connected"]}), 3)
        self.assertTrue(f["recusal"])
        self.assertIn("takes no part", doc("22.03", "later-packet.md"))

    def test_power_supported_capacity_and_one_preserved_resource_bound_claims(self):
        f = FIX["power"]
        self.assertLess(f["labels_initial"], f["criteria"])
        self.assertEqual(f["labels_after"], f["criteria"])
        self.assertTrue(f["coach_prompt"])
        self.assertEqual(f["chen_shifts_before"], f["chen_shifts_after"])
        self.assertFalse(
            f["references_tested"] or f["presentation_delivered"] or f["pressure_absent_proven"]
        )
        self.assertIn("supported rehearsal", doc("22.03", "later-packet.md"))

    def test_decision_new_count_changes_viability_within_switch_window(self):
        f = FIX["decision"]
        self.assertLessEqual(
            f["confirmed_initial"] + f["possible_initial"], f["capacities"][f["initial"]]
        )
        self.assertGreater(f["confirmed_later"], f["capacities"][f["initial"]])
        self.assertLessEqual(f["confirmed_later"], f["capacities"][f["revised"]])
        self.assertLessEqual(f["costs"][f["revised"]], f["budget"])
        self.assertEqual(minutes(f["changed"], f["hold_until"]), 40)
        self.assertIn("no known capacity breach existed at noon", doc("22.04", "later-packet.md"))

    def test_decision_receipt_and_event_remain_open_after_good_revision(self):
        f = FIX["decision"]
        self.assertEqual(f["recipients"] - f["acknowledged"], 4)
        self.assertEqual(f["capacities"][f["revised"]] - f["confirmed_later"], 4)
        self.assertTrue(f["initial_approvals"])
        self.assertFalse(f["event_completed"])
        self.assertIn("four have not yet confirmed receipt", doc("22.04", "later-packet.md"))

    def test_delegation_revision_keeps_all_minima_and_actual_time_authority(self):
        f = FIX["delegation"]
        self.assertEqual(len(f["minima"]), f["required_topics"])
        self.assertEqual(sum(f["first"]) - f["duration"], 5)
        self.assertEqual(sum(f["revised"]), f["duration"])
        self.assertTrue(
            all(
                actual >= minimum for actual, minimum in zip(f["revised"], f["minima"], strict=True)
            )
        )
        self.assertEqual(f["duration"] - sum(f["minima"]), 7)
        self.assertIn("3, 4, 10, 8, 5", doc("22.05", "later-packet.md"))

    def test_delegation_prompt_and_retained_aids_do_not_become_unlimited_readiness(self):
        f = FIX["delegation"]
        self.assertEqual(minutes(f["accepted"], f["deadline"]), 15)
        self.assertTrue(
            f["delegate_chose_revision"] and f["calculator"] and f["checklist_retained"]
        )
        self.assertFalse(f["lead_supplied_allocation"] or f["meeting_observed"])
        self.assertIn("keeping changes to total duration", doc("22.05", "later-packet.md"))

    def test_coaching_fresh_transfer_changes_salient_fact_preserving_seven_checks(self):
        f = FIX["coaching"]
        self.assertEqual(f["fact_categories"] + f["extra_checks"], f["criteria"])
        self.assertEqual([f["r1_revised"], f["r2"]], [f["criteria"], f["criteria"]])
        self.assertNotEqual(f["changed_r1"], f["changed_r2"])
        self.assertIn("MODEL does not supply the answer to R1", doc("22.06"))
        self.assertIn("Willow Room", doc("22.06", "later-packet.md"))

    def test_coaching_assistance_levels_and_next_opportunity_remain_distinct(self):
        f = FIX["coaching"]
        self.assertTrue(f["r1_assisted"] and f["r2_checklist"] and f["next_opportunity_accepted"])
        self.assertFalse(
            f["r2_coach_words"]
            or f["next_opportunity_done"]
            or f["sent"]
            or f["retention_measured"]
        )
        self.assertIn("Oren silent", doc("22.06", "later-packet.md"))

    def test_accountability_source_conflict_requires_leader_and_writer_repairs(self):
        f = FIX["accountability"]
        self.assertEqual(minutes(f["n1"], f["n2"]), 30)
        self.assertTrue(f["n1_current_left"])
        self.assertFalse(f["change_notified_initially"])
        self.assertEqual(minutes(f["draft"], f["draft_due"]), 10)
        self.assertGreater(minutes(f["labels_fixed"], f["correction"]), 0)
        self.assertIn("Lian accepts source-status repair", doc("22.07", "later-packet.md"))

    def test_accountability_consistent_followup_does_not_erase_future_uncertainty(self):
        f = FIX["accountability"]
        self.assertEqual(minutes(f["accepted"], f["checkpoint"]), 10)
        self.assertTrue(f["source_verified_n3"] and f["leader_own_typo_corrected"])
        self.assertFalse(f["sent"] or f["penalty"] or f["recurrence_impossible"])
        self.assertIn("same check to their own cover note", doc("22.07", "later-packet.md"))

    def test_dissent_resolves_dependency_before_finalization_without_earlier_access(self):
        f = FIX["dissent"]
        self.assertEqual(minutes(f["initial_setup"], f["approved_access"]), 20)
        self.assertEqual(minutes(f["approved_access"], f["start"]), f["setup_minutes"])
        self.assertEqual(minutes(f["update"], f["promise"]), 5)
        self.assertEqual(minutes(f["update"], f["finalization"]), 35)
        self.assertIn(
            "No extra venue permission or earlier access is invented",
            doc("22.08", "later-packet.md"),
        )

    def test_dissent_private_usability_and_silence_do_not_certify_climate(self):
        f = FIX["dissent"]
        self.assertTrue(f["private_route_usable"] and f["role_unchanged"])
        self.assertEqual(f["silent_people"], 2)
        self.assertFalse(
            f["public_credit_consent"]
            or f["silence_interpreted_as_agreement"]
            or f["climate_validated"]
        )
        self.assertIn("personal label was inappropriate", doc("22.08", "later-packet.md"))

    def test_culture_volume_distortion_is_visible_alongside_useful_early_response(self):
        f = FIX["culture"]
        self.assertEqual(f["reports"] - f["duplicates"], f["distinct_issues"])
        self.assertEqual(minutes(f["surfaced"], f["deadline"]), 240)
        self.assertEqual(minutes(f["surfaced"], f["resolved"]), 30)
        self.assertEqual(f["actual_person_minutes"] - f["planned_person_minutes"], 3)
        self.assertTrue(f["volume_points_removed"])
        self.assertIn("five reports but only two distinct issues", doc("22.09", "later-packet.md"))

    def test_culture_all_system_facets_remain_beyond_ritual_only_success(self):
        f = FIX["culture"]
        self.assertTrue(f["council_review_agreed"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "selection_changed",
                    "progression_changed",
                    "deliverables_complete",
                    "causal_culture_change",
                )
            )
        )
        for facet in (
            "norm",
            "incentive",
            "ritual",
            "information route",
            "selection",
            "progression",
            "consequence",
        ):
            self.assertIn(facet, doc("22.09").lower())
        self.assertIn("criteria are undocumented", doc("22.09"))

    def test_politics_timing_requires_two_accepted_owners_and_formal_approval(self):
        f = FIX["politics"]
        self.assertEqual(minutes(f["setup_start"], f["session_start"]), f["setup_minutes"])
        self.assertEqual(minutes(f["session_end"], f["room_clear"]), f["clear_minutes"])
        self.assertEqual(minutes(f["session_start"], f["session_end"]), 40)
        self.assertEqual(
            len({f["setup_owner"], f["clearance_owner"], f["approval"], f["room_authority"]}), 4
        )
        self.assertIn("no spare clearance margin", doc("22.10", "later-packet.md"))

    def test_politics_bounded_trial_does_not_invent_coalition_consensus_or_benefit(self):
        f = FIX["politics"]
        self.assertEqual(len(f["trial_dates"]), 2)
        self.assertGreater(f["review"], max(f["trial_dates"]))
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "coalition_confirmed",
                    "unanimous",
                    "permanent",
                    "trial_performed",
                    "trust_measured",
                )
            )
        )
        self.assertIn("Morgan has not endorsed the trial", doc("22.10", "later-packet.md"))

    def test_crisis_decision_and_update_fit_deadline_with_accepted_owners(self):
        f = FIX["crisis"]
        self.assertEqual(minutes(f["start_time"], f["decision"]), 20)
        self.assertEqual(minutes(f["decision"], f["update"]), 3)
        self.assertEqual(minutes(f["update"], f["update_due"]), 2)
        self.assertEqual(f["owners_accepted"], ["Kim", "Oli", "Pia"])
        self.assertFalse(f["alternative_available"] or f["cause_confirmed"])
        self.assertIn("TABLETOP DRAFT — DO NOT SEND", doc("22.11"))

    def test_crisis_partial_acknowledgment_cannot_become_universal_safety_or_qualification(self):
        f = FIX["crisis"]
        self.assertEqual(f["attendees"] - f["acknowledged"], 2)
        self.assertEqual(f["initial_people_onsite"], 0)
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "later_all_locations_known",
                    "followup_done",
                    "improvement_done",
                    "live_drill",
                    "qualified",
                )
            )
        )
        self.assertIn("known only at 16:40", doc("22.11", "later-packet.md"))

    def test_succession_fresh_exception_requires_current_authority_not_precedent(self):
        f = FIX["succession"]
        self.assertEqual(sum(f["agenda_minima"]), f["duration"])
        self.assertLess(len(f["e1_approvals"]), f["required_approvals"])
        self.assertLess(len(f["e2_approvals"]), f["required_approvals"])
        self.assertNotEqual(f["e1_approvals"], f["e2_approvals"])
        self.assertTrue(f["e1_assisted"] and f["e2_deferred"])
        self.assertFalse(f["e2_hint"] or f["purchase"])
        self.assertIn("two current approvals", doc("22.12", "later-packet.md"))

    def test_succession_appointment_pack_and_maintenance_do_not_complete_access_transfer(self):
        f = FIX["succession"]
        self.assertNotEqual(f["appointed_owner"], f["backup"])
        self.assertTrue(f["pack_access_both"] and f["maintenance_accepted"])
        self.assertFalse(
            f["notice_access_transferred"]
            or f["maintenance_done"]
            or f["public_release"]
            or f["institution_resilience_proven"]
        )
        self.assertIn("notice channel still depends on Ro", doc("22.12", "later-packet.md"))


if __name__ == "__main__":
    unittest.main()
