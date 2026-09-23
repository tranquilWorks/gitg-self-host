"""Verify original source cases; these helpers are not runtime/clinical evaluators."""

import copy
import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/adaptive-digital"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = ["12.15", "12.16", "14.01", "14.02", "14.03", "14.04"]


def document(competency, name="learner-guide.md"):
    return (SOURCE / competency / name).read_text()


def table_rows(competency, name="learner-guide.md"):
    return [
        [cell.strip() for cell in line.strip("|").split("|")]
        for line in document(competency, name).splitlines()
        if line.startswith("|") and "---" not in line
    ]


def minutes(value):
    if type(value) is not int or value < 0:
        raise ValueError("Case duration must be a known nonnegative integer")
    return value


def session_summary(records):
    """Summarize supplied events without turning absent observations into success."""
    durations = []
    met = 0
    for item in records:
        if type(item["occurred"]) is not bool:
            raise ValueError("Occurrence is unknown")
        if not item["occurred"]:
            if item["minutes"] is not None or item["purpose_met"] is not None:
                raise ValueError("An absent event cannot supply performed results")
            continue
        durations.append(minutes(item["minutes"]))
        if type(item["purpose_met"]) is not bool:
            raise ValueError("Purpose result is unknown")
        met += item["purpose_met"]
    return {
        "sessions": len(durations),
        "purpose_met": met,
        "total": sum(durations),
        "mean": sum(durations) / len(durations) if durations else None,
    }


def reachable(rules, confirmed):
    """Solve the fictional account's explicit AND/OR dependencies to a fixed point."""
    if not isinstance(confirmed, list) or any(type(x) is not str for x in confirmed):
        raise ValueError("Only explicitly confirmed resource names are seeds")
    for target, alternatives in rules.items():
        if type(target) is not str or not alternatives:
            raise ValueError("Invalid target or absent alternatives")
        for requirements in alternatives:
            if not isinstance(requirements, list) or not requirements:
                raise ValueError("A route must have prerequisites")
            if any(type(x) is not str or not x for x in requirements):
                raise ValueError("Missing prerequisite is not available")
    known = set(confirmed)
    while True:
        additions = {
            target
            for target, alternatives in rules.items()
            if any(set(required) <= known for required in alternatives)
        }
        updated = known | additions
        if updated == known:
            return known
        known = updated


class CorpusIntegrityTests(unittest.TestCase):
    def test_exact_identity_and_runtime_boundary(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(COHORT["formal_reviews_accepted"], 0)
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )
        self.assertEqual(COHORT["additional_companions_after"], 45)
        self.assertTrue(FIX["synthetic"])
        self.assertFalse(FIX["runtime_evidence"])

    def test_complete_canonical_entries_and_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        expected = [
            entry
            for domain in catalog["curriculum"]["domains"]
            for entry in domain["competencies"]
            if entry["id"] in IDS
        ]
        self.assertEqual(COHORT["entries"], expected)
        for name, digest in COHORT["input_sha256"].items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)

    def test_sequence_closes_health_skips_completed_domestic(self):
        implemented = yaml.safe_load(
            (ROOT / "contracts/tailored-practice-authoring.yaml").read_text()
        )["implemented_competency_ids"]
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        domestic = next(d for d in catalog["curriculum"]["domains"] if d["id"] == "13")
        self.assertTrue({e["id"] for e in domestic["competencies"]} <= set(implemented))
        last = json.loads((ROOT / "docs/authoring/health-stewardship/cohort.json").read_text())
        self.assertEqual(last["ids"][-1], "12.14")
        self.assertFalse(set(IDS) & set(implemented))

    def test_materials_links_and_separate_checks_resolve(self):
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
                self.assertEqual(
                    re.findall(r"^(\d)\. ", document(cid, name), re.M), ["1", "2", "3"]
                )
        for path in SOURCE.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target:
                    self.assertTrue(
                        (path.parent / target.split("#")[0]).resolve().is_file(), str(path)
                    )

    def test_scope_maps_preserve_each_canonical_claim(self):
        for entry in COHORT["entries"]:
            scope = document(entry["id"], "SCOPE-MAP.md")
            for key in ("name", "scope", "evidence_of_progress"):
                self.assertIn(entry[key], scope)
            self.assertIn(entry["measurement"]["minimum_standard"], scope)
            self.assertIn("not a formal M6K A/B/C receipt", scope)

    def test_active_contract_is_narrow_when_current(self):
        contract = yaml.safe_load((ROOT / "contracts/active-batch.yaml").read_text())
        self.assertTrue(all(isinstance(x, str) for x in contract["acceptance"]))
        if contract["batch"]["id"] == "M6K-ADAPTIVE-DIGITAL-SIX":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                "growth/**",
                ".github/**",
                "docs/authoring/health-stewardship/**",
            ):
                self.assertIn(path, contract["scope"]["forbidden_paths"])


