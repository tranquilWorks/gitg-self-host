"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/creative-culture-leisure"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"25.{i:02}" for i in range(6, 14)] + [f"26.{i:02}" for i in range(1, 5)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 213)
        self.assertEqual(COHORT["additional_companions_after"], 225)
        self.assertEqual(COHORT["reporting_cadence"], 12)
        self.assertTrue(COHORT["source_only"])
        self.assertEqual(
            [COHORT[k] for k in ("runtime_tailored", "runtime_pending", "protocols", "actions")],
            [108, 275, 383, 1151],
        )

    def test_exact_canonical_entries_and_seven_input_hashes(self):
        catalog = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        entries = [
            e for d in catalog["curriculum"]["domains"] for e in d["competencies"] if e["id"] in IDS
        ]
        self.assertEqual(entries, COHORT["entries"])
        self.assertEqual(len(COHORT["input_sha256"]), 7)
        for path, digest in COHORT["input_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_selected_current_recovery_entries_match(self):
        for domain in ("25", "26"):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            self.assertEqual(current, recovery)
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_source_only_legacy_companion(self):
        previous = json.loads((ROOT / "docs/authoring/economics-creative/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "25.05")
        self.assertEqual(previous["additional_companions_after"], 213)
        contract = yaml.safe_load((ROOT / "contracts/tailored-practice-authoring.yaml").read_text())
        self.assertFalse(set(IDS) & set(contract["implemented_competency_ids"]))
        self.assertEqual(set(IDS) & set(contract["retained_legacy_competency_ids"]), {"26.01"})
        self.assertEqual(COHORT["legacy_companion_ids"], ["26.01"])

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

    def test_mixed_classifications_and_absent_professional_boundaries(self):
        for e in COHORT["entries"]:
            expected = (
                ("elective_cultivation", "elective_but_flourishing_relevant")
                if e["id"].startswith("25.")
                else ("cross_context_core", "cross_tradition_core_or_broadly_recurrent")
            )
            self.assertEqual(
                (e["classification"]["applicability"], e["classification"]["normative_status"]),
                expected,
            )
            self.assertNotIn("professional_boundary", e)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn("no professional_boundary field", doc(e["id"], name))
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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 13)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-25")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        by_id = {source["id"]: source for source in sources}
        self.assertIn("linked Novakovich extract was not opened", by_id["S04"]["limits"])
        self.assertIn("Image and audio not inspected", by_id["S05"]["limits"])
        self.assertIn("Written transcript read", by_id["S06"]["limits"])
        self.assertIn("No label, icon or template applied", by_id["S09"]["limits"])
        self.assertIn("Later find requests returned a browser-check page", by_id["S11"]["limits"])
        self.assertIn("stale 2021 volunteer invitation", by_id["S12"]["limits"])

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
        if contract["batch"]["id"] == "M6K-CREATIVE-CULTURE-LEISURE-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/economics-creative/**",
                "tests/test_m6k_economics_creative_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 213))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 333, 50))
        self.assertEqual(coverage["remaining_count"], len(remaining))
        self.assertEqual(coverage["remaining_before"], len(remaining) + len(IDS))
        self.assertEqual(coverage["additional_after"], len(prior) + len(IDS))
        self.assertEqual(coverage["covered_unique_count"], len(covered))
        self.assertEqual(coverage["remaining_by_domain"], dict(Counter(x[:2] for x in remaining)))
        earlier = sorted(x for x in remaining if x[:2] in {"07", "08"})
        self.assertEqual(coverage["earlier_domains_07_08_remaining"], earlier)
        self.assertEqual(len(earlier), 25)
        legacy_pending = set(contract["retained_legacy_competency_ids"]) - prior - set(IDS)
        self.assertEqual(legacy_pending, {"08.02"})
        self.assertEqual(set(coverage["legacy_without_new_companion"]), legacy_pending)
        self.assertTrue(legacy_pending <= remaining)


def quote_blocks(cid, name="learner-guide.md"):
    blocks = re.findall(r"(?m)(?:^>.*(?:\n|$))+", doc(cid, name))
    return [
        [line.removeprefix("> ").removesuffix("\\").strip() for line in block.splitlines()]
        for block in blocks
    ]


class CaseTests(unittest.TestCase):
    def test_experiment_versions_and_one_sentence_retry(self):
        blocks = quote_blocks("25.06")
        self.assertEqual([len(b) for b in blocks], [6, 6, 6])
        retry = quote_blocks("25.06", "later-packet.md")[0]
        self.assertEqual(len(retry), 6)
        changed = [i + 1 for i, (a, b) in enumerate(zip(blocks[0], retry, strict=True)) if a != b]
        self.assertEqual(changed, [FIX["experiments"]["changed_sentence"]])
        self.assertIn("the cyclist", retry[4])
        self.assertTrue(all(line.startswith("“") and line.endswith("”") for line in blocks[1]))

    def test_experiment_reference_repair_does_not_settle_curiosity(self):
        self.assertFalse(FIX["experiments"]["curiosity_established"])
        self.assertIn("timeline rather than a surprising story", doc("25.06", "later-packet.md"))
        self.assertIn("not another person's response", doc("25.06"))
        self.assertIn("A decline ends the request", doc("25.06"))

    def test_revision_passes_preserve_complete_versions_and_exact_tense_fix(self):
        blocks = quote_blocks("25.07")
        self.assertEqual([len(b) for b in blocks], [6, 6, 6])
        self.assertNotEqual(blocks[0][1], blocks[1][1])
        self.assertIn("room seem warmer", blocks[1][4])
        self.assertEqual(blocks[2][4], blocks[1][4].replace("seem", "seemed"))
        self.assertEqual(
            [i + 1 for i, (a, b) in enumerate(zip(blocks[1], blocks[2], strict=True)) if a != b],
            [5],
        )
        self.assertEqual(FIX["release"]["released"], "V2")

    def test_release_nonresponse_and_unshared_revision_remain_distinct(self):
        f = FIX["release"]
        self.assertFalse(f["initial_response"] or f["optional_released"])
        self.assertEqual(f["later_response"], "mixed")
        self.assertIn(
            "intended emotional relief remains uncertain", doc("25.07", "later-packet.md")
        )
        self.assertIn("has not been sent", doc("25.07", "later-packet.md"))
        self.assertIn("reader has not replied", doc("25.07"))

    def test_collaboration_preserves_facts_and_changes_meaning_and_ending(self):
        first, final = quote_blocks("25.08")
        self.assertEqual((len(first), len(final)), (6, 6))
        self.assertEqual(
            [i + 1 for i, (a, b) in enumerate(zip(first, final, strict=True)) if a != b], [4, 6]
        )
        self.assertIn("quiet stories", first[3])
        self.assertIn("quiet company", final[3])
        self.assertIn("will not ask you to make a speech", final[5])
        self.assertIn("final ending selected and rewritten together", doc("25.08"))

    def test_collaboration_repairs_unagreed_edit_without_inventing_public_consent(self):
        self.assertFalse(FIX["collaboration"]["public_consent"])
        self.assertIn("felt rushed", doc("25.08"))
        self.assertIn("No post is made", doc("25.08", "later-packet.md"))
        self.assertIn("public use pending", doc("25.08", "later-packet.md"))
        self.assertIn("not as consent obtained through silence", doc("25.08", "later-packet.md"))

    def test_scene_and_exact_replacement_stay_within_preserved_word_limit(self):
        scene = " ".join(line for block in quote_blocks("25.09") for line in block if line)
        replacement = " ".join(quote_blocks("25.09", "later-packet.md")[0])
        original = "Tess looked away toward the street. “Neither do I.”"
        self.assertIn(original, scene)
        revised = scene.replace(original, replacement)
        self.assertNotEqual(scene, revised)
        self.assertLessEqual(len(scene.split()), 300)
        self.assertLessEqual(len(revised.split()), 300)
        self.assertIn("Nadia had tested three shades of green", scene)
        self.assertIn("steadied the sign", revised)

    def test_scene_preserves_both_concerns_and_unresolved_reception(self):
        f = FIX["imagination"]
        self.assertFalse(f["revised_reader_response"] or f["accessible_room_confirmed"])
        self.assertIn("Plain explanation for comparison", doc("25.09"))
        self.assertIn("care for memory and care for access", doc("25.09"))
        self.assertIn("There is no second reader response", doc("25.09", "later-packet.md"))
        self.assertIn("not a validated empathy outcome", doc("25.09", "later-packet.md"))

    def test_catalogue_identifiers_media_and_access_routes_are_not_conflated(self):
        f = FIX["literacy"]
        guide = doc("25.10")
        for key in ("wave", "cypresses"):
            self.assertNotEqual(f[key]["url_id"], f[key]["accession"])
            self.assertIn(f[key]["url_id"], guide)
            self.assertIn(f[key]["accession"], guide)
        self.assertFalse(f["image_inspected"] or f["audio_played"])
        self.assertIn("text-mediated detail record", guide)
        self.assertIn("without playing audio", guide)
        self.assertIn("woodblock print", guide)
        self.assertIn("oil painting on canvas", guide)

    def test_cultural_comparison_retracts_unsupported_influence_and_origin_claims(self):
        self.assertFalse(FIX["literacy"]["direct_influence_established"])
        for phrase in (
            "Original appreciation A",
            "Original appreciation B",
            "original purchasers",
            "excluded from collection",
            "next proposed study",
        ):
            self.assertIn(phrase, doc("25.10"))
        self.assertIn("removes a national stereotype", doc("25.10", "later-packet.md"))
        self.assertIn("not established by the inspected sources", doc("25.10", "later-packet.md"))

    def test_environment_two_uses_expose_conflict_before_revision(self):
        f = FIX["environment"]
        guide = doc("25.11")
        self.assertEqual(f["uses"], 2)
        self.assertIn("**Use check 1:**", guide)
        self.assertIn("**Use check 2:**", guide)
        self.assertIn("back right", guide)
        self.assertIn("near left", doc("25.11", "later-packet.md"))
        self.assertIn("keepsake", guide)
        self.assertIn("visual imbalance is an accepted tradeoff", doc("25.11", "later-packet.md"))

    def test_environment_rearrangement_is_not_a_third_use_or_access_certification(self):
        f = FIX["environment"]
        self.assertTrue(f["revised"])
        self.assertFalse(f["revised_tested"] or f["shared_belongings_moved"])
        self.assertIn("There is no third use", doc("25.11", "later-packet.md"))
        self.assertIn(
            "comfort and legibility after the change remain unconfirmed",
            doc("25.11", "later-packet.md"),
        )
        self.assertIn("certifies neither universal access nor legal compliance", doc("25.11"))

    def test_fan_geometry_sequence_and_component_only_correction_reconcile(self):
        f = FIX["craft"]
        self.assertEqual(f["panels"] - 1, f["creases"])
        self.assertEqual(len(f["sequence"]), f["creases"])
        self.assertTrue(
            all(a != b for a, b in zip(f["sequence"][:-1], f["sequence"][1:], strict=True))
        )
        self.assertEqual(f["sequence"][f["attempt_one_wrong_crease"] - 1], "M")
        self.assertEqual((f["full_attempts"], f["component_repeats"]), (2, 2))
        self.assertFalse(f["third_full_attempt"])
        self.assertIn("valley, mountain, valley, mountain, valley, mountain, valley", doc("25.12"))
        self.assertIn("There is no third complete fan", doc("25.12"))

    def test_craft_limited_permission_does_not_invent_origin_or_actual_demonstration(self):
        f = FIX["craft"]
        self.assertTrue(f["limited_demo_permitted"])
        self.assertFalse(f["limited_demo_occurred"] or f["public_video_permitted"])
        self.assertIn("Mae is not known to have invented it", doc("25.12"))
        self.assertIn("demonstration has not occurred", doc("25.12", "later-packet.md"))
        self.assertIn("does not approve a video or a club class", doc("25.12", "later-packet.md"))

    def test_cultural_use_cases_distinguish_five_scopes_and_authority(self):
        f = FIX["cultural_use"]
        self.assertEqual(len(f["cases"]) * len(f["uses"]), 15)
        self.assertTrue(f["a"]["private_learning"] and f["a"]["one_unrecorded_demo"])
        self.assertFalse(f["a"]["video"] or f["a"]["sale"] or f["b"]["authority_established"])
        for label in ("View", "Learn privately", "Adapt", "Teach", "Sell"):
            self.assertIn(f"| {label} |", doc("25.13"))
        self.assertIn("Legal rights", doc("25.13"))
        self.assertIn("customary restrictions", doc("25.13"))

    def test_cultural_alternative_removes_material_and_false_endorsement_before_any_sale(self):
        f = FIX["cultural_use"]
        self.assertEqual(
            (f["c"]["planned_cards"], f["c"]["produced"], f["c"]["orders"]), (30, 0, 0)
        )
        self.assertFalse(f["actual_publication"] or f["c"]["endorsement"])
        self.assertIn("No community name will market the alternative", doc("25.13"))
        self.assertIn("silence is not approval", doc("25.13", "later-packet.md"))
        self.assertIn(
            "community name and endorsement language are removed", doc("25.13", "later-packet.md")
        )

    def test_play_windows_fit_reserve_return_and_total_without_output_requirement(self):
        f = FIX["play"]
        self.assertLessEqual(f["first_day"] - f["reserve_day"], 3)
        self.assertLessEqual(f["return_day"] - f["first_day"], 7)
        self.assertLessEqual(f["return_day"], 10)
        self.assertEqual(f["initial_minutes"], 30)
        self.assertEqual(
            sum(
                f[k]
                for k in ("setup_minutes", "initial_minutes", "return_minutes", "review_minutes")
            ),
            55,
        )
        self.assertIn("no word count, polished ending, skill target", doc("26.01"))
        self.assertIn("an ordinary end reminder", doc("26.01"))

    def test_play_mixed_return_and_declined_invitation_add_no_enjoyment_or_runtime_credit(self):
        f = FIX["play"]
        self.assertEqual(f["return_non_instrumental"], "mixed")
        self.assertFalse(f["friend_participated"] or f["app_review_submitted"])
        self.assertIsNone(f["enjoyment_score"])
        self.assertIn("ranking possible punch lines", doc("26.01", "later-packet.md"))
        self.assertIn("declined invitation stays declined", doc("26.01", "later-packet.md"))
        self.assertIn(
            "no action fields or completion credit are populated", doc("26.01", "later-packet.md")
        )

    def test_rest_three_periods_repeat_chosen_condition_and_keep_all_outcomes(self):
        f = FIX["rest"]
        self.assertEqual(len(f["days"]), 3)
        self.assertLessEqual(max(f["days"]) - min(f["days"]), 7)
        self.assertEqual(sum(f["minutes"]) + f["review_minutes"], 70)
        self.assertNotEqual(f["conditions"][0], f["conditions"][1])
        self.assertEqual(f["conditions"][1], f["conditions"][2])
        self.assertEqual(f["outcomes"], ["agitating", "apparently restorative", "neutral"])
        self.assertIn("Three periods occurred", doc("26.02", "later-packet.md"))

    def test_rest_keeps_essential_contact_and_does_not_prove_causation_or_fourth_period(self):
        f = FIX["rest"]
        self.assertTrue(f["urgent_contact_available"])
        self.assertFalse(f["causal_effect_established"] or f["fourth_period_occurred"])
        self.assertIn("urgent-care contact audible", doc("26.02"))
        self.assertIn("not a fourth completed period", doc("26.02", "later-packet.md"))
        self.assertIn(
            "No sleep, fatigue or mental-health diagnosis", doc("26.02", "later-packet.md")
        )

    def test_hobby_four_sessions_and_exact_single_word_repair(self):
        f = FIX["hobby"]
        self.assertEqual(len(f["days"]), 4)
        self.assertLessEqual(max(f["days"]) - min(f["days"]), 14)
        self.assertTrue(all(15 <= x <= 30 for x in f["minutes"]))
        self.assertEqual(sum(f["minutes"]) + f["review_minutes"], 85)
        self.assertEqual(
            [(a, b) for a, b in zip(f["first_words"], f["revised_words"], strict=True) if a != b],
            [("branch", "index")],
        )
        for key in ("first_words", "revised_words", "variation_words"):
            self.assertEqual(len(f[key]), 5)
            self.assertIn(", ".join(f[key]), doc("26.03"))

    def test_hobby_hint_and_private_future_plan_are_not_independent_or_lifelong_evidence(self):
        f = FIX["hobby"]
        self.assertTrue(f["hint_given"])
        self.assertFalse(f["public_group_joined"] or f["future_sessions_occurred"])
        self.assertEqual(f["money_spent"], 0)
        self.assertIn("not solved wholly without a hint", doc("26.03", "later-packet.md"))
        self.assertIn("twenty minutes once a week", doc("26.03", "later-packet.md"))
        self.assertIn(
            "possibility rather than an established result", doc("26.03", "later-packet.md")
        )

    def test_nature_three_visits_preserve_vantage_time_and_absence(self):
        f = FIX["nature"]
        self.assertEqual(len(f["dates"]), 3)
        self.assertEqual(sum(f["minutes"]), 30)
        self.assertTrue(f["same_vantage"])
        self.assertEqual(f["times"][:2], ["08:00", "08:00"])
        self.assertEqual(f["times"][2], "16:00")
        self.assertEqual(f["animal_observed"], [False, True, False])
        self.assertIn("Visit N1", doc("26.04"))
        for label in ("Visit N2", "Visit N3", "three visits span seven days"):
            self.assertIn(label, doc("26.04", "later-packet.md"))

    def test_nature_source_does_not_identify_plant_or_measure_response_benefit(self):
        f = FIX["nature"]
        self.assertIsNone(f["species"])
        self.assertTrue(f["response_occurred"])
        self.assertFalse(f["ecological_benefit_measured"])
        self.assertIn("actually uses the paved route", doc("26.04", "later-packet.md"))
        self.assertIn("courtyard cactus remains unidentified", doc("26.04", "later-packet.md"))
        self.assertIn("no measured ecological improvement", doc("26.04", "later-packet.md"))
        self.assertIn("old volunteer invitation", doc("26.04"))


class FrozenPlayTests(unittest.TestCase):
    def setUp(self):
        self.package = yaml.safe_load((ROOT / COHORT["legacy_snapshot"]["path"]).read_text())

    def test_whole_package_identity_and_exact_snapshot_preserved(self):
        self.assertEqual(self.package, COHORT["legacy_snapshot"]["package"])
        self.assertEqual(self.package["stable_id"], "PRACTICE-PLAY-01")
        self.assertEqual(self.package["protocol_version"], "1.0.0")
        self.assertEqual(
            self.package["governance"]["authoring"]["content_review_status"],
            "frozen_runtime_behavior",
        )
        self.assertEqual(self.package["intervention"]["duration_days"], 10)

    def test_exact_three_action_instructions_due_windows_and_evidence_rules(self):
        actions = self.package["intervention"]["actions"]
        expected = [
            (
                "Choose a specific activity and reserve at least 30 minutes for it "
                "within the next three days.",
                3,
                ["future_interaction_scheduled"],
                ["user_initiated"],
            ),
            (
                "Use the reserved time for the activity. For that window, do not optimize, "
                "publish, measure, or turn it into work.",
                None,
                ["moved_beyond_transactional", "meaningful_information_shared"],
                ["user_initiated"],
            ),
            (
                "Within seven days, return to the activity for another short period "
                "or choose a second playful activity.",
                7,
                ["follow_up_within_seven_days"],
                ["moved_beyond_transactional"],
            ),
        ]
        self.assertEqual(len(actions), 3)
        for i, (action, (instruction, due, primary, supporting)) in enumerate(
            zip(actions, expected, strict=True), 1
        ):
            self.assertEqual(action["stable_id"], f"PRACTICE-PLAY-01-A{i}")
            self.assertEqual(action["sequence"], i)
            self.assertEqual(action["instructions"], instruction)
            self.assertEqual(action["due_within_days"], due)
            self.assertEqual(
                action["evidence_rules"],
                {
                    "schema_version": "practice-observation-v1",
                    "primary_markers": primary,
                    "supporting_markers": supporting,
                },
            )

    def test_available_fields_completion_and_missing_marker_exception_stay_frozen(self):
        evidence = self.package["evidence_and_scoring"]
        completion = self.package["completion_and_review"]
        self.assertEqual(
            evidence["check_in_fields"],
            [
                "future_interaction_scheduled",
                "moved_beyond_transactional",
                "meaningful_information_shared",
                "follow_up_within_seven_days",
                "internal_resistance",
            ],
        )
        self.assertNotIn("user_initiated", evidence["check_in_fields"])
        self.assertEqual(
            self.package["governance"]["legacy_compatibility_exceptions"][0]["exception_id"],
            "LEGACY-PLAY-A1-USER-INITIATED-UNCOLLECTABLE",
        )
        self.assertEqual(
            completion["completion_criteria"],
            [
                "All three actions attempted",
                "At least two actions completed",
                "At least one period of genuinely non-instrumental engagement",
                "Final review submitted",
            ],
        )
        self.assertEqual(
            completion["completion_rules"],
            {
                "minimum_completed": 2,
                "substantive_markers": [
                    "moved_beyond_transactional",
                    "meaningful_information_shared",
                ],
            },
        )
        self.assertIn("enjoyment intensity is not scored", evidence["performance_rubric"])


if __name__ == "__main__":
    unittest.main()
