"""Desk-test original source cases; no runtime scoring or participant state.

Helpers below validate only stipulated synthetic fixtures. They are not a new
application validator, scheduler, health model or competency assessment.
"""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import re
import unittest
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "docs/authoring/execution-capacity-closeout"
DATA = json.loads((CONTENT / "fixtures.json").read_text())
META = json.loads((CONTENT / "cohort.json").read_text())
IDS = [f"11.{n:02}" for n in range(5, 11)]


def source(cid, name="learner-guide.md"):
    return (CONTENT / cid / name).read_text()


def natural(value):
    if type(value) is not int or value < 0:
        raise ValueError("Expected a nonnegative integer")
    return value


def minute(value):
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise ValueError("Expected HH:MM")
    hour, part = map(int, value.split(":"))
    return hour * 60 + part


def schedule(rows, window):
    start, end = map(natural, window)
    if start >= end:
        raise ValueError("Empty or reversed window")
    previous = start
    seen = set()
    for a, b, label, duration in rows:
        for value in (a, b, duration):
            natural(value)
        if a < previous or b <= a or b > end or b - a != duration:
            raise ValueError("Overlap, out-of-window or wrong duration")
        if not isinstance(label, str) or not label or label in seen:
            raise ValueError("Missing or duplicate allocation")
        seen.add(label)
        previous = b
    return sum(row[3] for row in rows)


def fits(start, duration, access):
    for value in (start, duration, *access):
        natural(value)
    if duration == 0 or access[0] >= access[1]:
        raise ValueError("Invalid duration or access")
    return access[0] <= start and start + duration <= access[1]


def remaining_reserve(reserve, interruptions, released=0):
    natural(reserve)
    natural(released)
    return reserve + released - sum(natural(x) for x in interruptions)


def board(cards, limit=1):
    natural(limit)
    if limit == 0 or len({c["id"] for c in cards}) != len(cards):
        raise ValueError("Invalid capacity or duplicate card")
    by_id = {c["id"]: c for c in cards}
    visiting, visited = set(), set()

    def visit(cid):
        if cid in visiting or cid not in by_id:
            raise ValueError("Cycle or unknown dependency")
        if cid in visited:
            return
        visiting.add(cid)
        for dep in by_id[cid]["dependencies"]:
            visit(dep)
        visiting.remove(cid)
        visited.add(cid)

    for c in cards:
        visit(c["id"])
        if not isinstance(c["owner"], str) or not c["owner"].strip() or c["consented"] is not True:
            raise ValueError("Ownership needs consent")
        if c["state"] not in {"ready", "doing", "blocked", "done"}:
            raise ValueError("Unknown state")
        if type(c["accepted"]) is not bool:
            raise ValueError("Malformed acceptance")
        if c["state"] == "done" and (not c["output"] or not c["accepted"]):
            raise ValueError("Done needs an accepted output")
        if c["state"] == "blocked":
            for field in ("missing_input", "unblock_owner", "next_check"):
                if not isinstance(c.get(field), str) or not c[field].strip():
                    raise ValueError(
                        "Blocked work needs an input, responsible owner and checkpoint"
                    )
            if not any(
                owner["owner"] == c["unblock_owner"] and owner["consented"] is True
                for owner in cards
            ):
                raise ValueError("Unblocking responsibility needs a consenting owner")
        if c["state"] != "blocked" and any(by_id[d]["state"] != "done" for d in c["dependencies"]):
            raise ValueError("Dependencies incomplete")
    if sum(c["state"] == "doing" for c in cards) > limit:
        raise ValueError("WIP exceeds available worker")
    return True


def accepted_rate(attempted, wrong, initial_minutes, rework_minutes, verified_repairs=0):
    for value in (attempted, wrong, initial_minutes, rework_minutes, verified_repairs):
        natural(value)
    if (
        wrong > attempted
        or verified_repairs > wrong
        or initial_minutes + rework_minutes == 0
        or (verified_repairs > 0 and rework_minutes == 0)
    ):
        raise ValueError("Invalid accounting")
    accepted = attempted - wrong + verified_repairs
    return accepted, Fraction(accepted, initial_minutes + rework_minutes)