class AdaptiveAndPainCaseTests(unittest.TestCase):
    def test_full_schedule_and_harder_shortfall(self):
        case = FIX["adaptive"]
        total = sum(map(minutes, case["default_minutes"]))
        self.assertEqual(total, 15)
        self.assertEqual(case["available_minutes"] - total, 5)
        self.assertEqual(total - case["harder_available_minutes"], 2)
        guide = document("12.15")
        for item in ("Four minutes setup", "three minutes closing", "09:00", "09:20", "09:07"):
            self.assertIn(item, guide)

    def test_fresh_schedule_does_not_silently_shorten_rest(self):
        case = FIX["adaptive"]
        self.assertEqual(sum(case["fresh_minutes"]), 18)
        self.assertEqual(sum(case["fresh_minutes"]) - case["fresh_available_minutes"], 1)
        self.assertIn("18 minutes", document("12.15", "check-answers.md"))

    def test_later_bouts_preserve_deferral_and_unknown_followup(self):
        events = FIX["adaptive"]["events"]
        self.assertEqual(sum(x["bouts"] for x in events), 3)
        self.assertEqual(sum(x["bouts"] * x["minutes_each"] for x in events), 9)
        self.assertEqual(events[1]["status"], "deferred")
        self.assertEqual(events[1]["bouts"], 0)
        self.assertIsNone(events[2]["next_morning"])
        later = document("12.15", "later-packet.md")
        self.assertIn("Zero bouts", later)
        self.assertIn("response and next-morning function not yet recorded", later)

    def test_invalid_duration_does_not_become_success(self):
        for value in (True, -1, None, 1.5, "3"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                minutes(value)

    def test_pain_facts_are_not_diagnoses_or_completed_care(self):
        for case in ("A", "B", "C2"):
            self.assertIsNone(FIX["pain"][case]["diagnosis"])
        self.assertEqual(FIX["pain"]["B"]["assessment"], "not_recorded")
        self.assertEqual(FIX["pain"]["C2"]["contact"], "not_recorded")
        later = document("12.16", "later-packet.md")
        self.assertIn("no attended assessment", later)
        self.assertIn("emergency help rather than a routine-message wait", later)

    def test_chronic_plan_does_not_clear_new_emergency_features(self):
        self.assertEqual(FIX["pain"]["C2"]["required_route"], "emergency")
        later = document("12.16", "later-packet.md")
        self.assertIn("new bladder-control difficulty", later)
        self.assertIn("loss of feeling around the genital area", later)
        self.assertIn("no emergency contact or assessment", later)
        self.assertIsNone(FIX["pain"]["C1"]["next_day"])


class MediaCaseTests(unittest.TestCase):
    def test_only_option_b_preserves_all_explicit_requirements(self):
        fits = [
            name
            for name, values in FIX["media"]["options"].items()
            if all(value is True for value in values.values())
        ]
        self.assertEqual(fits, ["B"])
        rows = {r[0]: r for r in table_rows("14.01") if r[0] in "ABC"}
        self.assertIn("Pickup messages stop", rows["A"][2])
        self.assertIn("retain direct-message alerts", rows["B"][1])
        self.assertIn("Control of access", rows["C"][2])

    def test_default_sessions_exclude_absent_opportunity(self):
        self.assertEqual(
            session_summary(FIX["media"]["sessions"]),
            {
                "sessions": 2,
                "purpose_met": 1,
                "total": 18,
                "mean": 9,
            },
        )
        later = document("14.01", "later-packet.md")
        for time in ("18:00", "18:04", "18:03", "18:14"):
            self.assertIn(time, later)
        self.assertEqual(14 - 3, 11)
        self.assertEqual(14 - 5, 9)

    def test_fresh_case_arithmetic(self):
        self.assertEqual(
            session_summary(FIX["media"]["fresh_sessions"]),
            {
                "sessions": 2,
                "purpose_met": 1,
                "total": 19,
                "mean": 9.5,
            },
        )

    def test_absent_event_cannot_be_zero_minute_success(self):
        records = copy.deepcopy(FIX["media"]["sessions"])
        records[-1].update(minutes=0, purpose_met=True)
        with self.assertRaises(ValueError):
            session_summary(records)

    def test_missing_occurrence_and_outcome_fail_closed(self):
        for field in ("occurred", "purpose_met"):
            record = {"occurred": True, "minutes": 4, "purpose_met": True, field: None}
            with self.subTest(field=field), self.assertRaises(ValueError):
                session_summary([record])

    def test_no_observations_is_unknown_mean(self):
        self.assertIsNone(session_summary([FIX["media"]["sessions"][-1]])["mean"])


class FileRecoveryTests(unittest.TestCase):
    def test_actual_supplied_file_copy_then_retrieval_preserves_original(self):
        source = SOURCE / "14.02/materials/meeting-v2.txt"
        original_bytes = source.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("original", "copy", "restore-check"):
                (root / name).mkdir()
            original = root / "original/meeting-v2.txt"
            backup = root / "copy/meeting-v2.txt"
            restored = root / "restore-check/meeting-v2.txt"
            shutil.copyfile(source, original)
            shutil.copyfile(original, backup)
            shutil.copyfile(backup, restored)
            self.assertEqual(restored.read_bytes(), original_bytes)
            self.assertEqual(original.read_bytes(), original_bytes)
            self.assertEqual(restored.read_text().splitlines(), FIX["recovery"]["required"])
        self.assertEqual(source.read_bytes(), original_bytes)

    def test_material_versions_match_guide_and_differ_at_room_only(self):
        first = (SOURCE / "14.02/materials/meeting-v1.txt").read_text().splitlines()
        second = (SOURCE / "14.02/materials/meeting-v2.txt").read_text().splitlines()
        self.assertEqual(first, FIX["recovery"]["branches"]["R2"])
        self.assertEqual(second, FIX["recovery"]["required"])
        self.assertEqual([a != b for a, b in zip(first, second, strict=True)], [False, True, False])
        rows = {r[0]: r for r in table_rows("14.02")}
        self.assertEqual(rows["meeting-v2.txt"][2].split("; "), second)

    def test_success_stale_missing_and_truncated_outputs(self):
        results = {
            key: value == FIX["recovery"]["required"]
            for key, value in FIX["recovery"]["branches"].items()
        }
        self.assertEqual(results, {"R1": True, "R2": False, "R3": False, "R4": False})
        rows = {r[0]: r for r in table_rows("14.02", "later-packet.md")}
        for name in ("R1", "R2", "R4"):
            self.assertEqual(rows[name][2].split("; "), FIX["recovery"]["branches"][name])
        self.assertEqual(rows["R3"][2], "No file created")

    def test_same_filename_does_not_make_wrong_content_valid(self):
        wanted = ["Workshop", "Blue door", "Bring gloves"]
        obtained = ["Workshop", "Blue door", "Bring goggles"]
        self.assertEqual(wanted[:2], obtained[:2])
        self.assertNotEqual(wanted, obtained)
        self.assertIn("Retyping", document("14.02", "check-answers.md"))

    def test_sync_loss_leaves_only_older_independent_state(self):
        backup = (SOURCE / "14.02/materials/meeting-v1.txt").read_bytes()
        current = (SOURCE / "14.02/materials/meeting-v2.txt").read_bytes()
        local, synced = None, None  # Synthetic deletion, never a filesystem deletion.
        self.assertIsNone(local)
        self.assertIsNone(synced)
        self.assertNotEqual(backup, current)
        self.assertIn("no retained history", document("14.02", "later-packet.md"))


class PrivacyCaseTests(unittest.TestCase):
    def test_future_discovery_and_existing_records_have_distinct_status(self):
        self.assertIs(FIX["privacy"]["future_contact_discovery"], False)
        self.assertEqual(FIX["privacy"]["stored_contacts"], "acknowledged")
        later = document("14.03", "later-packet.md")
        self.assertIn("deletion not yet confirmed", later)
        self.assertIn("future matching disabled", later)

    def test_provider_reply_changes_only_its_stated_scope(self):
        before = FIX["privacy"]
        after = copy.deepcopy(before)
        for field in before["alternative_reply_scope"]:
            after[field] = "provider_confirmed_deleted"
        self.assertEqual([key for key in before if before[key] != after[key]], ["stored_contacts"])
        self.assertEqual(after["security_logs"], "retained")
        self.assertIsNone(after["recipient_copy"])

    def test_complete_policy_records_are_separately_addressed(self):
        labels = [r[0] for r in table_rows("14.03") if re.match(r"P[1-6] —", r[0])]
        self.assertEqual([x[:2] for x in labels], [f"P{i}" for i in range(1, 7)])
        self.assertIn("no processing deadline", document("14.03"))
        self.assertIn("another app", document("14.03", "check-prompts.md"))


class SecurityDependencyTests(unittest.TestCase):
    def test_initial_phone_loss_has_no_complete_route(self):
        case = FIX["security"]
        known = reachable(case["rules"], case["initial_confirmed"])
        self.assertIn("account_password", known)
        self.assertNotIn("account", known)
        self.assertNotIn("in_account_code", known)

    def test_independent_unused_code_completes_phone_loss_route(self):
        case = FIX["security"]
        self.assertIn("account", reachable(case["rules"], case["after_confirmed"]))
        self.assertNotIn("phone_code", case["after_confirmed"])

    def test_each_required_seed_really_is_required(self):
        case = FIX["security"]
        for seed in case["after_confirmed"]:
            confirmed = [x for x in case["after_confirmed"] if x != seed]
            with self.subTest(missing=seed):
                self.assertNotIn("account", reachable(case["rules"], confirmed))

    def test_circular_vault_with_paper_code_still_fails(self):
        self.assertNotIn(
            "account", reachable(FIX["security"]["circular_rules"], ["paper_unused_code"])
        )

    def test_consumed_code_is_not_unused_material(self):
        case = FIX["security"]
        confirmed = case["initial_confirmed"] + ["paper_consumed_code"]
        self.assertNotIn("account", reachable(case["rules"], confirmed))
        self.assertEqual(case["test_code_status"], "consumed")
        self.assertIn("different unused code", document("14.04", "later-packet.md"))

    def test_unknown_resources_and_empty_routes_rejected(self):
        for rules, seeds in (({"account": [[]]}, []), ({"account": [[None]]}, []), ({}, [True])):
            with self.subTest(rules=rules, seeds=seeds), self.assertRaises(ValueError):
                reachable(rules, seeds)

    def test_successful_signin_cannot_resolve_encryption_key(self):
        case = FIX["security"]
        known = reachable(case["rules"], case["after_confirmed"])
        self.assertIn("account", known)
        self.assertNotIn("encryption_key", known)
        self.assertIsNone(case["encryption_key_verified"])
        self.assertIn("Location still unverified", document("14.04", "later-packet.md"))

    def test_loss_case_excludes_working_session_as_a_shortcut(self):
        guide = document("14.04")
        self.assertIn("phone and every existing Postbox session are unavailable", guide)
        self.assertIn("retained working session", guide)
        self.assertIn("unexpected prompt", document("14.04", "check-answers.md"))


if __name__ == "__main__":
    unittest.main()
