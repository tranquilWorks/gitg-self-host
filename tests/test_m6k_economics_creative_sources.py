"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from collections import Counter
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/economics-creative"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"24.{i:02}" for i in range(8, 15)] + [f"25.{i:02}" for i in range(1, 6)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 201)
        self.assertEqual(COHORT["additional_companions_after"], 213)
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
        for domain in ("24", "25"):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads(
            (ROOT / "docs/authoring/stewardship-enterprise/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "24.07")
        self.assertEqual(previous["additional_companions_after"], 201)
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

    def test_mixed_classifications_and_exact_professional_boundaries(self):
        boundary = (
            "Business and economic education only; legal, tax, securities, "
            "employment, and regulatory questions require qualified advice."
        )
        for e in COHORT["entries"]:
            if e["id"].startswith("24."):
                self.assertEqual(e["classification"]["applicability"], "role_conditional")
                self.assertEqual(e["classification"]["normative_status"], "role_conditional")
                self.assertEqual(e["professional_boundary"], boundary)
                for name in ("learner-guide.md", "SCOPE-MAP.md"):
                    self.assertIn(boundary, doc(e["id"], name))
            else:
                self.assertEqual(e["classification"]["applicability"], "elective_cultivation")
                self.assertEqual(
                    e["classification"]["normative_status"], "elective_but_flourishing_relevant"
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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 18)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-24")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        by_id = {source["id"]: source for source in sources}
        self.assertIn("Only the opening incidence concept", by_id["S05"]["limits"])
        self.assertIn("deeper employee-ownership tool page returned 403", by_id["S08"]["limits"])
        self.assertIn("Selected passages only", by_id["S09"]["limits"])
        self.assertIn("Historical membership counts", by_id["S11"]["limits"])
        self.assertIn("No parties screened", by_id["S12"]["limits"])
        self.assertIn("not the complete course", by_id["S14"]["limits"])
        self.assertIn("no branded routine or worksheet copied or adapted", by_id["S15"]["limits"])
        self.assertIn("no legal code opened", by_id["S17"]["limits"])

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
        if contract["batch"]["id"] == "M6K-ECONOMICS-CREATIVE-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/stewardship-enterprise/**",
                "tests/test_m6k_stewardship_enterprise_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 201))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 321, 62))
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


def quote_blocks(cid, name="learner-guide.md"):
    blocks = re.findall(r"(?m)(?:^>.*(?:\n|$))+", doc(cid, name))
    return [
        [line.removeprefix("> ").removesuffix("\\").strip() for line in block.splitlines()]
        for block in blocks
    ]


class CaseTests(unittest.TestCase):
    def test_externality_counts_preserve_agreed_work_and_new_burden(self):
        f = FIX["externalities"]
        self.assertEqual(f["printed_before"] - f["used_before"], 22)
        self.assertEqual(f["printed_after"] - f["used_after"], 2)
        self.assertEqual(f["sorting_before"] - f["sorting_after"], 11)
        self.assertEqual(f["sorting_before"] - f["sorting_after"] - f["new_organizer_minutes"], 7)
        self.assertIn("**7-minute net reduction**", doc("24.08", "later-packet.md"))
        self.assertIn(
            "included ten-minute closing service is unchanged", doc("24.08", "later-packet.md")
        )

    def test_externality_reduction_does_not_prove_footprint_or_access(self):
        f = FIX["externalities"]
        self.assertIsNone(f["carbon_effect"])
        self.assertFalse(f["access_revision_tested"])
        self.assertIn("larger type", doc("24.08", "later-packet.md"))
        self.assertIn("No one has agreed", doc("24.08"))
        self.assertIn(
            "disposal and carbon effects remain unmeasured", doc("24.08", "later-packet.md")
        )

    def test_macro_rates_keep_denominators_and_real_income_distinct(self):
        f = FIX["macro"]
        self.assertEqual(
            Fraction(f["basket"][1] - f["basket"][0], f["basket"][0]), Fraction(8, 100)
        )
        self.assertEqual(Fraction(f["nominal_income"][1], f["basket"][1]), Fraction(35, 36))
        self.assertEqual((f["labor_force"] - f["employed"][0]) / f["labor_force"], 0.08)
        self.assertEqual(f["sector_output"][1] / f["hours"], 11)
        self.assertIn("2.78%", doc("24.09"))

    def test_macro_slowing_inflation_is_not_falling_prices_or_proven_recession(self):
        f = FIX["macro"]
        self.assertGreater(f["basket"][2], f["basket"][1])
        self.assertLess(Fraction(f["basket"][2] - f["basket"][1], f["basket"][1]), Fraction(8, 100))
        self.assertEqual(f["sector_output"][2] / f["hours"], 9.9)
        self.assertFalse(f["national_recession_determined"])
        self.assertIn("3.70%", doc("24.09", "later-packet.md"))
        self.assertIn("recession", doc("24.09", "later-packet.md"))

    def test_tax_base_sensitivity_and_phased_access_cost_reconcile(self):
        f = FIX["public_finance"]
        revenue = [Decimal(base) * Decimal(f["rate"]) for base in f["bases"]]
        self.assertEqual(revenue, [100, 90, 85])
        cost = f["program"] + f["admin"]
        self.assertEqual([r - cost for r in revenue], [10, 0, -5])
        self.assertEqual(revenue[-1] - f["phased_program"] - f["admin"] - f["access_proposal"], 3)
        self.assertIn("82", doc("24.10", "later-packet.md"))

    def test_tax_collection_incidence_and_public_good_limits_stay_separate(self):
        f = FIX["public_finance"]
        self.assertEqual(f["assumed_buyer_burden"] + f["assumed_seller_burden"], f["collected_tax"])
        self.assertFalse(f["access_proven"])
        self.assertIsNone(f["maintenance_cost"])
        self.assertIn("incidence", doc("24.10"))
        self.assertIn("nonrival", doc("24.10"))
        self.assertIn("income", doc("24.10"))

    def test_insurance_pool_stress_and_access_cost_do_not_change_adequacy(self):
        f = FIX["insurance"]
        income = f["members"] * f["contribution"]
        self.assertEqual(income - f["base_claims"] * f["benefit"] - f["admin"], 200)
        self.assertEqual(income - f["stress_claims"] * f["benefit"] - f["admin"], -1000)
        self.assertEqual(
            income - f["stress_claims"] * f["benefit"] - f["admin"] - f["access_admin_extra"], -1040
        )
        self.assertEqual(f["stated_need"] - f["benefit"], 30)
        self.assertIn("**1,040**", doc("24.11", "later-packet.md"))

    def test_insurance_approval_is_not_receipt_and_journey_keeps_appeal(self):
        f = FIX["insurance"]
        self.assertTrue(f["application_accepted"] and f["approved"])
        self.assertFalse(f["payment_received"])
        self.assertIn("not yet been received", doc("24.11", "later-packet.md"))
        for stage in (
            "information",
            "application",
            "verification",
            "decision",
            "payment",
            "appeal",
        ):
            self.assertIn(stage, doc("24.11"))
        self.assertIn("disability-related access need", doc("24.11"))
        self.assertIn("false or mismatched evidence", doc("24.11"))

    def test_governance_funding_and_fee_gaps_remain_unfunded(self):
        f = FIX["governance"]
        self.assertEqual(f["launch_required"] - f["confirmed_capital"], f["conditional_offer"])
        self.assertLess(f["funder_hours"], f["mission_hours"])
        cost = f["worker_cost"] + f["maintenance"]
        self.assertEqual(f["revenue"] - cost, 20)
        self.assertEqual(f["revenue"] - f["fee_revenue_reduction"] - cost, -20)
        self.assertIn("**120 remains unfunded**", doc("24.12"))

    def test_governance_quorum_and_economic_ownership_are_not_automatic_control(self):
        f = FIX["governance"]
        self.assertLess(f["later_attendees"], f["routine_quorum"])
        self.assertGreater(f["mission_votes"], f["routine_votes"])
        self.assertFalse(f["entity_formed"])
        self.assertIn("cannot authorize a fee or funding decision", doc("24.12", "later-packet.md"))
        self.assertIn("Public provision is the broader alternative", doc("24.12"))
        self.assertIn("financial stake without having equal votes", doc("24.12"))

    def test_innovation_total_effort_includes_review_and_repair(self):
        f = FIX["innovation"]
        total = sum(f["draft_minutes"] + f["review_minutes"] + f["repair_minutes"])
        self.assertEqual(total, 13)
        self.assertEqual(total - sum(f["manual_minutes"]), 4)
        self.assertEqual(sum(f["initial_correct"]), 1)
        self.assertIn("**13 minutes**", doc("24.13"))
        self.assertIn("time to be confirmed", doc("24.13"))

    def test_innovation_gate_stops_release_and_incomplete_retest_is_not_readiness(self):
        f = FIX["innovation"]
        self.assertEqual((f["stop_at"], f["released"]), ("R2", 0))
        self.assertLess(f["later_checks_complete"], f["later_cases_planned"])
        self.assertFalse(f["audience_access_checked"])
        self.assertIn("failure analysis, not continued deployment", doc("24.13"))
        self.assertIn("previous pause remains in effect", doc("24.13", "later-packet.md"))
        self.assertIn("manual route", doc("24.13", "later-packet.md"))

    def test_trade_opportunity_cost_and_both_bundle_gains(self):
        f = FIX["trade"]
        a_cost = Fraction(f["a_bread"], f["a_cloth"])
        b_cost = Fraction(f["b_bread"], f["b_cloth"])
        terms = Fraction(f["terms_bread_per_cloth"])
        self.assertEqual((a_cost, b_cost), (2, 1))
        self.assertTrue(b_cost < terms < a_cost)
        self.assertEqual(f["a_bread"] - terms - (f["a_bread"] - a_cost), Fraction(1, 2))
        self.assertEqual((f["b_cloth"] - 1) - (f["b_cloth"] - terms / b_cost), Fraction(1, 2))
        self.assertIn("**4.5 bread and one cloth**", doc("24.14"))
        self.assertIn("**2.5 cloth and 1.5 bread**", doc("24.14"))

    def test_trade_disruption_currency_and_unverified_source(self):
        f = FIX["trade"]
        gaps = [d * f["delay_weeks"] - f["buffer"] for d in f["weekly_demand"]]
        self.assertEqual(gaps, [10, 25])
        costs = [f["foreign_invoice"] * Decimal(rate) for rate in f["rates"]]
        self.assertEqual(costs, [120, 130])
        self.assertFalse(f["second_source_verified"] or f["lawful_transaction_determined"])
        self.assertIn("**25 units uncovered**", doc("24.14", "later-packet.md"))
        self.assertIn("no confirmed recovery date", doc("24.14"))

    def test_production_contains_three_complete_distinct_six_sentence_scenes(self):
        blocks = quote_blocks("25.01") + quote_blocks("25.01", "later-packet.md")
        self.assertEqual([len(b) for b in blocks], [6, 6, 6])
        for obj, block in zip(FIX["production"]["objects"], blocks, strict=True):
            self.assertIn(obj, " ".join(block).lower())
            self.assertEqual(sum(len(re.findall(r"[.!?](?:\s|$)", line)) for line in block), 6)
        self.assertEqual(len({" ".join(b) for b in blocks}), 3)

    def test_production_missed_day_and_actual_burden_survive_schedule(self):
        f = FIX["production"]
        self.assertNotIn("Wednesday", f["actual_days"])
        self.assertIn("Wednesday", f["planned_days"])
        self.assertEqual(sum(f["minutes"]), 37)
        self.assertTrue(all(n <= f["max_minutes"] for n in f["minutes"]))
        self.assertEqual(f["actual_learner_sessions"], 0)
        self.assertIn("within seven days", doc("25.01"))
        self.assertIn("**Monday, Thursday and Friday**", doc("25.01", "later-packet.md"))
        self.assertIn("following Tuesday at 7:10 p.m.", doc("25.01", "later-packet.md"))

    def test_observation_details_feed_three_transformations_and_a_miniature(self):
        f = FIX["observation"]
        self.assertEqual(re.findall(r"(?m)^\| (D[1-8]) \|", doc("25.02")), f["details"])
        self.assertEqual(len(f["alternatives"]), 3)
        for mapped in f["alternatives"].values():
            self.assertGreaterEqual(len(set(mapped)), 2)
            self.assertTrue(set(mapped) <= set(f["details"]))
        self.assertEqual([len(b) for b in quote_blocks("25.02")], [6])
        self.assertIn("unsuccessful early possibility", doc("25.02"))

    def test_observation_does_not_invent_senses_or_silently_replace_prior_facts(self):
        f = FIX["observation"]
        self.assertFalse(f["actual_observer"])
        self.assertEqual(f["changed_detail"], "D7")
        self.assertIn("Sound, smell, touch and actual movement remain unavailable", doc("25.02"))
        self.assertIn("Mark D7 as changed", doc("25.02", "later-packet.md"))
        self.assertIn("not a physical observation", doc("25.02", "later-packet.md"))

    def test_aesthetics_preserves_samples_and_all_five_dimensions(self):
        f = FIX["aesthetics"]
        for sample in f["samples"]:
            self.assertIn(sample, doc("25.03"))
        for dimension in f["dimensions"]:
            self.assertIn(f"| {dimension} |", doc("25.03"))
        self.assertIn("none of the samples is itself an adequate instruction", doc("25.03"))
        self.assertIn(f["changed_purpose"], doc("25.03"))

    def test_aesthetics_new_revision_and_reception_do_not_become_universal_verdict(self):
        blocks = quote_blocks("25.03")
        self.assertEqual([len(b) for b in blocks], [3])
        self.assertNotIn(FIX["aesthetics"]["samples"][2], " ".join(blocks[0]))
        self.assertIn("coat", " ".join(blocks[0]))
        self.assertFalse(FIX["aesthetics"]["actual_reader"])
        self.assertIn("not a second independent reader", doc("25.03", "later-packet.md"))
        self.assertIn("ordinary tidying", doc("25.03", "later-packet.md"))

    def test_medium_stable_six_words_and_same_exchange_across_two_forms(self):
        f = FIX["medium"]
        words = re.findall(r"[A-Za-z]+", f["base_line"].lower())
        self.assertEqual(len(words), 6)
        for variant in f["variations"]:
            self.assertEqual(re.findall(r"[A-Za-z]+", variant.lower()), words)
            self.assertIn(variant, doc("25.04"))
        blocks = quote_blocks("25.04")
        self.assertEqual([len(b) for b in blocks], [4, 4, 4])
        for block in blocks[:2]:
            clean = [
                re.sub(r"\s+", " ", re.sub(r"\[[^]]+\]", "", line[3:])).strip().lower()
                for line in block
            ]
            self.assertEqual(clean, [line.lower() for line in f["exchange"]])

    def test_medium_three_passes_accessible_rendering_and_partial_reception(self):
        f = FIX["medium"]
        self.assertEqual(re.findall(r"(?m)^\| ([123]) \|", doc("25.04")), ["1", "2", "3"])
        self.assertFalse(f["actual_audio"] or f["later_layout_tested"])
        self.assertIn("No audio was generated or performance recorded", doc("25.04"))
        self.assertIn("less mysterious", doc("25.04", "later-packet.md"))
        self.assertIn("effect remains untested", doc("25.04", "later-packet.md"))

    def test_synthesis_both_eight_line_versions_preserve_practical_facts(self):
        f = FIX["synthesis"]
        blocks = quote_blocks("25.05")
        self.assertEqual([len(b) for b in blocks], [8, 8])
        self.assertEqual(blocks[0][:2], f["initial_opening"])
        self.assertEqual(blocks[1][:2], f["revised_opening"])
        for block in blocks:
            for fact in f["required_facts"]:
                self.assertIn(fact, " ".join(block))
        self.assertEqual(blocks[0][2:], blocks[1][2:])

    def test_synthesis_later_time_revision_keeps_eight_lines_without_clearance_claim(self):
        f = FIX["synthesis"]
        later = quote_blocks("25.05")[1].copy()
        later[6] = f["later_line"]
        self.assertEqual(len(later), 8)
        self.assertIn(f["later_line"], doc("25.05", "later-packet.md"))
        self.assertFalse(f["external_artwork_copied"] or f["actual_event"] or f["sent"])
        self.assertIn("Credit alone does not give permission", doc("25.05"))
        self.assertIn("untested proposal", doc("25.05", "later-packet.md"))


if __name__ == "__main__":
    unittest.main()
