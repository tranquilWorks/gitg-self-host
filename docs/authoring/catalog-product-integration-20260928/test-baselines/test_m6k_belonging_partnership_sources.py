"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/belonging-partnership"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"17.{i:02}" for i in range(8, 15)] + [f"18.{i:02}" for i in range(1, 6)]


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
        self.assertEqual(COHORT["additional_companions_before"], 93)
        self.assertEqual(COHORT["additional_companions_after"], 105)
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
        for domain in ("17", "18"):
            self.assertEqual(
                (ROOT / f"docs/authoring/exercises/{domain}.yaml").read_bytes(),
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_bytes(),
            )

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads(
            (ROOT / "docs/authoring/respectful-connection/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "17.07")
        self.assertEqual(previous["additional_companions_after"], 93)
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

    def test_partnership_role_conditional_and_exact_professional_boundary(self):
        for e in COHORT["entries"]:
            if e["id"].startswith("18."):
                self.assertEqual(e["classification"]["applicability"], "role_conditional")
                self.assertEqual(e["classification"]["normative_status"], "role_conditional")
                for name in ("learner-guide.md", "SCOPE-MAP.md"):
                    self.assertIn(e["professional_boundary"], doc(e["id"], name))
                self.assertIn("single life", doc(e["id"]).lower())
                self.assertIn("fiction", doc(e["id"]).lower())
                self.assertIn("optional", doc(e["id"]).lower())
            else:
                self.assertEqual(e["classification"]["applicability"], "cross_context_core")

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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 14)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for s in sources:
            self.assertEqual(s["inspected"], "2026-09-24")
            self.assertTrue(s["sections"])
            self.assertTrue(s["limits"])
        for sid in ("S01", "S07", "S10", "S11"):
            self.assertIn("abstract", next(s for s in sources if s["id"] == sid)["limits"].lower())
        self.assertIn(
            "Opening sections only", next(s for s in sources if s["id"] == "S12")["limits"]
        )

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
        if contract["batch"]["id"] == "M6K-BELONGING-PARTNERSHIP-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/respectful-connection/**",
                "tests/test_m6k_respectful_connection_sources.py",
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
    def test_collaboration_rework_and_actual_roles(self):
        f = FIX["collaboration"]
        self.assertNotEqual(f["confirmed_room"], f["obsolete_room"])
        self.assertEqual(f["offered_minutes"]["Dev"] + f["extra_minutes"], 25)
        self.assertTrue(f["extra_agreed"])
        self.assertFalse(f["credit_public"])
        self.assertIn("private acknowledgment", doc("17.08"))

    def test_collaboration_partial_reader_result_not_superiority(self):
        f = FIX["collaboration"]
        self.assertEqual(sum(f["reader"].values()), 3)
        self.assertFalse(f["reader"]["entrance"])
        self.assertFalse(f["retest_performed"])
        self.assertFalse(f["isolated_comparator"])
        self.assertIn("no isolated-work comparator", doc("17.08", "later-packet.md"))

    def test_ecology_first_visit_feasible_changed_visit_late(self):
        f = FIX["ecology"]
        self.assertEqual(arrive(f["outbound"], f["travel_minutes"]), "09:50")
        home = arrive(f["return_bus"], f["travel_minutes"])
        self.assertEqual(home, "11:30")
        self.assertEqual(minutes(home, f["original_duty"]), 10)
        self.assertEqual(minutes(f["changed_duty"], home), 15)
        self.assertIn("fifteen minutes late", doc("17.09", "later-packet.md"))

    def test_ecology_later_date_is_unconfirmed_not_friendship(self):
        f = FIX["ecology"]
        first = datetime.fromisoformat(f["first_visit"])
        later = datetime.fromisoformat(f["possible_later"])
        self.assertEqual((later - first).days, 14)
        self.assertEqual(first.weekday(), 5)
        self.assertFalse(f["later_confirmed"])
        self.assertFalse(f["friendship_established"])
        self.assertIn("Chosen solitude", doc("17.09", "check-answers.md"))

    def test_network_one_permission_cannot_authorize_introduction(self):
        f = FIX["network"]
        self.assertTrue(f["requester_consents"])
        self.assertFalse(f["helper_consents"])
        self.assertFalse(f["introduction_made"])
        self.assertFalse(f["phone_permitted"])
        self.assertNotIn("phone", f["permitted_details"])

    def test_network_resource_usefulness_is_partial(self):
        f = FIX["network"]
        self.assertTrue(f["resource_offered"])
        self.assertEqual(f["understood_shapes"], 1)
        self.assertLess(f["understood_shapes"], f["total_shapes"])
        self.assertFalse(f["tutoring_performed"])
        self.assertIn("No introduction", doc("17.10", "later-packet.md"))

    def test_mentoring_context_and_reciprocal_contributions(self):
        f = FIX["mentoring"]
        self.assertFalse(f["drop_in_authorized"])
        self.assertTrue(f["portal_required"])
        self.assertTrue(f["both_contributions_reported"])
        self.assertIn("aged 29", doc("17.11"))
        self.assertIn("aged 67", doc("17.11"))

    def test_mentoring_twelve_days_and_no_standing_relationship(self):
        f = FIX["mentoring"]
        days = (datetime.fromisoformat(f["followup"]) - datetime.fromisoformat(f["exchange"])).days
        self.assertEqual(days, 12)
        self.assertLessEqual(days, f["followup_limit_days"])
        self.assertFalse(f["ongoing_mentorship"])
        self.assertFalse(f["next_meeting_accepted"])
        self.assertIn("sixteen days", doc("17.11", "check-answers.md"))

    def test_obligation_work_gap_separates_done_and_offered(self):
        f = FIX["obligation"]
        done = minutes(f["own_start"], f["own_end"])
        self.assertEqual(done, 30)
        self.assertEqual(f["total_person_minutes"] - done, 60)
        self.assertEqual(f["total_person_minutes"] - done - f["len_offered_minutes"], 40)
        self.assertIsNone(f["len_performed_minutes"])
        self.assertIn("Sixty minutes of work remains unperformed", doc("17.12", "later-packet.md"))

    def test_obligation_travel_no_hidden_assignment_or_care_withdrawal(self):
        f = FIX["obligation"]
        self.assertEqual(arrive(f["own_end"], f["travel_minutes"]), f["duty"])
        self.assertFalse(f["priya_remaining_accepted"])
        self.assertFalse(f["rotation_decided"])
        self.assertFalse(f["essential_care_task"])
        self.assertIn("Do not withdraw essential care", doc("17.12", "check-answers.md"))

    def test_difference_understanding_without_conversion(self):
        f = FIX["difference"]
        self.assertTrue(f["summaries_confirmed"])
        self.assertFalse(f["priority_agreement"])
        self.assertFalse(f["conversion"])
        self.assertTrue(f["topic_stopped"])

    def test_difference_ordinary_care_not_attendance_or_dignity_debate(self):
        f = FIX["difference"]
        self.assertTrue(f["walk_confirmed"])
        self.assertIsNone(f["walk_attended"])
        self.assertIn("not yet attendance", doc("17.13", "later-packet.md"))
        self.assertIn("debating personhood", doc("17.13", "check-answers.md"))

    def test_group_feasibility_and_authority(self):
        f = FIX["group"]
        self.assertEqual(f["trip_cost"] - f["budget"], 220)
        self.assertFalse(f["host_confirmed"])
        self.assertFalse(f["room_confirmed"])
        self.assertFalse(f["local_event_approved"])
        self.assertIn("cannot approve a new event", doc("17.14"))

    def test_group_contribution_promise_and_unknown_pressure(self):
        f = FIX["group"]
        self.assertTrue(f["inventory_completed"])
        self.assertTrue(f["retreat_optional"])
        self.assertTrue(f["message_change_promised"])
        self.assertIsNone(f["message_changed"])
        self.assertIsNone(f["later_social_pressure"])
        self.assertIn("did not purchase assent", doc("17.14", "later-packet.md"))

    def test_love_care_and_commitment_not_attention_debt(self):
        f = FIX["love"]
        self.assertTrue(f["quiet_respected"] and f["errand_accepted"] and f["errand_done"])
        self.assertTrue(f["usefulness_report"])
        self.assertFalse(f["gratitude_debt"])
        self.assertIsNone(f["counteroffer_accepted"])
        self.assertFalse(f["attention_scheduled"])

    def test_love_all_eight_distinctions_and_control_boundary(self):
        text = doc("18.01").lower()
        for term in (
            "affection",
            "desire",
            "attachment",
            "care",
            "commitment",
            "sacrifice",
            "admiration",
            "possession",
        ):
            self.assertIn(term, text)
        self.assertIn("Control and isolation", doc("18.01", "check-answers.md"))
        self.assertIn("no conversation is mutually scheduled", doc("18.01", "later-packet.md"))

    def test_courtship_refusal_ends_pursuit_without_invented_mutuality(self):
        f = FIX["courtship"]
        self.assertTrue(f["adults"])
        self.assertFalse(f["power_dependency"])
        self.assertIsNone(f["romantic_interest_mutual"])
        self.assertEqual(f["answer"], "declined")
        self.assertFalse(f["date_scheduled"])
        self.assertTrue(f["pursuit_stopped"])
        self.assertFalse(f["group_friendliness_reopens"])

    def test_courtship_no_automatic_intimacy_or_dependency_route(self):
        answers = doc("18.02", "check-answers.md")
        self.assertIn("did not authorize a kiss", answers)
        self.assertIn("power that may make refusal costly", answers)
        self.assertIn("Uncertainty is not consent", answers)
        self.assertIn("does not require a particular performance", doc("18.02"))

    def test_compatibility_material_mismatch_before_lease_deadline(self):
        f = FIX["compatibility"]
        gap = datetime.fromisoformat(f["lease_deadline"]) - datetime.fromisoformat(
            f["placement_offer"]
        )
        self.assertEqual(gap.days, 8)
        self.assertTrue(f["placement_accepted_intention"])
        self.assertFalse(f["both_want_long_distance"])
        self.assertTrue(f["joint_lease_declined"])
        self.assertFalse(f["lease_signed"])
        self.assertIsNone(f["future_contact_agreed"])

    def test_compatibility_positive_evidence_and_no_secret_tests(self):
        f = FIX["compatibility"]
        self.assertEqual(f["positive_kept_plans"], 3)
        self.assertEqual(f["notified_cancellations"], 1)
        self.assertIn("do not remove", doc("18.03", "later-packet.md"))
        self.assertIn("Deception and surveillance are excluded", doc("18.03", "check-answers.md"))
        for facet in (
            "values",
            "character",
            "conflict style",
            "direction",
            "attraction",
            "trust",
            "responsibility",
            "life constraints",
        ):
            self.assertIn(facet, doc("18.03").lower())

    def test_attachment_nonresponse_inside_agreed_unavailability(self):
        f = FIX["attachment"]
        self.assertGreater(minutes(f["unavailable_start"], f["message_time"]), 0)
        self.assertGreater(minutes(f["no_response_at"], f["unavailable_end"]), 0)
        self.assertEqual(f["extra_messages_sent"], 0)
        self.assertFalse(f["retaliatory_silence"])
        self.assertIn("not a broken check-in commitment", doc("18.04", "later-packet.md"))

    def test_attachment_counteroffer_fits_but_no_cure_or_standing_schedule(self):
        f = FIX["attachment"]
        self.assertGreaterEqual(minutes(f["available_start"], f["agreed_start"]), 0)
        self.assertEqual(minutes(f["agreed_start"], f["agreed_end"]), 10)
        self.assertEqual(f["agreed_end"], f["available_end"])
        self.assertTrue(f["checkin_performed"])
        self.assertFalse(f["standing_schedule"])
        self.assertFalse(f["attachment_diagnosed"])
        self.assertIn("Repeated breaches are relevant behavior", doc("18.04", "check-answers.md"))

    def test_intimacy_postponed_readiness_and_corrected_uncertainty(self):
        f = FIX["intimacy"]
        self.assertFalse(f["ready_tonight"])
        self.assertTrue(f["conversation_completed"])
        self.assertTrue(f["misunderstanding_corrected"])
        self.assertFalse(f["applied"] or f["enrolled"] or f["tuesday_changes_agreed"])
        self.assertIn("no application or enrollment", doc("18.05", "later-packet.md"))

    def test_intimacy_privacy_and_future_step_not_equal_disclosure(self):
        f = FIX["intimacy"]
        self.assertFalse(f["equal_disclosure_required"])
        self.assertFalse(f["friend_story_shared"])
        self.assertTrue(f["schedule_review_agreed"])
        self.assertFalse(f["schedule_review_performed"])
        self.assertIn("No equal-disclosure requirement", doc("18.05", "check-answers.md"))
        self.assertIn("not evidence that a disclosure occurred", doc("18.05"))


if __name__ == "__main__":
    unittest.main()
