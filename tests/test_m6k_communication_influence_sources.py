"""Regress source integrity, case feasibility and evidence limits; never grade learners."""

import hashlib
import json
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/communication-influence"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"16.{i:02}" for i in range(2, 14)]


def doc(cid, filename="learner-guide.md"):
    return (SOURCE / cid / filename).read_text()


def interval(start, end):
    return int(
        (datetime.strptime(end, "%H:%M") - datetime.strptime(start, "%H:%M")).total_seconds() / 60
    )


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_counts(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 69)
        self.assertEqual(COHORT["additional_companions_after"], 81)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)

    def test_canonical_entries_and_all_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        entries = [
            e for d in catalog["curriculum"]["domains"] for e in d["competencies"] if e["id"] in IDS
        ]
        self.assertEqual(COHORT["entries"], entries)
        self.assertEqual(len(COHORT["input_sha256"]), 5)
        for path, digest in COHORT["input_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_previous_endpoint_and_legacy_classification(self):
        previous = json.loads(
            (ROOT / "docs/authoring/resilience-community-listening/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "16.01")
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        self.assertFalse(set(IDS) & set(contract["implemented_competency_ids"]))
        self.assertEqual(set(IDS) & set(contract["retained_legacy_competency_ids"]), {"16.03"})
        self.assertEqual(COHORT["legacy_companion_ids"], ["16.03"])

    def test_legacy_actions_duration_and_followup_remain_original(self):
        legacy = yaml.safe_load(
            (ROOT / "data/practices/protocols/16/PRACTICE-EMOTIONAL-CUES-01.yaml").read_text()
        )
        self.assertEqual(legacy["parent_competency_id"], "16.03")
        self.assertEqual(legacy["intervention"]["duration_days"], 10)
        actions = legacy["intervention"]["actions"]
        self.assertEqual(
            [a["stable_id"] for a in actions],
            [f"PRACTICE-EMOTIONAL-CUES-01-A{i}" for i in range(1, 4)],
        )
        self.assertEqual(actions[-1]["due_within_days"], 7)
        self.assertIn(
            "follow_up_within_seven_days", actions[-1]["evidence_rules"]["primary_markers"]
        )
        self.assertIn("existing seven-day follow-up", doc("16.03"))
        self.assertIn("app's original fields", doc("16.03"))

    def test_five_complete_files_and_three_separate_checks_per_id(self):
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

    def test_canonical_scope_and_measurement_are_not_new_scoring(self):
        for e in COHORT["entries"]:
            scope = doc(e["id"], "SCOPE-MAP.md")
            for field in ("name", "scope", "evidence_of_progress"):
                self.assertIn(e[field], scope)
            self.assertIn(e["measurement"]["minimum_standard"], scope)
            self.assertTrue(e["measurement"]["not_proof_of_moral_worth"])
            self.assertIn("not a new exercise scoring rule", scope)
            self.assertIn("Human dignity is never scored", scope)

    def test_local_links_and_source_anchors_resolve(self):
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target:
                    continue
                name, _, anchor = target.partition("#")
                dest = (path.parent / name).resolve()
                self.assertTrue(dest.is_file(), f"{path}: {target}")
                if anchor:
                    self.assertRegex(dest.read_text(), rf"(?mi)^## {re.escape(anchor)}$")

    def test_current_contract_preserves_prior_paths_and_ci_boundary(self):
        c = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        if c["batch"]["id"] == "M6K-COMMUNICATION-INFLUENCE-TWELVE":
            self.assertEqual(c["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/resilience-community-listening/**",
                "tests/test_m6k_resilience_community_listening_sources.py",
            ):
                self.assertIn(path, c["scope"]["forbidden_paths"])
        self.assertTrue(all(isinstance(s, str) for s in c["acceptance"]))

    def test_source_index_covers_every_id_and_keeps_abstract_limits(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 16)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["limits"])
        for sid in ("S04", "S05", "S10"):
            s = next(s for s in sources if s["id"] == sid)
            self.assertIn("abstract", s["limits"].lower())

    def test_supplied_responses_never_become_participant_evidence(self):
        self.assertTrue(FIX["all_responses_supplied_fiction"])
        self.assertFalse(FIX["actual_participant_evidence"])
        for cid in IDS:
            self.assertIn("fiction", doc(cid, "later-packet.md").lower())
        review = (SOURCE / "QUALITY-REVIEW.md").read_text()
        for cid in IDS:
            self.assertIn(f"## {cid}", review)
        self.assertIn("not an independent cold-start review", review)


class ExpressionCueConversationTests(unittest.TestCase):
    def test_return_offer_is_late_but_collection_fits(self):
        x = FIX["expression"]
        self.assertEqual(x["need_day"], x["offered_day"])
        self.assertEqual(interval(x["need_time"], x["offered_time"]), x["late_minutes"])
        self.assertGreaterEqual(interval(x["collection_start"], x["collection_offer"]), 0)
        self.assertGreaterEqual(interval(x["collection_offer"], x["collection_end"]), 0)
        self.assertIn("misses the need by one hour", doc("16.02", "later-packet.md"))

    def test_understanding_does_not_supply_return_or_motive(self):
        self.assertTrue(FIX["expression"]["understood"])
        self.assertIsNone(FIX["expression"]["return_completed"])
        self.assertIsNone(FIX["expression"]["original_delay_reason"])
        self.assertIn(
            "requires an agreed location and acknowledgment", doc("16.02", "later-packet.md")
        )

    def test_cue_inventory_does_not_invent_unavailable_channels(self):
        for channel in FIX["cues"]["unobserved"]:
            self.assertIn(channel, doc("16.03"))
        self.assertIn("facial movement and tone unobserved", doc("16.03"))
        self.assertEqual(len(FIX["cues"]["supplied"]), 6)
        self.assertIsNone(FIX["cues"]["emotion"])

    def test_clarification_preserves_transport_and_refusal_unknowns(self):
        self.assertEqual(FIX["cues"]["earlier_session"], "possible_unconfirmed")
        self.assertIsNone(FIX["cues"]["transport_confirmed"])
        self.assertFalse(FIX["cues"]["refusal_confirms_annoyance"])
        self.assertIn("Transport remains unknown", doc("16.03", "later-packet.md"))

    def test_pair_and_group_attempts_remain_distinct(self):
        x = FIX["conversation"]
        self.assertEqual(x["pair_limit_minutes"], 5)
        self.assertEqual(x["group_limit_minutes"], 10)
        self.assertFalse(x["group_actual_attempt"])
        self.assertIn("missing group opportunity stays unattempted", doc("16.04"))

    def test_optional_inclusion_is_not_forced_speech_or_idea_adoption(self):
        x = FIX["conversation"]
        self.assertEqual(x["Em_initial_choice"], "watch")
        self.assertEqual(x["Em_later_channel"], "written")
        self.assertTrue(x["Em_idea_considered"])
        self.assertIsNone(x["Em_idea_adopted"])
        self.assertIn("four different events", doc("16.04", "later-packet.md"))

    def test_question_asking_correction_is_not_a_retraction_or_quota(self):
        self.assertIsNone(FIX["conversation"]["question_quota"])
        text = (SOURCE / "SOURCES.md").read_text()
        self.assertIn("Not a retraction", text)
        self.assertIn("distinct methodological dispute", text)
        self.assertIn("no question quota", doc("16.04"))

    def test_report_disconfirms_price_and_dislike_without_authorizing_purchase(self):
        x = FIX["perspective"]
        self.assertTrue(x["museum_preference"])
        self.assertFalse(x["price_objection"])
        self.assertFalse(x["ticket_purchase_authorized"])
        self.assertIsNone(x["parcel_outcome"])
        self.assertIn("ticket purchase now", doc("16.05", "later-packet.md"))

    def test_perspective_keeps_own_deadline_and_unagreed_joint_plan(self):
        self.assertIn(FIX["perspective"]["own_finish"], doc("16.05", "later-packet.md"))
        self.assertIn("jointly agreed before Morgan accepts", doc("16.05", "later-packet.md"))
        self.assertIn("reason for waiting remains unknown", doc("16.05", "later-packet.md"))


class AudienceFeedbackRhetoricTests(unittest.TestCase):
    def test_setup_window_and_public_start_are_different(self):
        x = FIX["audience"]
        self.assertEqual(interval(x["setup_start"], x["setup_end"]), x["setup_minutes"])
        self.assertGreater(interval(x["setup_end"], x["public_start"]), 0)
        self.assertIn("25 minutes", doc("16.06", "later-packet.md"))

    def test_route_and_role_facts_match_complete_case(self):
        x = FIX["audience"]
        guide = doc("16.06")
        for fact in (
            x["room"],
            x["old_room"],
            x["help_start"],
            x["help_end"],
            x["sign_owner"],
            x["boxes_owner"],
        ):
            self.assertIn(fact, guide)
        self.assertNotEqual(x["step_free_entrance"], x["stairs_entrance"])
        self.assertEqual(x["boxes"], 2)

    def test_corrected_visitor_route_does_not_complete_setup_retest(self):
        self.assertEqual(
            FIX["audience"]["visitor_later_route"], FIX["audience"]["step_free_entrance"]
        )
        self.assertIsNone(FIX["audience"]["setup_retest"])
        self.assertIn("setup copy revised but retest pending", doc("16.06", "later-packet.md"))

    def test_invitation_dates_and_duration_are_consistent(self):
        x = FIX["feedback"]
        self.assertEqual(datetime.fromisoformat(x["date"]).strftime("%A"), "Saturday")
        self.assertEqual(datetime.fromisoformat(x["reply_date"]).strftime("%A"), "Thursday")
        self.assertLess(x["reply_date"], x["date"])
        self.assertEqual(interval(x["start"], x["end"]), 90)

    def test_feedback_can_accept_observation_without_color_dependent_fix(self):
        x = FIX["feedback"]
        self.assertFalse(x["example_required"])
        self.assertNotEqual(x["proposed_fix"], x["chosen_fix"])
        self.assertTrue(x["fictional_retest_correct"])
        self.assertIsNone(x["real_retest"])
        self.assertIn("without depending on color", doc("16.07", "later-packet.md"))

    def test_required_cleanup_leaves_no_garden_reserve(self):
        x = FIX["rhetoric"]
        self.assertEqual(x["budget"] - x["materials"] - x["cleanup"], x["reserve"])
        self.assertEqual(x["reserve"], 0)
        self.assertIn("48 + 12 = 60", doc("16.08", "later-packet.md"))

    def test_attendance_does_not_become_maintenance_or_permanent_permission(self):
        x = FIX["rhetoric"]
        self.assertEqual(x["morning_volunteers"], 3)
        self.assertIsNone(x["maintenance_volunteers"])
        self.assertIsNone(x["water_access"])
        self.assertFalse(x["learning_outcome_established"])
        self.assertFalse(x["permanent_garden_approved"])
        self.assertIn("morning only", doc("16.08", "later-packet.md"))

    def test_fresh_rhetoric_cost_exceeds_budget(self):
        x = FIX["fresh"]["rhetoric"]
        self.assertEqual(x["materials"] + x["cleanup"] - x["budget"], x["shortfall"])
        self.assertIn("5-token shortfall", doc("16.08", "check-answers.md"))


class TalkStoryNegotiationTests(unittest.TestCase):
    def test_talk_return_correction_does_not_complete_log_step(self):
        x = FIX["presentation"]
        self.assertNotEqual(x["first_response_return"], x["return_location"])
        self.assertEqual(x["second_response_return"], x["return_location"])
        self.assertTrue(x["return_log_required"])
        self.assertFalse(x["second_response_log"])
        self.assertIn("omits the log update", doc("16.09", "later-packet.md"))

    def test_contact_is_not_automatic_extension_or_actual_delivery(self):
        x = FIX["presentation"]
        self.assertFalse(x["automatic_extension"])
        self.assertFalse(x["actual_delivery"])
        self.assertEqual(x["actual_rehearsal_count"], 0)
        self.assertIn("Do not invent a seven-day entitlement", doc("16.09", "later-packet.md"))
        self.assertIn("two actual rehearsal durations", doc("16.09"))

    def test_story_preserves_information_location_and_fair_character(self):
        x = FIX["story"]
        self.assertNotEqual(x["old_sign"], x["new_sign"])
        self.assertTrue(x["first_two_helpers_followed_old_sign"])
        self.assertFalse(x["Ivo_ignored_visible_new_sign"])
        self.assertIn("not at the place Ivo was deciding", doc("16.10", "later-packet.md"))

    def test_story_resolution_does_not_prove_universal_cause(self):
        x = FIX["story"]
        self.assertTrue(x["later_entrance_sign_corrected"])
        self.assertFalse(x["all_future_errors_prevented"])
        self.assertIn("other causes require their own evidence", doc("16.10", "later-packet.md"))
        self.assertIn("remaining sign gives the wrong room", doc("16.10"))

    def test_original_negotiation_package_meets_both_minima(self):
        x = FIX["negotiation"]
        shared = interval(x["room_start"], x["departure"]) - x["quiet_minimum"]
        self.assertEqual(shared, x["original_shared"])
        self.assertGreaterEqual(shared, x["shared_minimum"])
        self.assertGreater(interval(x["departure"], x["room_end"]), 0)
        self.assertIn("75 shared minutes", doc("16.11", "later-packet.md"))

    def test_changed_departure_makes_package_infeasible(self):
        x = FIX["negotiation"]
        shared = interval(x["room_start"], x["changed_departure"]) - x["quiet_minimum"]
        self.assertEqual(shared, x["changed_shared"])
        self.assertEqual(x["shared_minimum"] - shared, x["changed_shortfall"])
        self.assertIn("30-minute shortfall", doc("16.11", "later-packet.md"))
        self.assertTrue(x["home_alternatives_feasible"])

    def test_fresh_negotiation_uses_departure_not_room_closure(self):
        x = FIX["fresh"]["negotiation"]
        shared = interval(x["start"], x["departure"]) - x["quiet"]
        self.assertEqual(shared, x["shared_available"])
        self.assertEqual(x["shared_minimum"] - shared, x["shortfall"])
        self.assertIn("5 minutes short", doc("16.11", "check-answers.md"))

    def test_negotiation_consent_and_unethical_source_tactic_excluded(self):
        self.assertFalse(FIX["negotiation"]["actual_consent"])
        self.assertIsNone(FIX["negotiation"]["actual_followthrough"])
        self.assertIn("does not adopt its suggestion to worsen", doc("16.11"))
        self.assertIn("not automatic consent", doc("16.11", "later-packet.md"))


class ConflictWarmthTests(unittest.TestCase):
    def test_immediate_remedy_has_confirmation_and_fits(self):
        x = FIX["conflict"]
        self.assertGreater(interval(x["confirmation_received"], x["deadline"]), 0)
        end = datetime.strptime(x["remedy_start"], "%H:%M") + timedelta(
            minutes=x["meeting_minutes"]
        )
        self.assertEqual(end.strftime("%H:%M"), x["meeting_end"])
        self.assertEqual(interval(x["meeting_end"], x["leave"]), x["spare_minutes"])
        self.assertIn("14:55", doc("16.12", "later-packet.md"))

    def test_future_room_remains_unknown_after_overdue_acknowledgment(self):
        x = FIX["conflict"]
        self.assertEqual(
            interval(x["next_confirmation_due"], x["next_checked"]), x["next_overdue_minutes"]
        )
        self.assertIsNone(x["next_room_status"])
        self.assertIn(
            "confirmation overdue and room status unknown", doc("16.12", "later-packet.md")
        )

    def test_threat_branch_ends_peer_exercise_without_forced_blame(self):
        self.assertEqual(FIX["conflict"]["threat_branch"], "end_peer_exercise")
        self.assertIn(
            "Do not require a contribution-to-blame statement", doc("16.12", "later-packet.md")
        )
        self.assertIn("Their insulting conduct remains theirs", doc("16.12", "check-answers.md"))

    def test_fresh_remedy_shortfall_not_hidden_by_calm_agreement(self):
        x = FIX["fresh"]["conflict"]
        self.assertEqual(interval(x["start"], x["leave"]), x["available"])
        self.assertEqual(x["required"] - x["available"], x["shortfall"])
        self.assertIn("10-minute shortfall", doc("16.12", "check-answers.md"))

    def test_smile_does_not_overrule_objection_or_reveal_quiet_person(self):
        x = FIX["humor"]
        self.assertTrue(x["Pat_reported_hurt"] and x["Rem_smiled"])
        self.assertFalse(x["majority_overrides_objection"])
        self.assertIsNone(x["Casey_feelings"])
        self.assertIn("No conclusion about Casey's feelings", doc("16.13", "later-packet.md"))

    def test_warmth_plan_needs_permission_and_actual_attempt(self):
        x = FIX["humor"]
        self.assertTrue(x["warmth_planned"])
        self.assertFalse(x["warmth_actual"])
        self.assertFalse(x["move_material_without_permission"])
        self.assertIn("Wait for permission before moving", doc("16.13", "later-packet.md"))
        self.assertIn(
            "Quick wit and extroversion are not requirements", doc("16.13", "check-answers.md")
        )


if __name__ == "__main__":
    unittest.main()