def promise(events, now, original=None, proposal=None):
    """Case states; 'receipt' confirms the preceding successful handoff attempt."""
    original = copy.deepcopy(original or DATA["promise"]["original"])
    proposal = copy.deepcopy(proposal or DATA["promise"]["proposal"])
    natural(now)
    for terms in (original, proposal):
        natural(terms["due"])
        if not terms["method"] or not terms["item"]:
            raise ValueError("Incomplete terms")
    current = copy.deepcopy(original)
    proposed = accepted = False
    last, attempted_at, received_at = -1, None, None
    for at, kind in events:
        natural(at)
        if at <= last or at > now:
            raise ValueError("Unordered, duplicate or future event")
        last = at
        if kind == "propose":
            if proposed:
                raise ValueError("Duplicate proposal")
            proposed = True
        elif kind == "accept":
            if not proposed or accepted or at >= proposal["due"]:
                raise ValueError("Missing proposal, duplicate or expired acceptance")
            accepted = True
            current = copy.deepcopy(proposal)
        elif kind in {"acknowledge", "clarify"}:
            if not proposed:
                raise ValueError("No proposal to acknowledge")
        elif kind == "intermediary":
            if not accepted or current["method"] != "Jo":
                raise ValueError("Unauthorized intermediary")
        elif kind == "attempt":
            attempted_at = at
        elif kind == "failed_attempt":
            attempted_at = None
        elif kind == "receipt":
            if attempted_at is None or received_at is not None:
                raise ValueError("Receipt lacks a successful attempt")
            received_at = attempted_at
        else:
            raise ValueError("Unknown event")
    status = "open"
    if received_at is not None:
        status = "received_on_time" if received_at <= current["due"] else "received_late"
    elif now >= current["due"]:
        status = "missed"
    return {
        "original": original,
        "current": current,
        "accepted": accepted,
        "receipt": received_at,
        "status": status,
    }


def trial(outcomes, costs, comparable, burden):
    if len(outcomes) != 3 or len(costs) != 3 or any(len(c) != 2 for c in costs):
        raise ValueError("Preserve the three planned opportunities and both costs")
    for value in [*outcomes, comparable, burden]:
        if value is not None and type(value) is not bool:
            raise ValueError("Unknown is not a truthy label or numeric score")
    for value in itertools.chain.from_iterable(costs):
        if value is not None:
            natural(value)
    if burden is True:
        return "reject"
    if (
        any(x is None for x in outcomes)
        or any(x is None for x in itertools.chain.from_iterable(costs))
        or comparable is not True
        or burden is None
    ):
        return "inconclusive"
    if sum(outcomes) <= 1:
        return "reject"
    return "retain" if sum(map(sum, costs)) <= 24 else "revise"


