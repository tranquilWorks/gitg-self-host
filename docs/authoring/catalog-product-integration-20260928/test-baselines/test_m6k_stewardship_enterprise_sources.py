"""Source integrity and fictional-case regressions, never a learner grader."""

import hashlib
import json
import re
import unittest
from collections import Counter
from decimal import Decimal
from math import ceil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/authoring/stewardship-enterprise"
COHORT = json.loads((SOURCE / "cohort.json").read_text())
FIX = json.loads((SOURCE / "fixtures.json").read_text())
IDS = [f"23.{i:02}" for i in range(8, 13)] + [f"24.{i:02}" for i in range(1, 8)]


def doc(cid, name="learner-guide.md"):
    return (SOURCE / cid / name).read_text()


class IntegrityTests(unittest.TestCase):
    def test_exact_sequence_and_separate_runtime_count(self):
        self.assertEqual(COHORT["ids"], IDS)
        self.assertEqual(sorted(p.name for p in SOURCE.iterdir() if p.is_dir()), IDS)
        self.assertEqual(COHORT["additional_companions_before"], 189)
        self.assertEqual(COHORT["additional_companions_after"], 201)
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
        for domain in ("23", "24"):
            current = yaml.safe_load((ROOT / f"docs/authoring/exercises/{domain}.yaml").read_text())
            recovery = yaml.safe_load(
                (ROOT / f"docs/plans/m6k/recovery/selected/exercises/{domain}.yaml").read_text()
            )
            for cid in (cid for cid in IDS if cid.startswith(domain + ".")):
                self.assertEqual(current["exercises"][cid], recovery["exercises"][cid])

    def test_predecessor_and_no_new_legacy_companion(self):
        previous = json.loads((ROOT / "docs/authoring/governance-finance/cohort.json").read_text())
        self.assertEqual(previous["ids"][-1], "23.07")
        self.assertEqual(previous["additional_companions_after"], 189)
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
            if e["id"].startswith("23."):
                self.assertEqual(e["classification"]["applicability"], "context_sensitive")
                self.assertEqual(
                    e["classification"]["normative_status"],
                    "cross_tradition_core_or_broadly_recurrent",
                )
                boundary = (
                    "Financial education only; tax, investment, insurance, estate, "
                    "and benefits decisions may require licensed or jurisdiction-specific advice."
                )
            else:
                self.assertEqual(e["classification"]["applicability"], "role_conditional")
                self.assertEqual(e["classification"]["normative_status"], "role_conditional")
                boundary = (
                    "Business and economic education only; legal, tax, securities, "
                    "employment, and regulatory questions require qualified advice."
                )
            self.assertEqual(e["professional_boundary"], boundary)
            for name in ("learner-guide.md", "SCOPE-MAP.md"):
                self.assertIn(boundary, doc(e["id"], name))
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
        self.assertEqual([s["id"] for s in sources], [f"S{i:02}" for i in range(1, 17)])
        self.assertEqual({cid for s in sources for cid in s["competency_ids"]}, set(IDS))
        for source in sources:
            self.assertEqual(source["inspected"], "2026-09-24")
            self.assertTrue(source["sections"] and source["limits"])
            for cid in source["competency_ids"]:
                self.assertIn(f"../SOURCES.md#{source['id']}", doc(cid))
        by_id = {source["id"]: source for source in sources}
        self.assertIn("gift-tax paragraph is not adopted", by_id["S01"]["limits"])
        self.assertIn("not accessibility certification", by_id["S02"]["limits"])
        self.assertIn("Cost and response turnaround", by_id["S06"]["limits"])
        self.assertIn("not a live local vacancy", by_id["S08"]["limits"])
        self.assertIn("quarterly-to-monthly divide-by-four", by_id["S10"]["limits"])
        self.assertIn("No universal retention", by_id["S11"]["limits"])
        self.assertIn("Historical speaker views", by_id["S15"]["limits"])
        self.assertIn("No actual recruitment", by_id["S16"]["limits"])

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
        if contract["batch"]["id"] == "M6K-STEWARDSHIP-ENTERPRISE-TWELVE":
            self.assertEqual(contract["validation"]["required_ci"], [])
            for path in (
                "data/**",
                ".github/**",
                "docs/authoring/exercises/**",
                "docs/plans/m6k/**",
                "docs/authoring/governance-finance/**",
                "tests/test_m6k_governance_finance_sources.py",
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
        self.assertEqual((len(implemented), len(prior)), (108, 189))
        self.assertEqual(set(coverage["implemented_ids"]), implemented)
        self.assertEqual(set(coverage["prior_companion_ids"]), prior)
        self.assertEqual(coverage["new_companion_ids"], IDS)
        self.assertFalse(implemented & prior or implemented & set(IDS) or prior & set(IDS))
        covered = implemented | prior | set(IDS)
        remaining = canonical - covered
        self.assertTrue(covered <= canonical)
        self.assertEqual(set(coverage["covered_unique_ids"]), covered)
        self.assertEqual(set(coverage["remaining_ids"]), remaining)
        self.assertEqual((len(canonical), len(covered), len(remaining)), (383, 309, 74))
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


class CaseTests(unittest.TestCase):
    def test_giving_capacity_includes_preparation_and_overrun(self):
        f = FIX["generosity"]
        self.assertEqual(sum(f["planned"]), f["limit"])
        self.assertEqual(sum(f["later"]) - f["limit"], 2)
        self.assertIn("**32 minutes**", doc("23.08", "later-packet.md"))
        self.assertIn("no repayment", doc("23.08"))

    def test_giving_delivery_does_not_establish_use_or_continuation(self):
        f = FIX["generosity"]
        self.assertIsNone(f["worksheet_used"])
        self.assertFalse(f["recurring_agreement"])
        self.assertIn("worksheet use unknown", doc("23.08", "later-packet.md"))
        self.assertIn("essential care", doc("23.08"))

    def test_generational_allocations_preserve_separate_teaching_pot(self):
        f = FIX["generations"]
        self.assertEqual(sum(f["initial"]), f["available"])
        self.assertEqual(sum(f["later"]), f["available"])
        self.assertEqual(sum(f["teaching"]), 60)
        self.assertEqual(sum(f["teaching_later"]), 60)
        self.assertIn("not another 60", doc("23.09"))
        self.assertIn("50 uncommitted = 600", doc("23.09", "later-packet.md"))

    def test_generational_reservation_does_not_grant_property_rights(self):
        f = FIX["generations"]
        self.assertFalse(f["tool_permission"] or f["transfer"])
        self.assertIn("does not authorize maintenance", doc("23.09", "later-packet.md"))
        self.assertIn("Being older does not establish incapacity", doc("23.09"))
        self.assertIn("career", doc("23.09"))

    def test_lifecycle_uses_actual_wipe_instructions_and_retirement_trigger(self):
        f = FIX["lifecycle"]
        self.assertEqual(len(f["stages"]), 6)
        self.assertFalse(f["washing_allowed"] or f["food_contact"])
        self.assertIn(f["article"], doc("23.10"))
        self.assertIn("do not wash", doc("23.10", "SCOPE-MAP.md"))
        self.assertIn("triggers retirement", doc("23.10"))

    def test_lifecycle_later_burden_is_added_not_erased(self):
        f = FIX["lifecycle"]
        self.assertEqual(f["initial_minutes"] - f["expected_minutes"], 1)
        self.assertEqual(f["initial_minutes"] + f["later_minutes"], 12)
        self.assertIsNone(f["measured_carbon_saving"])
        self.assertIn("**12 minutes**", doc("23.10", "later-packet.md"))
        self.assertIn("declined", doc("23.10", "later-packet.md"))

    def test_hardship_optional_cuts_leave_essential_deficit(self):
        f = FIX["hardship"]
        essentials = sum(f["essentials"])
        self.assertEqual(essentials, 1900)
        self.assertEqual(essentials + f["optional"] - f["income"], 480)
        self.assertEqual(essentials - f["income"], 400)
        self.assertIn("Immediate danger", doc("23.11"))
        self.assertIn("essential care", doc("23.11"))

    def test_hardship_deferral_changes_timing_not_total_resources(self):
        f = FIX["hardship"]
        self.assertEqual(sum(f["essentials"]) - f["income"] - f["received_gift"], 300)
        early_cash = f["first_pay"] + f["received_gift"] - f["early_food"] - f["early_transport"]
        self.assertEqual(f["essentials"][0] - f["deferral"] - early_cash, 100)
        self.assertIsNone(f["service_cost"])
        self.assertIsNone(f["response_time"])
        self.assertFalse(f["official_contact"])
        self.assertIn("monthly gap remains **300**", doc("23.11", "later-packet.md"))

    def test_shared_money_equal_and_proportional_burdens(self):
        f = FIX["shared"]
        equal = Decimal(f["cost"]) / 2
        self.assertEqual(
            [equal / n * 100 for n in f["incomes"]], [Decimal("37.5"), Decimal("18.75")]
        )
        proportions = [Decimal(f["cost"]) * n / sum(f["incomes"]) for n in f["incomes"]]
        self.assertEqual(proportions, [300, 600])
        self.assertIn("take-home", doc("23.12"))

    def test_shared_money_threshold_and_changed_income_need_agreement(self):
        f = FIX["shared"]
        permitted = [x <= f["threshold"] and x <= f["food_remaining"] for x in f["purchases"]]
        self.assertEqual(permitted, [True, False])
        self.assertEqual(
            [f["cost"] * n // sum(f["later_incomes"]) for n in f["later_incomes"]], [360, 540]
        )
        self.assertFalse(f["relative_received"] or f["later_agreement"])
        self.assertIn("does not automatically authorize", doc("23.12", "later-packet.md"))

    def test_career_pay_comparison_keeps_hours_and_missing_costs(self):
        f = FIX["career"]
        hourly = [Decimal(p) / h for p, h in zip(f["pay"], f["hours"], strict=True)]
        self.assertEqual(hourly[0], Decimal("18.75"))
        self.assertLess(hourly[1], hourly[0])
        self.assertEqual(f["pay"][1] - f["added_transport"] - f["pay"][0], 100)
        self.assertIn("not net take-home pay", doc("24.01"))

    def test_career_capability_step_preserves_change_authority(self):
        f = FIX["career"]
        self.assertEqual(f["before_misses"] - f["after_misses"], 4)
        self.assertLess(f["handoff_success"], f["handoff_tasks"])
        self.assertEqual(sum(f["plan"]) + f["extra"] - f["budget"], 5)
        self.assertEqual(f["budget"] - (sum(f["plan"]) - f["canceled"] + f["extra"]), 15)
        self.assertFalse(f["pay_increase"])
        self.assertIn("separately approved", doc("24.01", "later-packet.md"))

    def test_value_offer_has_complete_facts_and_two_tasks_for_one_reader(self):
        f = FIX["value"]
        self.assertEqual(len(f["fields"]), 5)
        self.assertEqual(sum(f["first_results"]), 1)
        self.assertEqual(len(f["first_results"]), 2)
        self.assertEqual(sum(f["provider_minutes"]), 40)
        self.assertIn("N's first two tasks", doc("24.02"))
        self.assertIn("East entrance", doc("24.02"))

    def test_value_organizer_burden_prevents_false_savings_claim(self):
        f = FIX["value"]
        before = f["before_questions"] * f["minutes_each"]
        later = f["later_questions"] * f["minutes_each"] + f["organizer_maintenance"]
        self.assertEqual((before, later, later - before), (12, 14, 2))
        self.assertIsNone(f["paid_demand"])
        self.assertIn("**14 minutes**", doc("24.02", "later-packet.md"))

    def test_business_reconciles_profit_cash_and_receivables_separately(self):
        f = FIX["business"]
        revenue = f["orders"] * f["price"]
        costs = f["orders"] * f["variable"] + f["overhead"]
        receipts = f["paid_orders"] * f["price"]
        self.assertEqual((revenue, costs, receipts), (200, 160, 100))
        self.assertEqual((revenue - costs, f["opening_cash"] + receipts - costs), (40, 40))
        self.assertEqual(revenue - receipts, 100)
        self.assertIn("numerical coincidence", doc("24.03"))

    def test_business_rework_and_payment_delay_do_not_create_cash(self):
        f = FIX["business"]
        profit = f["orders"] * (f["price"] - f["variable"]) - f["overhead"] - f["rework"]
        self.assertEqual(profit, 25)
        self.assertEqual(40 - f["rework"], 25)
        self.assertIn("**100**", doc("24.03", "later-packet.md"))
        self.assertIn("proposed control", doc("24.03", "later-packet.md"))
        self.assertIn("Macroeconomic", doc("24.03"))

    def test_discovery_three_records_include_contradiction_and_missing_buyer(self):
        f = FIX["discovery"]
        records = f["initial_records"]
        self.assertEqual(len(records), 3)
        self.assertEqual([r["minutes"] for r in records], [20, 0, 10])
        self.assertEqual(
            {r["mechanism"] for r in records}, {"version", "adequate_alternative", "approval"}
        )
        self.assertFalse(any(r["buyer"] for r in records))
        self.assertEqual(f["actual_interviews"], 0)
        self.assertIn("spending approver is missing", doc("24.04"))

    def test_discovery_failed_prototype_stays_separate_from_interviews(self):
        f = FIX["discovery"]
        self.assertTrue(f["prototype_copies_time"] and f["later_stale"])
        self.assertFalse(f["revised_tested"])
        self.assertIn("not an extra initial interview", doc("24.04", "later-packet.md"))
        self.assertIn("no later reader task", doc("24.04", "later-packet.md"))

    def test_unit_economics_acquisition_and_lower_price_have_correct_denominators(self):
        f = FIX["units"]
        variable = f["materials"] + f["labor"] + f["handling"]
        contribution = f["price"] - variable
        self.assertEqual((variable, contribution), (7, 5))
        self.assertEqual(f["volume"] * contribution - f["fixed"] - f["campaign"], 70)
        self.assertEqual(f["campaign"] / f["new_customers"], 3)
        self.assertEqual(ceil(f["fixed"] / contribution), 20)
        self.assertEqual(ceil(f["fixed"] / (f["lower_price"] - variable)), 34)
        self.assertEqual(ceil((f["fixed"] + f["campaign"]) / (f["lower_price"] - variable)), 44)
        self.assertIn("no finite volume", doc("24.05"))

    def test_unit_economics_cash_gap_and_later_labor_stop_unfunded_scale(self):
        f = FIX["units"]
        variable = f["materials"] + f["labor"] + f["handling"]
        cash = (
            f["opening_cash"]
            + f["receipts_before_day30"]
            - f["volume"] * variable
            - f["fixed"]
            - f["campaign"]
        )
        self.assertEqual(cash, -210)
        revised = f["materials"] + f["later_labor"] + f["handling"]
        self.assertEqual(f["pilot_units"] * revised + f["fixed"], 190)
        self.assertEqual(f["volume"] * (f["price"] - revised) - f["fixed"] - f["campaign"], -10)
        self.assertEqual(f["actual_spend"], 0)
        self.assertIsNone(f["retention"])
        self.assertIn("**70**", doc("24.05", "later-packet.md"))

    def test_operations_approval_precedes_delivery_and_payment_remains_open(self):
        f = FIX["operations"]
        days = {"Thursday": 3, "Friday": 4, "Monday": 7}

        def stamp(text):
            day, clock = text.split()
            h, m = map(int, clock.split(":"))
            return days[day] * 1440 + h * 60 + m

        self.assertLess(stamp(f["approval"]), stamp(f["delivery"]))
        self.assertLess(stamp(f["delivery"]), stamp(f["deadline"]))
        self.assertLess(stamp(f["deadline"]), stamp(f["payment_due"]))
        self.assertFalse(f["payment_received"])
        self.assertIn("synthetic invoice; unpaid", doc("24.06"))

    def test_operations_pointer_repair_preserves_fiction_and_qualified_limits(self):
        f = FIX["operations"]
        self.assertEqual(len(f["initial_current"]), 2)
        self.assertEqual(f["later_current"], ["v2"])
        self.assertFalse(f["actual_independent_reader"] or f["compliance_complete"])
        self.assertIn("without coaching", doc("24.06", "later-packet.md"))
        self.assertIn("without hints", doc("24.06", "later-packet.md"))
        self.assertIn("not a legal business-record retention rule", doc("24.06"))

    def test_market_three_mechanisms_do_not_supply_shares_or_legal_findings(self):
        f = FIX["market"]
        self.assertEqual(len(f["services"]), 3)
        self.assertEqual(len(set(f["mechanisms"])), 3)
        self.assertIsNone(f["market_shares"])
        self.assertFalse(f["legal_finding"])
        self.assertIn("Low prices alone", doc("24.07"))
        self.assertIn("Capture would require evidence", doc("24.07"))

    def test_market_narrower_export_needs_privacy_and_usability(self):
        f = FIX["market"]
        self.assertTrue(f["initial_export_exposes_others"])
        self.assertFalse(f["later_export_exposes_others"])
        self.assertFalse(f["later_export_timezone"] or f["actual_export"])
        self.assertIn("omit the time zone", doc("24.07", "later-packet.md"))
        self.assertIn("indefinite blanket blocking", doc("24.07", "later-packet.md"))


if __name__ == "__main__":
    unittest.main()
