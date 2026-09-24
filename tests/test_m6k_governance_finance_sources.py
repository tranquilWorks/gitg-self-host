"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from collections import Counter
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/governance-finance"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"22.{i:02}" for i in range(13, 18)] + [f"23.{i:02}" for i in range(1, 8)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 177)
        self.assertEqual(COHORT["additional_companions_after"], 189)
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
        for domain in ("22", "23"):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads(
            (ROOT / "docs/authoring/leadership-foundations/cohort.json").read_text()
        )
        self.assertEqual(previous["ids"][-1], "22.12")
        self.assertEqual(previous["additional_companions_after"], 177)
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
        for e in COHORT["entries"]:
            if e["id"].startswith("22."):
                self.assertEqual(e["classification"]["applicability"], "role_conditional")
                self.assertEqual(e["classification"]["normative_status"], "role_conditional")
                self.assertNotIn("professional_boundary", e)
                for name in ("learner-guide.md", "SCOPE-MAP.md"):
                    self.assertIn(
                        "canonical record has no professional_boundary field", doc(e["id"], name)
                    )
            else:
                self.assertEqual(e["classification"]["applicability"], "context_sensitive")
                self.assertEqual(
                    e["classification"]["normative_status"],
                    "cross_tradition_core_or_broadly_recurrent",
                )
                self.assertEqual(
                    e["professional_boundary"],
                    "Financial education only; tax, investment, insurance, estate, "
                    "and benefits decisions may require licensed or jurisdiction-specific advice.",
                )
                for name in ("learner-guide.md", "SCOPE-MAP.md"):
                    self.assertIn(e["professional_boundary"], doc(e["id"], name))
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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 16)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-24")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        by_id = {source["id"]: source for source in sources}
        self.assertIn("England and Wales", by_id["S01"]["limits"])
        self.assertIn("not generalized", by_id["S01"]["limits"])
        self.assertIn("not the full report", by_id["S02"]["limits"])
        self.assertIn("No confidentiality guarantee", by_id["S03"]["limits"])
        self.assertIn("nonbinding", by_id["S05"]["limits"])
        self.assertIn("failed retrieval", by_id["S08"]["limits"])
        self.assertIn("not disclosed APRs", doc("23.04"))
        self.assertIn("not forecasts", by_id["S11"]["limits"])
        self.assertIn("not a tax computation", by_id["S15"]["limits"])

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
        if contract["batch"]["id"] == "M6K-GOVERNANCE-FINANCE-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/leadership-foundations/**",
                "tests/test_m6k_leadership_foundations_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 177))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 297, 86))
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


def calendar(opening, incomes, outflows):
    events = [(day, amount) for day, amount in incomes] + [
        (day, -amount) for day, amount in outflows
    ]
    balances = [(0, opening)]
    for day, amount in sorted(events, key=lambda item: item[0]):
        balances.append((day, balances[-1][1] + amount))
    return balances