class SourceIntegrity(unittest.TestCase):
    def test_exact_six_canonical_identities(self):
        self.assertEqual(META["ids"], IDS)
        self.assertEqual([e["id"] for e in META["entries"]], IDS)
        curriculum = yaml.safe_load(
            (
                ROOT / "data/curriculum/ideal_person_curriculum_v2_pluralist_full_scope.yaml"
            ).read_text()
        )
        domain = next(d for d in curriculum["curriculum"]["domains"] if d["id"] == "11")
        canonical = [entry for entry in domain["competencies"] if entry["id"] in IDS]
        self.assertEqual(META["entries"], canonical)
        for entry in META["entries"]:
            with self.subTest(cid=entry["id"]):
                self.assertIn(entry["name"], source(entry["id"]))
                scope = source(entry["id"], "SCOPE-MAP.md")
                self.assertIn(entry["scope"], scope)
                self.assertIn(entry["evidence_of_progress"], scope)
                self.assertIn("minimum_standard", entry["measurement"])

    def test_inputs_and_frozen_package_are_byte_pinned(self):
        for path, expected in META["input_sha256"].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_relative_learning_links_resolve(self):
        for path in CONTENT.rglob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if not target.startswith("https://"):
                    self.assertTrue((path.parent / target.split("#")[0]).is_file(), (path, target))

    def test_all_six_have_separate_attempt_and_correction_files(self):
        for cid in IDS:
            guide, prompt, key = (
                source(cid, p) for p in ("learner-guide.md", "check-prompts.md", "check-answers.md")
            )
            self.assertIn("later-packet.md", guide)
            self.assertEqual(len(re.findall(r"^## Check \d", prompt, re.MULTILINE)), 2)
            self.assertNotIn(key.strip(), guide + prompt)
            self.assertIn("Check 1", key)
            self.assertIn("Check 2", key)
            for label in ("Supportive", "Mixed", "Contradictory", "Inconclusive"):
                self.assertIn(f"**{label}:**", guide)

    def test_runtime_and_review_claims_remain_separate(self):
        self.assertTrue(META["source_only"])
        self.assertEqual((META["runtime_tailored"], META["runtime_pending"]), (108, 275))
        self.assertEqual((META["protocols"], META["actions"]), (383, 1151))
        notes = (CONTENT / "SOURCES.md").read_text()
        self.assertIn("independent cold-start acceptance", notes)
        self.assertIn("remain pending", notes)
        self.assertIn("practice-observation-v1", notes)


