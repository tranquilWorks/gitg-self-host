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
SOURCE = ROOT / "docs/authoring/civic-work-foundations"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"20.{i:02}" for i in range(13, 19)] + ["21.01", "21.02", "21.04", "21.05", "21.06", "21.07"]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 141)
        self.assertEqual(COHORT["additional_companions_after"], 153)
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

    def test_selected_current_recovery_entries_match(self):
        for domain in ("20", "21"):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads((ROOT / "docs/authoring/civic-participation/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "20.12")
        self.assertEqual(previous["additional_companions_after"], 141)
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

    def test_mixed_classification_and_optional_canonical_boundary(self):
        for e in COHORT["entries"]:
            civic = e["id"].startswith("20.")
            self.assertEqual(
                e["classification"]["applicability"],
                "cross_context_core" if civic else "context_sensitive",
            )
            self.assertEqual(
                e["classification"]["normative_status"], "cross_tradition_core_or_broadly_recurrent"
            )
            self.assertEqual("professional_boundary" in e, civic)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                if civic:
                    self.assertIn(e["professional_boundary"], doc(e["id"], name))
                else:
                    self.assertIn(
                        "canonical record has no professional_boundary field", doc(e["id"], name)
                    )
            self.assertIn("Fiction and no attempt are legitimate", doc(e["id"]))
        self.assertEqual(COHORT["skipped_implemented_ids"], ["21.03"])
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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 13)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["sections"])
            self.assertTrue(s["limits"])
            for cid in s["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{s['id']}", doc(cid))
        by_id = {s["id"]: s for s in sources}
        self.assertIn("Pandemic-specific claims", by_id["S01"]["limits"])
        self.assertIn("Workplace context", by_id["S02"]["limits"])
        self.assertIn("not the full letter", by_id["S03"]["limits"])
        self.assertIn("full NORMLEX instrument could not be retrieved", by_id["S05"]["limits"])
        self.assertIn("Linked research was not inspected", by_id["S09"]["limits"])
        self.assertIn("not a NASA-compliant control", by_id["S12"]["limits"])

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
        if contract["batch"]["id"] == "M6K-CIVIC-WORK-FOUNDATIONS-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/civic-participation/**",
                "tests/test_m6k_civic_participation_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 141))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 261, 122))
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
    def test_propaganda_mechanism_and_factual_record_are_separate(self):
        f = FIX["propaganda"]
        self.assertEqual((f["changed"], f["bookings"]), (2, 12))
        self.assertTrue(f["maintenance_record"])
        self.assertFalse(
            f["group_blame_supported"] or f["fairness_assessed"] or f["coordination_established"]
        )
        self.assertIn("does not settle every fairness concern", doc("20.13", "later-packet.md"))
        for phrase in (
            "Scapegoating",
            "Dehumanizing",
            "Conspiratorial closure",
            "Epistemic capture",
        ):
            self.assertIn(phrase, doc("20.13"))

    def test_propaganda_consistency_and_revised_draft_are_not_dissemination(self):
        f = FIX["propaganda"]
        self.assertTrue(f["favored_test_private"] and f["mocking_reply_removed"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "original_forwarded",
                    "rewrite_shared",
                    "reply_sent",
                    "belief_changed_known",
                )
            )
        )
        self.assertIn(
            "No original post, rewrite or response is sent", doc("20.13", "later-packet.md")
        )

    def test_nonviolent_methods_and_partial_access_are_distinct(self):
        f = FIX["nonviolent"]
        self.assertTrue(f["text_supplied"])
        self.assertFalse(f["written_route_accepted"] or f["written_route_implemented"])
        self.assertEqual(minutes(f["telephone_start"], f["telephone_end"]), 60)
        self.assertLess(f["deadline"], f["meeting"])
        self.assertIn(
            "monitored written access-question route by 15 October at 12:00", doc("20.14")
        )
        for phrase in (
            "Negotiation",
            "Mediation",
            "Restorative",
            "boycott",
            "strike",
            "protest",
            "civil resistance",
        ):
            self.assertIn(phrase.lower(), doc("20.14").lower())

    def test_nonviolent_refusal_branch_does_not_become_a_real_campaign(self):
        f = FIX["nonviolent"]
        self.assertTrue(f["refusal_separate_branch"] and f["followup_draft"])
        self.assertFalse(f["followup_sent"] or f["actual_campaign"])
        self.assertIn(
            "hypothetical branch, not an additional event", doc("20.14", "later-packet.md")
        )
        self.assertIn("without automatic escalation", doc("20.14"))

    def test_disobedience_new_review_route_changes_necessity_not_legal_status(self):
        f = FIX["disobedience"]
        self.assertTrue(
            f["a_public_reason"]
            and f["a_opponent_consistency"]
            and f["specified_review_route_exists"]
        )
        self.assertEqual(f["normal_review_working_days"], 5)
        self.assertFalse(
            f["specified_review_route_used"]
            or f["response_guaranteed"]
            or f["rule_legal_status_known"]
        )
        self.assertIn("weakens the supplied necessity argument", doc("20.15", "later-packet.md"))

    def test_disobedience_accountability_preserves_rights_and_known_motive(self):
        f = FIX["disobedience"]
        self.assertEqual(f["b_original_purpose"], "private convenience")
        self.assertFalse(f["breach_occurred"] or f["legal_consultation"] or f["rights_waived"])
        self.assertIn("does not require surrendering legal rights", doc("20.15", "later-packet.md"))
        self.assertIn("would not retroactively establish", doc("20.15"))

    def test_mutual_two_selected_exchanges_preserve_source_and_access_limits(self):
        f = FIX["mutual"]
        self.assertNotEqual(f["stale_hours"], f["current_hours"])
        self.assertTrue(
            all(
                f[k]
                for k in (
                    "hours_accepted",
                    "hours_sent",
                    "copy_requested",
                    "copy_accepted",
                    "copy_retained",
                )
            )
        )
        self.assertFalse(f["exception_checked"] or f["actual_visit"])
        self.assertIn("Tuesday 10:00", doc("20.16"))
        for stop in f["route"]:
            self.assertIn(stop, doc("20.16"))

    def test_mutual_backup_acceptance_does_not_impose_debt_or_care(self):
        f = FIX["mutual"]
        self.assertTrue(f["backup_accepted"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "equal_debt",
                    "lee_required_contribution",
                    "backup_done",
                    "private_care_transferred",
                )
            )
        )
        self.assertIn("That check has not happened", doc("20.16", "later-packet.md"))
        for area in (
            "Food",
            "Transport",
            "Public information",
            "Emergencies",
            "Childcare",
            "support",
        ):
            self.assertIn(area, doc("20.16"))

    def test_insurance_ordinary_and_stress_scenarios_do_not_double_spend_remainder(self):
        f = FIX["insurance"]
        fund = f["members"] * f["contribution"]
        self.assertEqual(fund, 1000)
        self.assertEqual(fund - f["ordinary_needs"] * f["per_need"], 200)
        self.assertEqual(f["stress_needs"] * f["per_need"] - fund, 600)
        self.assertFalse(f["admin_known"] or f["reserve_supplied"])
        self.assertIn("not an established reserve", doc("20.17", "later-packet.md"))

    def test_insurance_stress_options_expose_burden_and_missing_policy_data(self):
        f = FIX["insurance"]
        self.assertEqual(600 - f["hypothetical_extra_reserve"], 300)
        self.assertEqual(f["members"] * f["alternative_contribution"], 1600)
        self.assertEqual(f["stress_needs"] * f["alternative_benefit"], 1000)
        self.assertEqual(f["per_need"] - f["alternative_benefit"], 30)
        self.assertFalse(f["fraud_rate_known"] or f["takeup_known"] or f["policy_implemented"])
        self.assertIn("does not establish affordability", doc("20.17", "later-packet.md"))

    def test_reconciliation_components_do_not_fund_or_implement_themselves(self):
        f = FIX["reconciliation"]
        self.assertEqual(f["estimated_resources"] - f["identified_resources"], 15)
        self.assertTrue(f["rule_withdrawn_on_paper"])
        self.assertFalse(
            f["actual_access_verified"]
            or f["remedy_delivered"]
            or f["legal_responsibility_determined"]
        )
        self.assertIn("not verified access", doc("20.18", "later-packet.md"))
        for word in (
            "Truth-telling",
            "Accountability",
            "Memory",
            "Reparations",
            "Institutional reform",
            "Coexistence",
        ):
            self.assertIn(word, doc("20.18"))

    def test_reconciliation_voluntary_record_does_not_require_forgiveness(self):
        f = FIX["reconciliation"]
        self.assertTrue(f["public_testimony_condition_removed"] and f["record_process_voluntary"])
        self.assertFalse(f["forgiveness_required"] or f["testimony_collected"] or f["consensus"])
        self.assertIn(
            "ordinary training access does not require disclosure or forgiveness",
            doc("20.18", "later-packet.md"),
        )

    def test_work_choice_hard_constraint_survives_prestige_and_totals(self):
        f = FIX["work_choice"]
        self.assertEqual(f["a_planned_hours"] + f["a_extra_hours"] - f["hours_cap"], 6)
        self.assertGreaterEqual(f["b_pay"], f["income_floor"])
        self.assertEqual(sum(f["b_hours"]), f["hours_cap"])
        self.assertEqual(sum(f["current_hours"]), sum(f["redesign_hours"]))
        self.assertIn("36 reported hours against a 30-hour limit", doc("21.01", "later-packet.md"))
        for word in (
            "Aptitude",
            "Livelihood",
            "Service",
            "Meaning",
            "Environment",
            "Growth",
            "Dignity",
            "Real need",
        ):
            self.assertIn(word, doc("21.01"))

    def test_work_choice_discussion_and_role_account_do_not_create_terms_or_approval(self):
        f = FIX["work_choice"]
        self.assertTrue(f["manager_discussion_accepted"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "protected_hours_verified",
                    "redesign_approved",
                    "mentor_accepted",
                    "offer_accepted",
                    "resigned",
                )
            )
        )
        self.assertIn(
            "not approval, allocated mentoring or a started trial", doc("21.01", "later-packet.md")
        )

    def test_reliability_provisional_delivery_does_not_erase_late_complete_scope(self):
        f = FIX["reliability"]
        self.assertLess(f["checkpoint"], f["v1_sent"])
        self.assertEqual(minutes(f["v1_sent"], f["deadline"]), 20)
        self.assertEqual(minutes(f["deadline"], f["v2_sent"]), 70)
        self.assertLess(f["room_confirmed"], f["v2_sent"])
        self.assertTrue(f["provisional_scope_accepted"])
        self.assertFalse(f["v1_ready_for_attendees"])
        self.assertIn(
            "original commitment was not fully met on time", doc("21.02", "later-packet.md")
        )

    def test_reliability_complete_materials_and_effort_do_not_imply_attendance(self):
        f = FIX["reliability"]
        self.assertEqual(sum(f["topics_minutes"]), 30)
        self.assertEqual(f["actual_minutes"] - f["estimate_minutes"], 10)
        self.assertLessEqual(f["actual_minutes"], f["available_minutes"])
        self.assertFalse(f["meeting_occurred"])
        for phrase in (
            "Welcome and purpose, 5 minutes",
            "review the draft notice, 15 minutes",
            "decide owners and next dates, 10 minutes",
            "Room N2",
        ):
            self.assertIn(phrase, doc("21.02"))

    def test_mastery_component_success_retains_whole_task_regression(self):
        f = FIX["mastery"]
        self.assertEqual(sum(f["baseline"]), 2)
        self.assertEqual(sum(f["f1"]), 2)
        self.assertFalse(f["baseline"][2])
        self.assertTrue(f["f1"][2])
        self.assertFalse(f["f1"][0])
        self.assertEqual(f["practice_destinations"], ["BLUE", "desk"])
        self.assertIn("omits writing the item ID", doc("21.04", "later-packet.md"))

    def test_mastery_fresh_integrated_result_is_not_real_expert_or_retention_evidence(self):
        f = FIX["mastery"]
        self.assertEqual(sum(f["f2"]), len(f["criteria"]))
        self.assertTrue(f["f1_fresh"] and f["f2_fresh"])
        self.assertFalse(
            f["actual_expert"] or f["actual_reader"] or f["retention_test"] or f["broad_transfer"]
        )
        self.assertIn("No actual reader or expert was involved", doc("21.04", "later-packet.md"))
        self.assertIn("Write its item ID on a borrow slip", doc("21.04"))

    def test_quality_paper_positions_preserve_route_and_restore_all_tokens(self):
        f = FIX["quality"]
        self.assertEqual(len(f["chair_positions"]), f["chairs"])
        self.assertEqual(len({tuple(x) for x in f["chair_positions"]}), f["chairs"])
        self.assertTrue(
            all(p[1] != f["clear_column"] for p in f["chair_positions"] + [f["table_position"]])
        )
        self.assertEqual(f["restored_chairs"] + f["restored_tables"], f["chairs"] + f["tables"])
        self.assertIn("NORMAL STORAGE", doc("21.05"))
        self.assertIn("Room Desk", doc("21.05"))

    def test_quality_two_uses_are_not_two_uncoached_successes(self):
        f = FIX["quality"]
        self.assertTrue(f["first_assisted"] and f["second_uncoached"] and f["second_new_reader"])
        self.assertFalse(f["actual_room"] or f["safety_certified"] or f["durable_reputation"])
        self.assertIn("not two uncoached successes", doc("21.05", "later-packet.md"))

    def test_users_praise_yields_to_task_failure_and_new_event_facts(self):
        f = FIX["users"]
        self.assertTrue(
            f["praise"]
            and f["a_time_correct"]
            and f["a_contact_correct"]
            and f["requirement_changed"]
        )
        self.assertNotEqual(f["a_selected_entry"], f["required_entry"])
        self.assertEqual(f["b_selected_entry"], f["required_entry"])
        self.assertEqual(minutes(f["a_entry_open"], f["a_start"]), 15)
        self.assertEqual(minutes(f["b_entry_open"], f["b_start"]), 15)
        self.assertNotEqual(f["a_start"], f["b_start"])
        self.assertIn("East Entrance from 18:45", doc("21.06"))

    def test_users_helper_review_and_retry_do_not_create_private_contact_or_general_validation(
        self,
    ):
        f = FIX["users"]
        self.assertTrue(f["b_new_reader"] and f["helper_label_approved"])
        self.assertFalse(
            f["coached"]
            or f["new_private_contact"]
            or f["actual_arrival"]
            or f["support_saving_measured"]
        )
        self.assertIn("No new private phone number", doc("21.06", "later-packet.md"))

    def test_systems_approved_version_controls_readiness_not_timestamp(self):
        f = FIX["systems"]
        self.assertTrue(f["all_owners_agreed"] and f["first_held"])
        self.assertFalse(f["first_card_has_id"])
        self.assertEqual(f["selected_notice"], f["approved_notice"])
        self.assertNotEqual(f["selected_notice"], f["new_draft"])
        self.assertEqual(f["correction_route"], ["Lena", "Ash", "Ren"])
        self.assertIn("Q1; N2; APPROVED; Ash at 10:00 UTC", doc("21.07", "later-packet.md"))

    def test_systems_added_burden_and_maintenance_do_not_prove_net_saving_or_publication(self):
        f = FIX["systems"]
        self.assertEqual(f["writer_added_minutes"] + f["approver_added_minutes"], 3)
        self.assertTrue(f["maintenance_accepted"])
        self.assertFalse(
            f["other_costs_known"]
            or f["actual_publication"]
            or f["net_savings_known"]
            or f["incentive_motive_proven"]
        )
        self.assertIn(
            "No other time, queue delay or net saving is measured", doc("21.07", "later-packet.md")
        )