class CaseTests(unittest.TestCase):
    def test_procurement_eligibility_precedes_price_and_personal_voucher(self):
        f = FIX["procurement"]
        eligible = [bid for bid in f["bids"] if bid["on_time"]]
        self.assertEqual(min(eligible, key=lambda bid: bid["price"])["name"], "Alder")
        self.assertEqual(min(f["bids"], key=lambda bid: bid["price"])["name"], "Cedar")
        self.assertIn("Alder at 170", doc("22.13", "later-packet.md"))
        self.assertIn("not a price reduction", doc("22.13"))

    def test_procurement_recommendation_does_not_invent_approval(self):
        f = FIX["procurement"]
        self.assertTrue(f["recusal_recorded"])
        self.assertFalse(any(f[k] for k in ("approval", "purchase", "delivery", "legal_finding")))
        self.assertIn("no approval, purchase, delivery or payment", doc("22.13", "later-packet.md"))

    def test_capture_three_mechanisms_retain_budget_and_authority_costs(self):
        f = FIX["capture"]
        self.assertEqual(len(f["cases"]), 3)
        self.assertEqual(f["withdrawn"] - f["later_grant"], 50)
        self.assertIn("50 units unreplaced", doc("22.14", "later-packet.md"))
        self.assertIn("8 discretionary units", doc("22.14"))

    def test_capture_rotation_does_not_remove_gatekeeper(self):
        f = FIX["capture"]
        self.assertLess(f["rotating_seats"], f["panel_seats"])
        self.assertTrue(f["leader_shortlist_retained"] and f["leader_appeal_retained"])
        self.assertFalse(f["technical_approval"])
        self.assertIn("partial reform", doc("22.14", "later-packet.md"))

    def test_dissent_evidence_and_route_deadlines_stay_distinct(self):
        f = FIX["dissent"]
        self.assertEqual((f["direct_records"], f["secondhand_claims"]), (2, 1))
        self.assertFalse(f["legal_deadline_known"])
        self.assertIn("not a legal filing deadline", doc("22.15"))
        self.assertIn("retaliation complaints cannot be anonymous", doc("22.15"))
        self.assertIn("restricted, classified, privileged or personal records", doc("22.15"))

    def test_dissent_alternate_acknowledgment_is_not_clearance(self):
        f = FIX["dissent"]
        self.assertFalse(f["acknowledged_on_time"])
        self.assertTrue(f["alternate_acknowledged"])
        self.assertFalse(
            f["technical_signoff"] or f["reopening"] or f["retaliation_protection_proven"]
        )
        self.assertIn("technical sign-off pending", doc("22.15", "later-packet.md"))

    def test_governance_current_rule_selects_earliest_eligible_request(self):
        f = FIX["governance"]
        winner = min((r for r in f["requests"] if r["eligible"]), key=lambda r: r["time"])
        self.assertEqual(winner["name"], f["corrected_to"])
        self.assertIn("absent from R2", doc("22.16", "later-packet.md"))

    def test_governance_preappointed_review_survives_absence_but_notice_is_partial(self):
        f = FIX["governance"]
        self.assertTrue(
            f["coordinator_absent"] and f["reviewer_recused"] and f["substitute_preappointed"]
        )
        self.assertFalse(f["leader_veto"] or f["oversight_completed"])
        self.assertEqual(f["notices"] - f["receipts"], 1)
        self.assertIn("B's receipt remains unconfirmed", doc("22.16", "later-packet.md"))

    def test_repair_two_reports_separate_interim_protection_from_findings(self):
        f = FIX["repair"]
        self.assertEqual(f["report_count"], 2)
        self.assertTrue(f["shift_preserved_this_week"])
        self.assertFalse(f["conduct_finding"])
        self.assertIn("no conduct finding is supplied", doc("22.17", "later-packet.md"))
        self.assertIn("Never require an affected person to confront", doc("22.17"))

    def test_repair_duplicate_entries_do_not_establish_double_payment_or_fraud(self):
        f = FIX["repair"]
        self.assertEqual(sum(f["entry_amounts"]), 160)
        self.assertEqual(sum(f["payments"]), 80)
        self.assertTrue(f["audit_history_retained"])
        self.assertFalse(f["fraud_proven"] or f["monitoring_performed"])
        self.assertIn("one 80-unit payment", doc("22.17", "later-packet.md"))

    def test_literacy_reconciles_cash_without_inventing_debt_or_tax(self):
        f = FIX["literacy"]
        self.assertEqual(f["gross"] - f["withholding"], f["net"])
        self.assertEqual(sum(f["outflows"]), 2100)
        surplus = f["net"] - sum(f["outflows"])
        self.assertEqual(surplus, 300)
        self.assertEqual(f["opening_cash"] + surplus, 700)
        self.assertFalse(f["payment_allocation_known"] or f["final_tax_known"])
        self.assertIn("Closing debt remains unknown", doc("23.01"))

    def test_literacy_separate_examples_and_income_stress(self):
        f = FIX["literacy"]
        self.assertEqual(f["opening_debt"] * Decimal(f["separate_interest_rate"]), 12)
        old, new = f["basket"]
        self.assertEqual(Decimal(new - old) / old, Decimal("0.05"))
        net = f["next_net"] - sum(f["outflows"])
        self.assertEqual(net, -100)
        self.assertEqual(700 + net, 600)
        self.assertIn("closing cash is **600**", doc("23.01", "later-packet.md"))

    def test_budget_positive_month_hides_early_shortfall_and_split_repairs_it(self):
        f = FIX["budget"]
        original = calendar(f["opening"], f["incomes"], f["original_outflows"])
        revised = calendar(f["opening"], f["incomes"], f["revised_outflows"])
        self.assertEqual(sum(amount for _, amount in f["original_outflows"]), 2150)
        self.assertEqual(min(original, key=lambda row: row[1]), (8, -100))
        self.assertEqual(min(amount for _, amount in revised), 100)
        self.assertEqual((original[-1][1], revised[-1][1]), (350, 350))
        self.assertTrue(f["rent_agreed"])
        self.assertIn("with no fee or other consequence", doc("23.02"))

    def test_budget_next_cycle_uses_carry_and_delayed_income(self):
        f = FIX["budget"]
        opening = calendar(f["opening"], f["incomes"], f["revised_outflows"])[-1][1]
        second = calendar(opening, f["next_incomes"], f["revised_outflows"])
        self.assertEqual(min(second, key=lambda row: row[1]), (16, 150))
        self.assertEqual(second[-1][1], 600)
        self.assertFalse(f["actual_adherence"])
        self.assertIn("minimum is **150**", doc("23.02", "later-packet.md"))

    def test_reserve_targets_are_conditional_contribution_counts(self):
        f = FIX["reserve"]
        gaps = [need - f["accessible"] for need in f["needs"]]
        self.assertEqual(gaps, [400, 700])
        self.assertEqual([gap // f["contribution"] for gap in gaps], f["initial_contributions"])
        self.assertEqual(f["initial_contributions"], [8, 14])
        self.assertIn("not two simultaneous events", doc("23.03"))

    def test_reserve_balance_does_not_establish_weekend_access_or_protection(self):
        f = FIX["reserve"]
        funded = f["accessible"] + sum(f["later_contributions"])
        self.assertEqual(funded, 250)
        self.assertEqual([need - funded for need in f["needs"]], [350, 650])
        self.assertEqual(f["needs"][0] - f["immediate_later"], 400)
        self.assertFalse(f["protection_verified"] or f["withdrawal_tested"])
        self.assertIn("cannot be counted on for Sunday", doc("23.03", "later-packet.md"))

    def test_debt_total_cost_reverses_nominal_rate_ranking(self):
        f = FIX["debt"]
        totals = [
            f["principal"] * (1 + Decimal(rate) * f["years"]) + fee
            for rate, fee in zip(f["nominal_rates"], f["end_fees"], strict=True)
        ]
        self.assertEqual(totals, [1150, 1120])
        self.assertEqual(totals[0] - totals[1], 30)
        self.assertEqual(f["monthly_saving"] * f["months"] - totals[1], 8)
        self.assertIn("not disclosed APRs", doc("23.04"))

    def test_debt_first_miss_warns_before_two_miss_balloon_gap(self):
        f = FIX["debt"]
        self.assertEqual(f["missed_months"], [4, 7])
        self.assertEqual(f["comparison_ceiling"] - 11 * f["monthly_saving"], 86)
        self.assertEqual((f["months"] - len(f["missed_months"])) * f["monthly_saving"], 940)
        self.assertEqual(f["comparison_ceiling"] - 940, 180)
        self.assertEqual(f["current_accepted_obligation"], 0)
        self.assertFalse(f["actual_borrowing"])
        self.assertIn("180 unpaid", doc("23.04", "later-packet.md"))

    def test_investing_net_compounding_and_fee_cards_are_separate(self):
        f = FIX["investing"]
        values = [f["start"] * (1 + Decimal(rate)) ** f["years"] for rate in f["net_rates"]]
        self.assertEqual(values, [Decimal("1102.50"), Decimal("1081.60")])
        self.assertEqual(values[0] - values[1], Decimal("20.90"))
        self.assertEqual([f["start"] * Decimal(rate) for rate in f["expense_ratios"]], [2, 8])
        self.assertFalse(f["taxes_included"])
        self.assertIn("do not subtract", doc("23.05"))

    def test_investing_two_fund_names_retain_overlap_and_near_date_loss(self):
        f = FIX["investing"]
        exposure = [
            sum(
                amount * holdings[i] / 100
                for amount, holdings in zip(f["equal_split"], f["holdings"], strict=True)
            )
            for i in (0, 1)
        ]
        self.assertEqual(exposure, [600, 400])
        self.assertEqual(f["start"] * (1 - Decimal(f["loss_fraction"])), 800)
        self.assertTrue(f["official_educational_example_inspected"])
        self.assertFalse(f["actual_prospectus_inspected"] or f["trade"])
        self.assertIn("200 shortfall", doc("23.05", "later-packet.md"))

    def test_continuity_source_question_does_not_confer_authority(self):
        f = FIX["continuity"]
        self.assertEqual(f["headings"], 5)
        self.assertTrue(f["trusted_contact"] and f["source_question_answered"])
        self.assertFalse(f["bill_paying_authority"] or f["dependent_authority"])
        self.assertIn("not automatically a bill-paying agent", doc("23.06"))

    def test_continuity_locator_repair_is_not_executed_protection(self):
        f = FIX["continuity"]
        self.assertTrue(f["missing_contact_repaired"])
        self.assertFalse(
            f["inquiry_sent"] or f["policy_coverage_verified"] or f["legal_document_executed"]
        )
        self.assertIn("drafted, unsent", doc("23.06", "later-packet.md"))
        self.assertIn("no supplied authority", doc("23.06", "later-packet.md"))

    def test_consumption_complete_cost_and_opportunity_cost(self):
        f = FIX["consumption"]
        totals = [sum(parts) for parts in f["costs"]]
        self.assertEqual(totals, [0, 15, 80, 170])
        self.assertEqual(totals[-1] - f["limit"], 90)
        self.assertEqual(f["limit"] - f["chosen_cosmetic_cost"], 65)
        self.assertIn("65** of the optional 80", doc("23.07", "later-packet.md"))

    def test_consumption_supplied_uses_and_pause_do_not_invent_purchase_or_satisfaction(self):
        f = FIX["consumption"]
        self.assertEqual((f["supplied_uses"], f["pause_hours"]), (2, 48))
        self.assertTrue(f["safe"])
        self.assertFalse(
            any(
                f[k]
                for k in (
                    "structural_repair",
                    "repair_performed",
                    "purchase",
                    "lifespan_known",
                    "visitor_judgment_observed",
                )
            )
        )
        self.assertIn("No repair has been performed", doc("23.07", "later-packet.md"))
        self.assertIn("two real uses and the real pause", doc("23.07", "later-packet.md"))


if __name__ == "__main__":
    unittest.main()