class ScheduleCases(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(DATA["schedule"])

    def test_actual_markdown_baseline_matches_complete_fixture(self):
        rows = re.findall(
            r"\| (\d\d:\d\d)\u2013(\d\d:\d\d) \| ([^|]+) \| (\d+) \|", source("11.05")
        )
        parsed = [[minute(a), minute(b), label.strip(), int(n)] for a, b, label, n in rows]
        self.assertEqual(parsed, self.data["baseline"])
        self.assertEqual(schedule(parsed, self.data["window"]), 180)

    def test_every_baseline_dependency_and_access(self):
        rows = self.data["baseline"]
        for left, right in itertools.pairwise(rows):
            self.assertEqual(left[1], right[0])
        self.assertTrue(fits(rows[1][0], rows[1][3], self.data["form_energy"]))
        self.assertTrue(fits(rows[6][0], rows[6][3], self.data["errand_access"]))
        self.assertEqual(rows[3][:2], [610, 640])
        self.assertEqual(rows[4][3], 15)

    def test_late_buffer_does_not_rescue_errand_access(self):
        self.assertEqual(self.data["errand_access"][1] - 30, 675)
        self.assertFalse(fits(675 + 5, 30, self.data["errand_access"]))
        rows = self.data["baseline"][:5] + self.data["branch_a_remaining"]
        self.assertEqual(schedule(rows, self.data["window"]), 180)
        self.assertEqual(remaining_reserve(30, [20], 30 + 5), 45)

    def test_interrupted_form_preserves_unfinished_work(self):
        case = self.data["branch_b"]
        self.assertEqual(case["form_done"] + case["form_remaining"], 60)
        self.assertEqual(case["interruption"][1] + case["form_remaining"], 625)
        self.assertEqual(case["form_deadline"] - case["interruption"][1], 20)
        self.assertIn("At 09:25 communicate", source("11.05", "check-answers.md"))

    def test_disjoint_windows_cannot_be_added_for_unsplittable_task(self):
        c = self.data["fresh_1"]
        self.assertEqual(sum(b - a for a, b in c["windows"]), 45)
        self.assertEqual(max(b - a for a, b in c["windows"]), 25)
        self.assertFalse(any(fits(a, c["task"] + c["handoff"], (a, b)) for a, b in c["windows"]))
        self.assertEqual(840 - c["task"] - c["handoff"], 805)

    def test_reserve_spent_once_and_deferred_task_not_done(self):
        c = self.data["fresh_2"]
        self.assertEqual(remaining_reserve(c["reserve"], c["interruptions"]), -5)
        free = remaining_reserve(c["reserve"], c["interruptions"], c["deferred"])
        self.assertEqual(free, 5)
        self.assertEqual(
            c["work"] - c["deferred"] + c["recovery"] + sum(c["interruptions"]) + free,
            c["window"],
        )
        self.assertIn("optional task pending", source("11.05", "check-answers.md"))

    def test_overlap_is_rejected_even_with_correct_total(self):
        rows = self.data["baseline"]
        rows[-1] = [680, 710, "Reserved buffer", 30]
        with self.assertRaises(ValueError):
            schedule(rows, self.data["window"])

    def test_duplicate_reserve_is_rejected(self):
        rows = self.data["baseline"]
        rows[-1] = [690, 705, "Reserved buffer", 15]
        rows.append([705, 720, "Reserved buffer", 15])
        with self.assertRaises(ValueError):
            schedule(rows, self.data["window"])

    def test_duration_and_window_boundaries(self):
        self.assertTrue(fits(675, 30, [660, 705]))
        self.assertFalse(fits(676, 30, [660, 705]))
        for row in (
            [540, 540, "x", 0],
            [539, 544, "x", 5],
            [540, 546, "x", 5],
            [715, 725, "x", 10],
        ):
            with self.subTest(row=row), self.assertRaises(ValueError):
                schedule([row], [540, 720])

    def test_malformed_times_and_numbers_fail(self):
        for bad in ("9:00", "24:00", "10:60", "09:00Z", "-1:00"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                minute(bad)
        for bad in (True, -1, 1.5, "5", None, float("nan")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                remaining_reserve(bad, [])


class WorkflowCases(unittest.TestCase):
    def setUp(self):
        self.cards = copy.deepcopy(DATA["workflow"]["cards"])

    def test_source_inventory_exactly_matches_fixture(self):
        rows = re.findall(
            r"\| (Upper Left|Upper Right|Lower Left|Lower Right) \| ([^|]+) \| ([^|]+) \|",
            source("11.06"),
        )
        self.assertEqual([[x.strip() for x in row] for row in rows], DATA["workflow"]["inventory"])

    def test_complete_key_can_find_and_return_both_actual_items(self):
        key = source("11.06", "check-answers.md").split("Its four location outputs")[0]
        locations = re.findall(r"(?:in|to) (Upper Left|Lower Left|Upper Right|Lower Right)", key)
        self.assertEqual(locations, DATA["workflow"]["v1_locations"])
        inventory = {item: location for location, label, item in DATA["workflow"]["inventory"]}
        self.assertEqual(
            locations,
            [inventory[t] for t in DATA["workflow"]["targets"] for _ in range(2)],
        )

    def test_inherited_draft_fails_actual_retrieval(self):
        d = DATA["workflow"]
        self.assertEqual(
            [a == b for a, b in zip(d["v0_locations"], d["v1_locations"], strict=True)],
            [True, True, False, True],
        )
        self.assertEqual(d["reader_v0"], [True, True, False, None])
        self.assertIn("not-tested", source("11.06", "check-answers.md"))

    def test_initial_board_and_completed_outputs(self):
        self.assertTrue(board(self.cards))
        for card in self.cards:
            card.update(state="doing")
            self.assertTrue(board(self.cards))
            card.update(state="done", output=f"{card['id']}-artifact", accepted=True)
            self.assertTrue(board(self.cards))

    def test_initial_card_states_and_dependencies_align_with_source(self):
        rows = re.findall(
            r"^\| ([SIDTR]) [^|]+ \| [^|]+ \| ([^|]+) \| (Ready|Blocked) \|$",
            source("11.06"),
            re.MULTILINE,
        )
        self.assertEqual([r[0] for r in rows], [c["id"] for c in self.cards])
        for (cid, dependency, state), card in zip(rows, self.cards, strict=True):
            self.assertEqual(state.lower(), card["state"])
            if cid != "S":
                self.assertEqual([dependency.strip()], card["dependencies"])
                self.assertEqual(card["missing_input"], f"{dependency.strip()} output")
                self.assertEqual(card["unblock_owner"], "learner")

    def test_blocked_input_owner_and_checkpoint_cannot_be_missing(self):
        for field in ("missing_input", "unblock_owner", "next_check"):
            for value in (None, "", " ", True):
                with self.subTest(field=field, value=value):
                    cards = copy.deepcopy(self.cards)
                    cards[1][field] = value
                    with self.assertRaises(ValueError):
                        board(cards)

    def test_unblocking_cannot_be_assigned_to_an_unconsenting_outsider(self):
        self.cards[1]["unblock_owner"] = "Lee"
        with self.assertRaises(ValueError):
            board(self.cards)

    def test_done_without_output_fails(self):
        self.cards[0].update(state="done", accepted=True)
        with self.assertRaises(ValueError):
            board(self.cards)

    def test_done_with_failed_acceptance_fails(self):
        self.cards[0].update(state="done", output="draft", accepted=False)
        with self.assertRaises(ValueError):
            board(self.cards)

    def test_unconsenting_owner_fails(self):
        self.cards[0].update(owner="Lee", consented=False)
        with self.assertRaises(ValueError):
            board(self.cards)

    def test_wip_capacity_cannot_be_duplicated(self):
        self.cards[0]["state"] = "doing"
        self.cards[1].update(state="doing", dependencies=[])
        with self.assertRaises(ValueError):
            board(self.cards)

    def test_ready_or_doing_without_dependency_fails(self):
        for state in ("ready", "doing", "done"):
            with self.subTest(state=state):
                cards = copy.deepcopy(self.cards)
                cards[1].update(state=state, output="premature", accepted=True)
                with self.assertRaises(ValueError):
                    board(cards)

    def test_unknown_duplicate_and_cyclic_cards_fail(self):
        for mode in ("unknown", "duplicate", "cycle"):
            with self.subTest(mode=mode):
                cards = copy.deepcopy(self.cards)
                if mode == "unknown":
                    cards[1]["dependencies"] = ["Z"]
                elif mode == "duplicate":
                    cards[1]["id"] = "S"
                else:
                    cards[0].update(dependencies=["R"], state="blocked")
                with self.assertRaises(ValueError):
                    board(cards)

    def test_rework_cannot_leave_failed_card_done(self):
        for card in self.cards:
            card.update(state="done", output="v1", accepted=True)
        self.assertTrue(board(self.cards))
        self.cards[2].update(output="v2", accepted=False)
        with self.assertRaises(ValueError):
            board(self.cards)
        self.assertIn("rerun the two-location", source("11.06", "check-answers.md"))

    def test_paper_self_review_does_not_supply_release_acceptance(self):
        guide = source("11.06")
        self.assertIn("shared release", guide)
        self.assertIn("actual willing reader", guide)
        self.assertIn("shared release remains blocked", source("11.06", "later-packet.md"))


class PacingCases(unittest.TestCase):
    def test_inventory_table_is_complete_and_exact(self):
        rows = re.findall(r"\| ([AB]) \| ([^|]+) \| (\d+) \|", source("11.07"))
        self.assertEqual([[a, b.strip(), int(c)] for a, b, c in rows], DATA["pacing"]["inventory"])
        self.assertEqual(len({r[1] for r in rows}), 8)

    def test_maintenance_and_sprint_include_rework(self):
        m, s = DATA["pacing"]["maintenance"], DATA["pacing"]["sprint"]
        self.assertEqual(sum(m["active"]), 37)
        self.assertEqual(sum(s["active"]), 60)
        self.assertEqual(s["attempted"] - s["wrong"], 5)
        self.assertEqual(sum(m["recovery"]), 20)
        self.assertEqual(s["care_delay"], 10)
        self.assertIn("60 active minutes", source("11.07", "check-answers.md"))

    def test_corrected_items_not_counted_twice(self):
        a, b = DATA["pacing"]["fresh"]
        count_a, rate_a = accepted_rate(*a)
        count_b, rate_b = accepted_rate(*b)
        self.assertEqual((count_a, count_b), (12, 10))
        self.assertEqual((rate_a, rate_b), (Fraction(2, 7), Fraction(1, 3)))
        self.assertLess(rate_a, rate_b)

    def test_unrepaired_wrong_items_not_accepted(self):
        self.assertEqual(accepted_rate(8, 3, 40, 0)[0], 5)

    def test_rework_time_alone_cannot_certify_repairs(self):
        self.assertEqual(accepted_rate(8, 3, 40, 12)[0], 5)
        self.assertEqual(accepted_rate(8, 3, 40, 12, 2)[0], 7)
        with self.assertRaises(ValueError):
            accepted_rate(8, 3, 40, 12, 4)
        with self.assertRaises(ValueError):
            accepted_rate(8, 3, 40, 0, 3)

    def test_bounded_sprint_preserves_separate_recovery(self):
        self.assertEqual(4 * 6 + 10, 34)
        self.assertEqual(40 - (4 * 6 + 10), 6)
        self.assertGreater(4 * 8 + 10, 40)
        self.assertIn("15-minute recovery", source("11.07", "check-answers.md"))

    def test_malformed_pace_counts_fail(self):
        for values in (
            (1, 2, 3, 0),
            (1, 0, 0, 0),
            (True, 0, 3, 0),
            (1, 0, -1, 0),
            (1, 0, 2.5, 0),
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                accepted_rate(*values)

    def test_recovery_is_not_fabricated_output_or_punitive_deadline(self):
        key = source("11.07", "check-answers.md")
        self.assertIn("zero attempted", key)
        self.assertIn("unknown next-day capacity", key)
        self.assertIn("No medical consequence", source("11.07", "later-packet.md"))


class PromiseCases(unittest.TestCase):
    def test_accepted_revision_and_confirmed_receipt(self):
        result = promise(DATA["promise"]["A"], 1985)
        self.assertEqual(result["status"], "received_on_time")
        self.assertEqual(result["receipt"], 1980)
        self.assertEqual(result["current"]["due"], 1980)
        self.assertEqual(result["original"]["due"], 2460)

    def test_acknowledgment_does_not_change_original_promise(self):
        result = promise(DATA["promise"]["B"], 2460)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["current"], result["original"])
        self.assertEqual(result["status"], "missed")

    def test_intermediary_custody_is_not_receipt(self):
        result = promise(DATA["promise"]["A"][:3], 1080)
        self.assertIsNone(result["receipt"])
        self.assertEqual(result["status"], "open")

    def test_failed_revised_promise_does_not_revert_due(self):
        result = promise(DATA["promise"]["C"], 1990)
        self.assertEqual(result["status"], "missed")
        self.assertEqual(result["current"]["due"], 1980)
        self.assertIsNone(result["receipt"])

    def test_attempt_without_receipt_stays_unconfirmed(self):
        result = promise(DATA["promise"]["A"][:-1], 1985)
        self.assertIsNone(result["receipt"])
        self.assertEqual(result["status"], "missed")

    def test_late_receipt_remains_late(self):
        events = [
            [720, "propose"],
            [750, "accept"],
            [2000, "attempt"],
            [2005, "receipt"],
        ]
        self.assertEqual(promise(events, 2005)["status"], "received_late")

    def test_no_proposal_or_expired_acceptance_fails(self):
        for events in ([[[750, "accept"]]], [[[720, "propose"], [1980, "accept"]]]):
            with self.assertRaises(ValueError):
                promise(events[0], 2000)

    def test_unauthorized_intermediary_and_unsupported_receipt_fail(self):
        for events in (
            [[720, "propose"], [1080, "intermediary"]],
            [[720, "propose"], [750, "accept"], [1985, "receipt"]],
        ):
            with self.subTest(events=events), self.assertRaises(ValueError):
                promise(events, 2000)

    def test_chronology_and_malformed_events_fail(self):
        for events in (
            [[750, "accept"], [720, "propose"]],
            [[720, "propose"], [720, "acknowledge"]],
            [[3000, "propose"]],
            [[True, "propose"]],
            [[720, "delivered_probably"]],
        ):
            with self.subTest(events=events), self.assertRaises(ValueError):
                promise(events, 2500)

    def test_input_promise_and_events_are_immutable(self):
        before = copy.deepcopy(DATA["promise"])
        promise(DATA["promise"]["A"], 1985)
        self.assertEqual(DATA["promise"], before)

    def test_source_events_and_clock_offsets_align(self):
        self.assertEqual(1440 + 9 * 60, DATA["promise"]["proposal"]["due"])
        self.assertEqual(1440 + 17 * 60, DATA["promise"]["original"]["due"])
        packet = source("11.08", "later-packet.md")
        for phrase in (
            "Thursday 12:30",
            "Thursday 18:00",
            "Friday 09:05",
            "Friday 17:00",
            "No Monday delivery",
        ):
            self.assertIn(phrase, packet)
        self.assertIn("repair draft is not a sent acceptance", source("11.08", "check-answers.md"))


class ReviewCases(unittest.TestCase):
    def test_original_baseline_and_denominator(self):
        rows = re.findall(r"\| (Monday|Wednesday|Friday) \| (yes|no) \| (\d+) \|", source("11.09"))
        self.assertEqual([r[1] == "yes" for r in rows], DATA["review"]["baseline"]["outcomes"])
        self.assertEqual([int(r[2]) for r in rows], DATA["review"]["baseline"]["active"])
        self.assertEqual(sum(int(r[2]) for r in rows), 21)

    def test_all_later_table_values_align_with_fixture(self):
        packet = source("11.09", "later-packet.md")
        rows = re.findall(r"^\| ([A-F]) \| (.*?) \| (.*?) \| (.*?) \|", packet, re.MULTILINE)
        self.assertEqual(len(rows), 6)
        for name, *days in rows:
            branch = DATA["review"]["branches"][name]
            outcomes, costs = [], []
            for day in days:
                ready, evening, morning = re.fullmatch(
                    r"(yes|no); (\d+|unknown)\+(\d+)", day
                ).groups()
                outcomes.append(ready == "yes")
                costs.append([None if evening == "unknown" else int(evening), int(morning)])
            self.assertEqual(outcomes, branch["outcomes"])
            self.assertEqual(costs, branch["costs"])

    def test_every_branch_recomputes_expected_decision(self):
        for name, b in DATA["review"]["branches"].items():
            with self.subTest(branch=name):
                self.assertEqual(
                    trial(b["outcomes"], b["costs"], b["comparable"], b["burden"]),
                    b["expected"],
                )

    def test_boundary_24_is_retained_25_revised(self):
        self.assertEqual(trial([True, False, True], [[4, 4]] * 3, True, False), "retain")
        self.assertEqual(
            trial([True, False, True], [[5, 4], [4, 4], [4, 4]], True, False), "revise"
        )

    def test_outcome_threshold_and_adversity_exhaustively(self):
        for outcomes in itertools.product([False, True], repeat=3):
            for burden in (False, True):
                expected = "reject" if burden or sum(outcomes) <= 1 else "retain"
                self.assertEqual(trial(outcomes, [[4, 4]] * 3, True, burden), expected)

    def test_unknown_not_zero_or_success(self):
        self.assertEqual(trial([True, True, None], [[4, 4]] * 3, True, False), "inconclusive")
        self.assertEqual(
            trial([True] * 3, [[4, 4], [None, 4], [4, 4]], True, False), "inconclusive"
        )
        self.assertEqual(trial([True] * 3, [[4, 4]] * 3, True, None), "inconclusive")

    def test_known_adverse_burden_stops_even_with_missing_data(self):
        self.assertEqual(trial([None] * 3, [[None, None]] * 3, None, True), "reject")

    def test_different_conditions_are_not_method_effect(self):
        self.assertEqual(trial([True] * 3, [[4, 4]] * 3, False, False), "inconclusive")
        self.assertIn("material availability differs", source("11.09", "later-packet.md"))

    def test_cost_range_crossing_threshold_is_uncertain(self):
        low, high = 7 + 8 + 7, 7 + 11 + 7
        self.assertEqual((low, high), (22, 25))
        self.assertLessEqual(low, 24)
        self.assertGreater(high, 24)
        self.assertIn("22\u201325", source("11.09", "check-answers.md"))

    def test_malformed_or_reduced_denominator_fails(self):
        for outcomes, costs in (
            ([True] * 2, [[4, 4]] * 2),
            ([True] * 3, [[4]] * 3),
            ([1, 0, 1], [[4, 4]] * 3),
            ([True] * 3, [[-1, 4]] * 3),
            ([True] * 3, [[True, 4]] * 3),
        ):
            with (
                self.subTest(outcomes=outcomes, costs=costs),
                self.assertRaises(ValueError),
            ):
                trial(outcomes, costs, True, False)


class BoundaryCases(unittest.TestCase):
    def test_actual_frozen_runtime_rules_are_pinned(self):
        # Hash checked above; exact snippets also guard the intended compatibility contract.
        package = (ROOT / "data/practices/protocols/11/PRACTICE-BOUNDARY-01.yaml").read_text()
        self.assertEqual(
            re.findall(r"  - stable_id: (PRACTICE-BOUNDARY-01-A\d)", package),
            [f"PRACTICE-BOUNDARY-01-A{i}" for i in (1, 2, 3)],
        )
        due = re.findall(r"    due_within_days: (\d+|null)", package)
        self.assertEqual(
            [None if x == "null" else int(x) for x in due],
            DATA["boundary"]["due_within_days"],
        )
        self.assertIn("duration_days: 10", package)
        self.assertIn("minimum_completed: 2", package)
        self.assertIn("marker_mode: all", package)
        self.assertEqual(package.count("schema_version: practice-observation-v1"), 3)

    def test_action_specific_observation_allowlists_unchanged(self):
        package = (ROOT / "data/practices/protocols/11/PRACTICE-BOUNDARY-01.yaml").read_text()
        matches = re.findall(
            r"primary_markers:\n      - (\w+)\n      supporting_markers:\n      - (\w+)",
            package,
        )
        self.assertEqual([list(x) for x in matches], DATA["boundary"]["markers"])

    def test_legitimate_limit_needs_no_approval_but_duty_remains(self):
        a, b = DATA["boundary"]["A"], DATA["boundary"]["B"]
        self.assertFalse(a["approval"])
        self.assertEqual(a["packs"], DATA["boundary"]["setup_packs"])
        self.assertEqual(DATA["boundary"]["setup_packs"] - b["packs"], 1)
        self.assertIn("proposed repair", source("11.10", "check-answers.md"))

    def test_preparation_is_not_live_follow_through(self):
        packet = source("11.10", "later-packet.md")
        key = source("11.10", "check-answers.md")
        self.assertIn("No direct statement or follow-through", packet)
        self.assertIn("neither a direct communicated statement", key)
        self.assertIn("Reading checks are not replacement application evidence", key)

    def test_unsafe_branch_stops_instead_of_coercing_closure(self):
        self.assertFalse(DATA["boundary"]["C"]["safe"])
        self.assertIn("Do not continue this interaction", source("11.10", "later-packet.md"))
        self.assertIn("withholding the key", source("11.10", "check-answers.md"))

    def test_project_and_relationship_endings_have_distinct_remaining_duties(self):
        guide = source("11.10")
        for phrase in (
            "ten paper tickets",
            "Three blank ticket drafts",
            "Saturday by noon",
            "Saturday at 11:00",
            "No other item is owed",
        ):
            self.assertIn(phrase, guide)
        self.assertIn(
            "new return method would need agreement",
            source("11.10", "check-answers.md"),
        )


if __name__ == "__main__":
    unittest.main()
