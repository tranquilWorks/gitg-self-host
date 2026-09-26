"""Integrity and supplied-case checks; these do not grade learners or runtime evidence."""

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/leisure-life-design"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
CASES = FIX["cases"]
IDS = [f"26.{i:02}" for i in range(5, 15)] + ["27.01", "27.02"]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


def minute(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{2}:[0-9]{2}", value):
        raise ValueError("Expected HH:MM")
    hour, mins = map(int, value.split(":"))
    if hour > 23 or mins > 59:
        raise ValueError("Invalid clock time")
    return hour * 60 + mins


def table(cid):
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in doc(cid).splitlines()
        if line.startswith("|") and "---" not in line
    ][1:]


class IntegrityTests(unittest.TestCase):
    def test_exact_ids_files_and_runtime_boundary(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
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
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(COHORT["reporting_cadence"], 12)

    def test_canonical_entries_and_six_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        self.assertEqual(
            COHORT["entries"],
            [
                e
                for d in catalog["curriculum"]["domains"]
                for e in d["competencies"]
                if e["id"] in IDS
            ],
        )
        self.assertEqual(len(COHORT["input_sha256"]), 6)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_current_recovery_inputs_remain_equal(self):
        for domain in ("26", "27"):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            self.assertEqual(current, recovery)
            for cid in (x for x in IDS if x.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_individual_scope_maps_preserve_metadata(self):
        for entry in COHORT["entries"]:
            scope = doc(entry["id"], "SCOPE-MAP.md")
            for key in ("name", "scope", "evidence_of_progress"):
                self.assertIn(entry[key], scope)
            for value in entry["classification"].values():
                for item in value if isinstance(value, list) else [value]:
                    self.assertIn(item, scope)
            for item in entry["measurement"]["preferred_evidence_types"]:
                self.assertIn(item, scope)
            self.assertIn(entry["measurement"]["minimum_standard"], scope)
            self.assertIn("not a new exercise scoring rule", scope)
            self.assertIn("Human dignity is never scored", scope)

    def test_classification_modes_and_absent_boundary(self):
        for entry in COHORT["entries"]:
            self.assertNotIn("professional_boundary", entry)
            self.assertEqual(entry["classification"]["applicability"], "cross_context_core")
            self.assertEqual(
                entry["classification"]["normative_status"],
                "cross_tradition_core_or_broadly_recurrent",
            )
            expected = (
                ["receptivity", "interdependence", "transcendence"]
                if entry["id"].startswith("26.")
                else ["agency", "receptivity", "interdependence", "stewardship"]
            )
            self.assertEqual(entry["classification"]["formation_modes"], expected)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn("no professional_boundary field", doc(entry["id"], name))

    def test_source_coverage_is_disjoint_and_complete(self):
        cov = COHORT["source_coverage"]
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        canonical = {e["id"] for d in catalog["curriculum"]["domains"] for e in d["competencies"]}
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        implemented = set(contract["implemented_competency_ids"])
        paths = cov["prior_companion_guides"]
        directories = {str(Path(p).parent.parent) for p in paths}
        actual = {
            str(p.relative_to(ROOT))
            for d in directories
            for p in (ROOT / d).glob("*/learner-guide.md")
        }
        self.assertEqual(set(paths), actual)
        prior = [Path(p).parent.name for p in paths]
        self.assertEqual(len(prior), len(set(prior)))
        self.assertEqual(len(prior), 225)
        self.assertEqual(sorted(prior), cov["prior_companion_ids"])
        self.assertEqual(sorted(implemented), cov["implemented_ids"])
        self.assertFalse(implemented & set(prior))
        self.assertFalse((implemented | set(prior)) & set(IDS))
        covered = implemented | set(prior) | set(IDS)
        self.assertEqual(len(covered), 345)
        self.assertEqual(cov["covered_count"], 345)
        self.assertEqual(sorted(canonical - covered), cov["remaining_ids"])
        self.assertEqual(cov["remaining_count"], 38)
        self.assertEqual(
            dict(Counter(cid[:2] for cid in canonical - covered)), {"07": 14, "08": 11, "27": 13}
        )
        self.assertEqual(cov["remaining_by_domain"], {"07": 14, "08": 11, "27": 13})
        self.assertEqual(COHORT["additional_companions_after"], 237)
        self.assertIn("08.02", cov["remaining_ids"])
        self.assertIn("27.03", cov["remaining_ids"])

    def test_predecessor_and_no_new_legacy_selection(self):
        old = json.loads((ROOT / "docs/authoring/creative-culture-leisure/cohort.json").read_text())
        self.assertEqual(old["ids"][-1], "26.04")
        self.assertEqual(old["additional_companions_after"], COHORT["additional_companions_before"])
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        self.assertFalse(set(IDS) & set(contract["retained_legacy_competency_ids"]))
        self.assertEqual(COHORT["legacy_companion_ids"], [])

    def test_checks_have_three_separate_answers(self):
        for cid in IDS:
            for name in ("check-prompts.md", "check-answers.md"):
                self.assertEqual(re.findall(r"^(\d)\. ", doc(cid, name), re.M), ["1", "2", "3"])
            self.assertNotEqual(doc(cid, "check-prompts.md"), doc(cid, "check-answers.md"))

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

    def test_nine_inspected_sources_and_excluded_routes(self):
        sources = json.loads((SOURCE / "sources.json").read_text())["sources"]
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 10)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-26")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        self.assertIn("transcript not inspected", sources[6]["limits"])
        self.assertIn("minimal challenge page", (SOURCE / "SOURCES.md").read_text())
        self.assertIn("retrieval errors", (SOURCE / "SOURCES.md").read_text())

    def test_fiction_and_formal_review_boundaries(self):
        self.assertTrue(FIX["all_responses_supplied_fiction"])
        self.assertFalse(FIX["actual_participant_evidence"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        self.assertEqual(set(CASES), set(IDS))
        for cid in IDS:
            self.assertIn("Supplied fiction", doc(cid, "later-packet.md"))
            self.assertIn("remain pending", doc(cid, "SCOPE-MAP.md"))
            self.assertIn(f"## {cid}", (SOURCE / "QUALITY-REVIEW.md").read_text())

    def test_verification_exact_source_and_test_bytes(self):
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

    def test_active_contract_valid_and_scoped(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertTrue(all(isinstance(x, str) for x in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-LEISURE-LIFE-DESIGN-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/creative-culture-leisure/**",
                "tests/test_m6k_creative_culture_leisure_sources.py",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


class IndividualCaseTests(unittest.TestCase):
    def test_2605_route_table_and_return_math(self):
        f = CASES["26.05"]
        self.assertEqual([int(row[1]) for row in table("26.05")], [s[2] for s in f["segments"]])
        self.assertIn("Closed", table("26.05")[2][2])
        total = 2 * (f["segments"][0][2] + f["segments"][1][2]) + f["pause"]
        self.assertEqual(minute(f["start"]) + total, minute(f["planned_return"]))
        self.assertLess(minute(f["planned_return"]), minute(f["deadline"]))
        self.assertEqual(minute(f["start"]) + 14 + 5, minute(f["turnaround"]) - 1)

    def test_2605_actual_return_and_contact_are_distinct(self):
        f = CASES["26.05"]
        times = [minute(t) for _, t in f["actual"]]
        self.assertEqual(times, sorted(times))
        self.assertEqual(times[2] - times[1], 6)
        self.assertFalse(f["visited_overlook"])
        later = doc("26.05", "later-packet.md")
        for _, t in f["actual"]:
            self.assertIn(t, later)
        self.assertIn("No overlook visit", later)

    def test_2606_travel_options_and_actual_timeline(self):
        f = CASES["26.06"]
        for key, ret in (
            ("hall_only", "hall_return"),
            ("combined", "combined_return"),
            ("actual", "actual_return"),
        ):
            self.assertEqual(minute(f["start"]) + sum(f[key]), minute(f[ret]))
        self.assertGreater(minute(f["combined_return"]), minute(f["deadline"]))
        self.assertEqual(sum(f["actual"]) - sum(f["hall_only"]), 5)
        self.assertIn("five additional minutes", doc("26.06", "later-packet.md"))
        self.assertIn("11:02", doc("26.06", "check-answers.md"))

    def test_2606_sources_and_permissions_are_scoped(self):
        self.assertFalse(CASES["26.06"]["market_visited"])
        guide = doc("26.06")
        self.assertIn("1962", guide)
        self.assertIn("1980", guide)
        self.assertIn("These are complete ordinary phrases", guide)
        self.assertIn("people and private notes require separate consent", guide)
        self.assertIn("cannot speak for former ferry workers", doc("26.06", "later-packet.md"))

    def test_2607_interpretation_preserves_distinct_voices(self):
        guide = doc("26.07")
        self.assertIn("Mira, one long-standing participant", guide)
        self.assertIn("Dev, a newer participant", guide)
        self.assertIn("observed, attributed meaning, my interpretation and unknown", guide)
        self.assertIn("represents no ethnicity, nation or religion", guide)
        self.assertIn("missed repair", doc("26.07", "later-packet.md"))

    def test_2607_proposal_and_permission_not_promoted(self):
        f = CASES["26.07"]
        self.assertFalse(f["overflow_agreed"])
        self.assertFalse(f["verse_reuse"])
        self.assertFalse(f["dev_repair_completed"])
        later = doc("26.07", "later-packet.md")
        self.assertIn("neither has yet agreed", later)
        self.assertIn("Nobody grants access", later)
        self.assertIn("no actual community response", later)

    def test_2608_actual_help_replaces_dwell_minutes(self):
        f = CASES["26.08"]
        planned = sum(f["travel"]) + f["planned_reading"]
        actual = sum(f["travel"]) + f["clarification"] + f["actual_reading"]
        self.assertEqual(planned, 17)
        self.assertEqual(actual, planned)
        self.assertEqual([int(row[1]) for row in table("26.08")], [3, 4, 2])
        self.assertEqual(minute(f["start"]) + actual, minute(f["actual_arrivals"][-1]))
        for t in f["actual_arrivals"]:
            self.assertIn(t, doc("26.08", "later-packet.md"))

    def test_2608_support_and_access_not_erased(self):
        f = CASES["26.08"]
        self.assertTrue(f["staff_help"])
        self.assertFalse(f["entered_workroom"])
        self.assertIn("staff-only", doc("26.08").lower())
        self.assertIn("staff help", doc("26.08", "later-packet.md"))
        self.assertIn("universal and solo claims", doc("26.08", "check-answers.md"))

    def test_2609_signal_model_and_fresh_math(self):
        f = CASES["26.09"]
        self.assertEqual([f["arrival_year"] - t for t in f["travel_years"]], f["emission_years"])
        self.assertEqual([30 - t for t in (3, 8)], [27, 22])
        self.assertIn("Years 27 and 22", doc("26.09", "check-answers.md"))
        self.assertIn("fixed shared clock", doc("26.09"))
        self.assertIn("18 for A and 15 for B", doc("26.09", "later-packet.md"))

    def test_2609_neutral_response_and_unknown_present(self):
        f = CASES["26.09"]
        self.assertIsNone(f["current_source_states"])
        self.assertEqual(f["light_year_kind"], "distance")
        self.assertIn("no strong emotion", doc("26.09", "later-packet.md"))
        self.assertIn("no direct solar observation", doc("26.09"))
        self.assertIn("cannot prove humility", doc("26.09"))

    def test_2610_celebration_includes_host_burden(self):
        f = CASES["26.10"]
        self.assertEqual(sum(f["sequence"]), 15)
        self.assertEqual(sum(f["sequence"]) + f["setup"] + f["cleanup"], f["host_limit"])
        self.assertEqual(minute(f["actual_end"]) - minute(f["actual_start"]), f["host_limit"])
        self.assertEqual(f["budget"], 0)
        for t in (f["actual_start"], f["actual_end"]):
            self.assertIn(t, doc("26.10", "later-packet.md"))

    def test_2610_private_memory_and_unknown_enjoyment(self):
        f = CASES["26.10"]
        self.assertIsNone(f["deni_enjoyment"])
        self.assertFalse(f["public_post_permission"])
        self.assertIn("Deni offers no feedback", doc("26.10", "later-packet.md"))
        self.assertIn("None consents to public names or photographs", doc("26.10"))
        self.assertIn("five-minute game felt long", doc("26.10", "later-packet.md"))

    def test_2611_turn_mechanism_changes_available_modes(self):
        f = CASES["26.11"]
        for key in ("typed_received_during_round", "drawing_described"):
            self.assertFalse(f["round1"][key])
            self.assertTrue(f["round2"][key])
        self.assertIn("arrives after the round closes", doc("26.11", "later-packet.md"))
        self.assertIn("collect one response or pass", doc("26.11", "later-packet.md"))
        self.assertIn("No one has yet checked", doc("26.11"))

    def test_2611_pass_and_unknown_enjoyment_preserved(self):
        f = CASES["26.11"]
        self.assertTrue(f["round1"]["cora_pass"] and f["round2"]["cora_pass"])
        self.assertIsNone(f["cora_enjoyment"])
        self.assertIsNone(f["dani_enjoyment"])
        self.assertIn("no fixed response deadline", doc("26.11"))
        self.assertIn("not a controlled experiment", doc("26.11", "later-packet.md"))

    def test_2612_journey_wait_and_later_response(self):
        f = CASES["26.12"]
        self.assertEqual(sum(f["travel"]) + f["reflection"], f["planned_minutes"])
        self.assertEqual(
            minute(f["start"]) + f["planned_minutes"] + f["wait"], minute(f["actual_return"])
        )
        self.assertGreater(minute(f["booklet_receipt"]), minute(f["actual_return"]))
        self.assertIn("four more than the 28-minute plan", doc("26.12", "later-packet.md"))

    def test_2612_unknown_burden_and_harmless_restraint(self):
        f = CASES["26.12"]
        self.assertIsNone(f["second_trip_added_minutes"])
        self.assertFalse(f["public_photo"])
        self.assertIn("must not be called zero", doc("26.12", "later-packet.md"))
        self.assertIn("does not include withholding water, food, medication", doc("26.12"))
        self.assertIn("1974", doc("26.12"))
        self.assertIn("2008", doc("26.12"))

    def test_2613_correction_delivery_before_deadline(self):
        f = CASES["26.13"]
        times = [
            minute(f[k]) for k in ("correction_started", "checked", "sent", "delivered", "deadline")
        ]
        self.assertEqual(times, sorted(times))
        later = doc("26.13", "later-packet.md")
        for key in (
            "correction_started",
            "checked",
            "sent",
            "delivered",
            "wrong_time",
            "correct_time",
        ):
            self.assertIn(f[key], later)
        self.assertEqual(f["selected_line"], "A")

    def test_2613_no_forced_amusement_or_read_receipt(self):
        f = CASES["26.13"]
        self.assertTrue(f["stopped"])
        self.assertFalse(f["laughter"])
        self.assertIsNone(f["read_receipt"])
        self.assertIn(f["reaction"], doc("26.13", "later-packet.md"))
        self.assertIn("no recipient read receipt", doc("26.13", "later-packet.md"))
        self.assertIn("No one owes amusement", doc("26.13"))

    def test_2614_visible_minutes_and_accepted_null(self):
        f = CASES["26.14"]
        for r in f["records"]:
            self.assertEqual(r["visible"] + r["blocked"], f["required_minutes"])
            self.assertEqual(r["accepted"], r["visible"] == f["required_minutes"])
        self.assertEqual(sum(r["accepted"] for r in f["records"]), 1)
        self.assertEqual(f["records"][0]["obstruction"], "none visible")
        self.assertEqual(f["records"][1]["obstruction"], "unknown")
        self.assertIn("09:04", doc("26.14", "later-packet.md"))
        self.assertIn("Four visible minutes plus six blocked", doc("26.14", "later-packet.md"))

    def test_2614_authority_and_future_not_inferred(self):
        f = CASES["26.14"]
        self.assertFalse(f["future_confirmed"])
        self.assertIsNone(f["ecosystem_change"])
        self.assertIn("No entry to the planted area", doc("26.14"))
        self.assertIn("no confirmation or observation", doc("26.14", "later-packet.md"))
        self.assertIn("Plant removal is unauthorized", doc("26.14", "check-answers.md"))

    def test_2701_windows_planned_and_actual_actions(self):
        f = CASES["27.01"]
        self.assertEqual([int(r[1]) for r in table("27.01")], f["windows"])
        self.assertEqual([int(r[3]) for r in table("27.01")], f["planned"])
        self.assertTrue(all(a <= b for a, b in zip(f["planned"], f["windows"], strict=True)))
        self.assertEqual(sum(f["planned"]), 35)
        self.assertEqual(sum(f["actual"]), 27)
        self.assertEqual(sum(f["planned"]) - sum(f["actual"]), 8)
        self.assertIn("27 minutes, compared with 35 planned", doc("27.01", "later-packet.md"))

    def test_2701_six_areas_and_pending_relationship(self):
        f = CASES["27.01"]
        self.assertEqual(f["tokens_spent"], 0)
        self.assertFalse(f["shared_rearrangement_agreed"])
        self.assertFalse(f["meeting_performed"])
        self.assertIsNone(f["friend_reply"])
        self.assertIn(
            "calendar, environment, resources, relationships, roles and recurring practice",
            doc("27.01"),
        )
        self.assertIn("Necessary care is not removed", doc("27.01", "later-packet.md"))

    def test_2702_live_options_and_reduced_capacity(self):
        f = CASES["27.02"]
        self.assertEqual([int(r[1]) for r in table("27.02")], list(f["options"].values()))
        self.assertEqual(f["options"]["F"] + 90, f["window_minutes"])
        self.assertGreater(f["options"]["F"] + f["options"]["G"], f["window_minutes"])
        reduced = f["window_minutes"] - f["new_care_minutes"]
        self.assertEqual(reduced, 135)
        self.assertEqual([k for k, v in f["options"].items() if v <= reduced], ["F", "G"])
        self.assertIn("135 minutes remain", doc("27.02", "check-answers.md"))

    def test_2702_eight_goods_and_cancellation_review(self):
        f = CASES["27.02"]
        self.assertIn(
            "work, family, health, service, rest, growth, pleasure and security", doc("27.02")
        )
        self.assertLess(minute(f["cancelled"]), minute(f["acknowledged"]))
        for k in ("new_visit_agreed", "lesson_performed", "service_performed"):
            self.assertFalse(f[k])
        self.assertIn("part of the quiet time dull", doc("27.02", "later-packet.md"))
        self.assertIn("considered but not scheduled", doc("27.02", "later-packet.md"))


class FreshCaseRegressionTests(unittest.TestCase):
    def test_outing_fresh_return(self):
        self.assertEqual(minute("10:10") + 7 + 4 + 7, minute("10:28"))
        self.assertIn("10:28", doc("26.05", "check-answers.md"))
        self.assertEqual(minute("09:18") + 6, minute("09:24"))

    def test_challenge_fresh_overrun(self):
        self.assertEqual(5 + 5 + 4 - 12, 2)
        self.assertIn("14 minutes, two too many", doc("26.08", "check-answers.md"))

    def test_celebration_fresh_full_burden(self):
        self.assertEqual(4 + 13 + 3 - 18, 2)
        self.assertIn("20 minutes exceeds the limit by two", doc("26.10", "check-answers.md"))

    def test_clock_parser_rejects_malformed_inputs(self):
        for value in (None, True, 900, "9:00", "24:00", "09:60", "-1:00"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                minute(value)


if __name__ == "__main__":
    unittest.main()
