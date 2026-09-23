"""Check original source cases and harmless retrieval, never learner competence."""

import hashlib
import json
import re
import shutil
import tempfile
import unittest
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/digital-judgment-preparedness"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"14.{i:02}" for i in range(5, 14)] + [f"15.{i:02}" for i in range(1, 4)]


def doc(cid, filename="learner-guide.md"):
    return (SOURCE / cid / filename).read_text()


def reconciliation(pending, server):
    """The supplied toy service's exact-ID rule, not a real retry implementation."""
    if len(pending) != len(set(pending)):
        raise ValueError("Duplicate request identity")
    result = {}
    for request in pending:
        status = server.get(request)
        if status not in ("accepted", "not received", None):
            raise ValueError("Unrecognized server status")
        result[request] = {
            "accepted": "reconcile accepted",
            "not received": "submit same ID then verify",
            None: "verify or hold",
        }[status]
    return result


class IntegrityTests(unittest.TestCase):
    def test_exact_twelve_and_separate_source_runtime_counts(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertEqual(COHORT["additional_companions_before"], 45)
        self.assertEqual(COHORT["additional_companions_after"], 57)
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        self.assertTrue(COHORT["source_only"])
        self.assertTrue(FIX["synthetic"])
        self.assertFalse(FIX["runtime_evidence"])
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )

    def test_canonical_entries_are_exact_and_inputs_unchanged(self):
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

    def test_sequence_and_runtime_selection_are_distinct(self):
        previous = json.loads((ROOT / "docs/authoring/adaptive-digital/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "14.04")
        implemented = yaml.safe_load(
            (ROOT / "contracts/tailored-practice-authoring.yaml").read_text()
        )["implemented_competency_ids"]
        self.assertFalse(set(IDS) & set(implemented))

    def test_complete_packages_separate_checks_and_all_local_links(self):
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
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target:
                    self.assertTrue(
                        (path.parent / target.split("#")[0]).resolve().is_file(), str(path)
                    )

    def test_scope_maps_preserve_metadata_and_acceptance_limits(self):
        for entry in COHORT["entries"]:
            scope = doc(entry["id"], "SCOPE-MAP.md")
            for field in ("name", "scope", "evidence_of_progress"):
                self.assertIn(entry[field], scope)
            self.assertIn(entry["measurement"]["minimum_standard"], scope)
            if entry.get("professional_boundary"):
                self.assertIn(entry["professional_boundary"], scope)
            self.assertIn("not a formal M6K A/B/C receipt", scope)

    def test_current_contract_preserves_prior_sources_and_deferred_gates(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertTrue(all(isinstance(a, str) for a in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-DIGITAL-JUDGMENT-PREPAREDNESS-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                "growth/**",
                ".github/**",
                "docs/authoring/adaptive-digital/**",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


class RequestAndFeedTests(unittest.TestCase):
    def test_six_distinct_requests_and_independent_underlying_need(self):
        rows = re.findall(r"^\| (S\d) \|", doc("14.05"), re.M)
        self.assertEqual(rows, FIX["scams"]["ids"])
        self.assertFalse(FIX["scams"]["bank_authorized"])
        self.assertTrue(FIX["scams"]["club_renewal_due"])
        self.assertFalse(FIX["scams"]["club_download_required"])
        later = doc("14.05", "later-packet.md")
        self.assertIn("real renewal need does not validate", later)

    def test_reported_exposure_is_not_recovery_or_refund(self):
        case = FIX["scams"]
        self.assertTrue(case["code_reported"])
        self.assertIsNone(case["account_recovery_complete"])
        self.assertEqual(case["payment_sent"], 300)
        self.assertIsNone(case["payment_recovered"])
        self.assertIn("No refund decision", doc("14.05", "later-packet.md"))
        self.assertIn("120 remains an exposed payment", doc("14.05", "check-answers.md"))

    def test_feed_card_categories_and_independent_source_count(self):
        cards = FIX["feed"]["cards"]
        self.assertEqual(
            Counter(c[1] for c in cards),
            {
                "direct": 4,
                "adjacent": 3,
                "provocative": 1,
                "unrelated": 2,
            },
        )
        self.assertEqual({c[2] for c in cards if c[1] == "direct"}, {"G", "nursery"})
        self.assertEqual(re.findall(r"^\| (F\d+) \|", doc("14.06"), re.M), [c[0] for c in cards])
        self.assertIn("F9 is another occurrence of F1", doc("14.06"))

    def test_two_observed_sessions_and_canceled_opportunity(self):
        records = FIX["feed"]["sessions"]
        observed = [r for r in records if r["occurred"] is True]
        self.assertEqual(len(observed), 2)
        self.assertEqual(sum(r["minutes"] for r in observed), 19)
        self.assertEqual(sum(r["endpoint"] is True for r in observed), 1)
        self.assertEqual(sum(r["minutes"] for r in observed) / len(observed), 9.5)
        self.assertTrue(all(records[-1][k] is None for k in ("minutes", "endpoint", "shifts")))
        later = doc("14.06", "later-packet.md")
        for phrase in (
            "18:00\u201318:12",
            "18:00\u201318:07",
            "mean observed duration is 9.5",
            "not a causal",
        ):
            self.assertIn(phrase, later)

    def test_fresh_feed_denominator_excludes_cancellation(self):
        values = FIX["feed"]["fresh_minutes"]
        self.assertEqual(sum(values), 14)
        self.assertEqual(sum(values) / len(values), 7)
        self.assertIn(
            "Two observed sessions, 14 minutes, mean seven", doc("14.06", "check-answers.md")
        )


class AIAuditTests(unittest.TestCase):
    def test_corrected_notice_preserves_all_source_facts_within_limit(self):
        later = doc("14.07", "later-packet.md")
        notice = later.split("“")[1].split("”")[0]
        for value in FIX["ai"]["source"].values():
            self.assertIn(value, notice)
        self.assertEqual(len(notice.split()), 39)
        self.assertLessEqual(len(notice.split()), 70)
        self.assertNotIn("guarantee", notice)
        self.assertNotIn("Report 2026", notice)
        self.assertIn("39 whitespace-delimited words", later)

    def test_correction_and_verification_cost_counted(self):
        case = FIX["ai"]
        manual = sum(case["manual_minutes"])
        assisted = sum(case["assisted_minutes"])
        self.assertEqual((manual, assisted, assisted - manual), (8, 11, 3))
        self.assertIn("Manual total: eight minutes", doc("14.07", "later-packet.md"))
        self.assertIn("Assisted total: eleven minutes", doc("14.07", "later-packet.md"))

    def test_fresh_effort_and_private_input_are_separate_defects(self):
        case = FIX["ai"]
        self.assertEqual(sum(case["fresh_assisted_minutes"]) - sum(case["fresh_manual_minutes"]), 4)
        key = doc("14.07", "check-answers.md")
        self.assertIn("four minutes slower", key)
        self.assertIn("does not grant permission retroactively", key)

    def test_contradiction_unsupported_and_framing_are_distinct(self):
        guide = doc("14.07")
        for phrase in (
            "day and fee conflict",
            "lack support",
            "Young professionals",
            "unnecessarily narrows",
        ):
            self.assertIn(phrase, guide)
        self.assertIn("That remains unsupported", doc("14.07", "later-packet.md"))


class ProvenanceAndChronologyTests(unittest.TestCase):
    def test_validated_asset_does_not_supply_truth_or_identity(self):
        case = FIX["provenance"]
        self.assertFalse(set(case["validated_D"]) & set(case["not_validated_D"]))
        self.assertIsNone(case["event_reply"]["origin"])
        self.assertIn("no claim about the event date", doc("14.08").lower())
        self.assertIn("not a validation result", doc("14.08"))

    def test_partial_event_reply_does_not_fill_unknown_venue(self):
        case = FIX["provenance"]
        self.assertEqual(case["partial_reply"]["fee"], 0)
        self.assertIsNone(case["partial_reply"]["venue"])
        later = doc("14.08", "later-packet.md")
        self.assertIn("Only the fee is resolved", later)
        self.assertIn("mutually exclusive replies", later)

    def test_reposts_trace_to_one_origin(self):
        edges = FIX["library"]["copies"]
        path = ["C"]
        while path[-1] in edges:
            path.append(edges[path[-1]])
        self.assertEqual(path, ["C", "B", "A"])
        self.assertIn("C → B → A", doc("14.09"))

    def test_relative_date_keeps_original_publication_anchor(self):
        case = FIX["library"]
        self.assertEqual(
            date.fromisoformat(case["publication"]) + timedelta(days=1),
            date.fromisoformat(case["tomorrow_event"]),
        )
        self.assertIn("means May 5", doc("14.09"))
        self.assertIn("August 3", doc("14.09", "check-answers.md"))

    def test_later_record_changes_interval_not_permanence_or_actual_reopening(self):
        case = FIX["library"]
        self.assertEqual(len(case["west_closed"]), 3)
        self.assertEqual(case["new_whole_closure"], ["2026-05-06"])
        self.assertIn(case["new_whole_closure"][0], case["west_closed"])
        self.assertFalse(case["reopening_observed"])
        later = doc("14.09", "later-packet.md")
        self.assertIn("planned and conditional, not observed", later)
        self.assertIn("one-day whole-library closure", later)

    def test_manual_versions_do_not_establish_misconduct(self):
        self.assertEqual(FIX["conduct"]["margin_by_version"], {"2": 8, "3": 6})
        later = doc("14.10", "later-packet.md")
        self.assertIn("version 2 manual confirms 8", later)
        self.assertIn("version 3 manual still says 6", later)
        self.assertFalse(FIX["conduct"]["default_posted"])
        self.assertFalse(FIX["conduct"]["private_chat_consent"])

    def test_moderation_receipt_is_not_resolution(self):
        self.assertEqual(FIX["conduct"]["public_targeting_posts"], 3)
        self.assertEqual(FIX["conduct"]["report_status"], "acknowledged")
        self.assertIsNone(FIX["conduct"]["resolved"])
        self.assertIn("No review decision or removal", doc("14.10", "later-packet.md"))


class RightsAndContinuityTests(unittest.TestCase):
    def test_rights_conditions_are_specific_to_stipulated_use(self):
        case = FIX["rights"]
        self.assertEqual(case["use"], "primarily commercial")
        self.assertTrue(case["creative_adaptation"])
        self.assertTrue(case["A"]["permitted"])
        self.assertFalse(case["B"]["permitted"])
        self.assertFalse(case["C"]["permitted"])
        self.assertIsNone(case["D"]["permitted"])
        guide = doc("14.11")
        self.assertIn("not just file format", guide)
        self.assertIn("No separate permission to share", guide)

    def test_credit_and_distribution_preserve_required_distinctions(self):
        case = FIX["rights"]["A"]
        guide = doc("14.11")
        for value in case.values():
            if isinstance(value, str):
                self.assertIn(value, guide)
        self.assertIn("recolored blue", guide)
        later = doc("14.11", "later-packet.md")
        self.assertIn("crops away the credit line", later)
        self.assertIn("cannot accurately describe", later)

    def test_payment_and_possession_do_not_create_missing_permission(self):
        self.assertFalse(FIX["rights"]["E"]["publication_authorized"])
        self.assertFalse(FIX["rights"]["actual_publication"])
        later = doc("14.11", "later-packet.md")
        self.assertIn("would not remove B's NonCommercial condition", later)
        self.assertIn("Exclude those personal records", later)
        self.assertIn("copyright and permission notice", doc("14.11", "check-answers.md"))

    def test_actual_local_fallback_retrieval_preserves_originals(self):
        materials = SOURCE / "14.12/materials"
        before = {p.name: p.read_bytes() for p in materials.iterdir() if p.is_file()}
        with tempfile.TemporaryDirectory() as tmp:
            fallback = Path(tmp) / "event-fallback.txt"
            shutil.copyfile(materials / "event-v2.txt", fallback)
            # Open the created fallback independently; inspect answers from its saved bytes.
            retrieved = fallback.read_text().splitlines()
            self.assertTrue(set(FIX["continuity"]["required_lines"]) <= set(retrieved))
            self.assertEqual(fallback.read_bytes(), before["event-v2.txt"])
        self.assertEqual(
            before, {p.name: p.read_bytes() for p in materials.iterdir() if p.is_file()}
        )

    def test_stale_copy_and_truncated_contact_fail_minimum_answers(self):
        materials = SOURCE / "14.12/materials"
        required = set(FIX["continuity"]["required_lines"])
        stale = set((materials / "event-v1.txt").read_text().splitlines())
        current = set((materials / "event-v2.txt").read_text().splitlines())
        self.assertEqual(len(required - stale), 2)  # Room and entry directions changed.
        self.assertTrue(required <= current)
        missing_contact = current - {FIX["continuity"]["required_lines"][-1]}
        self.assertFalse(required <= missing_contact)
        self.assertIn("freshness failed", doc("14.12", "later-packet.md"))

    def test_request_materials_match_fixture_statuses(self):
        materials = SOURCE / "14.12/materials"
        pending = [
            line.split(" | ")[0] for line in (materials / "outbox.txt").read_text().splitlines()[1:]
        ]
        server = {
            line.split(" | ")[0]: line.split(" | ")[1]
            for line in (materials / "server-receipts.txt").read_text().splitlines()[1:]
        }
        self.assertEqual(pending, FIX["continuity"]["local_pending"])
        self.assertEqual(server, FIX["continuity"]["server"])
        self.assertEqual(
            reconciliation(pending, server),
            {
                "R-41": "reconcile accepted",
                "R-42": "submit same ID then verify",
            },
        )

    def test_unknown_server_state_is_not_confirmed_absence(self):
        self.assertEqual(
            reconciliation(["P-1", "P-2"], FIX["continuity"]["fresh_server"]),
            {
                "P-1": "reconcile accepted",
                "P-2": "verify or hold",
            },
        )
        self.assertEqual(
            reconciliation(["R-41", "R-42"], {}),
            {
                "R-41": "verify or hold",
                "R-42": "verify or hold",
            },
        )
        self.assertIn("not confirmed missing", doc("14.12", "check-answers.md"))

    def test_duplicate_identity_and_unrecognized_status_are_not_silently_retried(self):
        for pending, server in ((["R-41", "R-41"], {}), (["R-41"], {"R-41": "maybe"})):
            with self.subTest(pending=pending, server=server), self.assertRaises(ValueError):
                reconciliation(pending, server)


class PolicyAndPreparednessTests(unittest.TestCase):
    def test_baseline_queue_has_no_reserve(self):
        p = FIX["policy"]
        capacity = p["moderators"] * p["minutes_each"]
        demand = (
            p["baseline_ordinary"] * p["ordinary_minutes"] + p["urgent_count"] * p["urgent_minutes"]
        )
        self.assertEqual((capacity, demand, capacity - demand), (60, 60, 0))
        self.assertIn("zero reserve", doc("14.13", "later-packet.md"))

    def test_surge_and_fresh_queue_count_complete_reviews(self):
        p = FIX["policy"]
        capacity = p["moderators"] * p["minutes_each"]
        demand = p["surge_ordinary"] * p["ordinary_minutes"] + p["urgent_minutes"]
        self.assertEqual(demand - capacity, 20)
        self.assertEqual((capacity - p["urgent_minutes"]) // p["ordinary_minutes"], 4)
        fresh_demand = p["fresh_ordinary"] * p["ordinary_minutes"] + p["urgent_minutes"]
        self.assertEqual(fresh_demand - p["fresh_capacity"], 5)
        self.assertEqual(
            divmod(p["fresh_capacity"] - p["urgent_minutes"], p["ordinary_minutes"]), (2, 5)
        )
        self.assertIn("two complete ordinary reviews", doc("14.13", "check-answers.md"))

    def test_appeal_access_and_off_hours_are_not_closed_by_policy_text(self):
        later = doc("14.13", "later-packet.md")
        for phrase in (
            "cannot use the slider",
            "cannot reach the form behind login",
            "off-hours coverage unresolved",
        ):
            self.assertIn(phrase, later)

    def test_course_selection_covers_topics_without_awarding_attendance(self):
        case = FIX["first_aid"]
        courses = case["courses"]
        self.assertEqual(
            set(courses["B"]["observed"]) | set(courses["C"]["observed"]), set(case["topics"])
        )
        self.assertEqual(courses["A"]["observed"], [])
        self.assertEqual(case["C_status"], "booked")
        self.assertIn("does not prove that either was attended or passed", doc("15.01"))

    def test_supplied_receipt_scope_does_not_include_unassessed_topics(self):
        receipt = FIX["first_aid"]["receipt"]
        self.assertEqual(
            {k for k, v in receipt.items() if v == "satisfactory observed"}, {"CPR", "AED"}
        )
        self.assertEqual(receipt["choking"], "not assessed")
        self.assertEqual(receipt["communication"], "role-play with correction")
        self.assertIn("Only two physical topics", doc("15.01", "later-packet.md"))

    def test_delegation_and_unsafe_scene_preserve_unknowns(self):
        case = FIX["first_aid"]
        self.assertEqual((case["entrance_before"], case["entrance_after"]), ("east", "north"))
        for field in ("aed_fetched", "aed_used", "hazard_breathing"):
            self.assertIsNone(case[field])
        later = doc("15.01", "later-packet.md")
        self.assertIn("No AED retrieval is recorded yet", later)
        self.assertIn("cannot safely establish responsiveness or breathing", later)

    def test_household_all_six_hazards_have_case_rows(self):
        rows = re.findall(r"^\| ([^|]+) \|", doc("15.02"), re.M)
        self.assertTrue(set(FIX["household"]["hazards"]) <= set(rows))

    def test_household_repair_does_not_close_external_dependencies(self):
        case = FIX["household"]
        self.assertFalse(case["initial"]["lantern_works"])
        self.assertTrue(case["later"]["lantern_works"])
        self.assertTrue(case["later"]["contact_retrieved"])
        self.assertFalse(case["later"]["contact_called"])
        self.assertIsNone(case["later"]["care_plan"])
        self.assertIsNone(case["later"]["transport_confirmed"])
        self.assertFalse(case["later"]["helper_consented"])
        later = doc("15.02", "later-packet.md")
        self.assertIn("No actual call is attempted", later)
        self.assertIn("no instructions, battery duration or confirmed arrangement", later)

    def test_access_route_requires_both_open_and_suitable(self):
        case = FIX["awareness"]

        def usable(routes):
            return [name for name, r in routes.items() if r["open"] is True and r["level"] is True]

        self.assertEqual(usable(case["initial_routes"]), ["east"])
        self.assertEqual(usable(case["changed_routes"]), [])
        changed = dict(case["changed_routes"], garden=case["A_garden"])
        self.assertEqual(usable(changed), ["garden"])
        self.assertIsNone(case["north_exit_suitable"])
        self.assertIn(
            "North-exit emergency suitability still has no confirmation",
            doc("15.03", "later-packet.md"),
        )

    def test_alternative_goal_and_absent_visit_do_not_fabricate_traversal(self):
        case = FIX["awareness"]
        self.assertTrue(case["B"]["desk_pickup"])
        self.assertFalse(case["B"]["garden_traversed"])
        self.assertEqual(
            case["visits"],
            [{"occurred": True, "changed": False}, {"occurred": False, "changed": None}],
        )
        later = doc("15.03", "later-packet.md")
        self.assertIn("Do not record garden traversal", later)
        self.assertIn("absence of an observation is not an observation of no change", later)


if __name__ == "__main__":
    unittest.main()
