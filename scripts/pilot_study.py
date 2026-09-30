#!/usr/bin/env python3
"""Prepare and summarize a private M6L-08 study; never open the application DB."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

VERSION = "GG-M6L08-OBSERVATIONS-1.0"
MAX_BYTES = 2 * 1024 * 1024
THRESHOLD = 5
TASKS = {
    0: ("entry", "assessment", "context_choice", "direction_link", "start_practice"),
    1: ("check_in", "weekly_review", "next_week"),
    2: ("check_in", "weekly_review", "next_week"),
    3: ("check_in", "weekly_review", "history", "exit"),
}
OUTCOMES = ("completed", "unable", "stopped", "skipped")
ASSISTANCE = ("none", "prompted", "not_observed")
TIME_BANDS = ("under_2", "2_to_5", "5_to_15", "over_15", "not_reported")
FIT = ("fits", "does_not_fit", "uncertain", "not_asked")
BARRIERS = ("none_reported", "access", "comprehension", "burden", "privacy_safety", "not_asked")
AXES = (
    "item_response_distribution",
    "item_missingness_and_not_applicable",
    "test_retest_reliability",
    "convergent_and_discriminant_validity",
    "differential_item_functioning_and_fairness",
    "completion_burden_and_abandonment",
    "recommendation_fit",
    "longitudinal_outcome_association",
)


def exact_object(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def choices(values):
    return {"type": "string", "enum": list(values)}


OBSERVATION = exact_object(
    {
        "cycle": {"type": "integer", "minimum": 0, "maximum": 3},
        "task": choices(sorted({task for tasks in TASKS.values() for task in tasks})),
        "outcome": choices(OUTCOMES),
        "assistance": choices(ASSISTANCE),
        "time_band": choices(TIME_BANDS),
        "fit": choices(FIT),
        "barrier": choices(BARRIERS),
    }
)
SCHEMA = exact_object(
    {
        "schema_version": {"const": VERSION},
        "product_revision": {
            "type": "string",
            "pattern": "^[0-9a-f]{40}$",
            "minLength": 40,
            "maxLength": 40,
        },
        "data_kind": choices(("synthetic", "participant")),
        "participants": {
            "type": "array",
            "maxItems": 1000,
            "items": exact_object(
                {
                    "ref": {
                        "type": "string",
                        "pattern": "^study-[0-9a-f]{32}$",
                        "minLength": 38,
                        "maxLength": 38,
                    },
                    "consent": choices(("consented", "withdrawn")),
                    "observations": {"type": "array", "maxItems": 15, "items": OBSERVATION},
                }
            ),
        },
    }
)


def validate(dataset):
    if not Draft202012Validator(SCHEMA).is_valid(dataset):
        raise ValueError("Study input does not match the exact field and value allowlist.")
    refs = set()
    for participant in dataset["participants"]:
        if participant["ref"] in refs:
            raise ValueError("Duplicate study participant reference.")
        refs.add(participant["ref"])
        seen = set()
        for row in participant["observations"]:
            key = (row["cycle"], row["task"])
            if key in seen or row["task"] not in TASKS[row["cycle"]]:
                raise ValueError("Duplicate observation or task outside its planned cycle.")
            seen.add(key)
            if (
                row["task"] not in {"context_choice", "start_practice"}
                and row["fit"] != "not_asked"
            ):
                raise ValueError("Fit must be not_asked outside the recommendation tasks.")


def histogram(values, categories):
    counts = Counter(values)
    # Withhold the whole breakdown to avoid deriving one rare cell from its total.
    if any(0 < counts[category] < THRESHOLD for category in categories):
        return {"status": "suppressed", "counts": None}
    return {"status": "available", "counts": {key: counts[key] for key in categories}}


def summarize(dataset):
    validate(dataset)
    included = [p for p in dataset["participants"] if p["consent"] == "consented"]
    rows = []
    for cycle, tasks in TASKS.items():
        for task in tasks:
            observations = [
                next(
                    (r for r in p["observations"] if (r["cycle"], r["task"]) == (cycle, task)),
                    None,
                )
                for p in included
            ]
            outcomes = [r["outcome"] if r else "not_observed" for r in observations]
            rows.append(
                {
                    "cycle": cycle,
                    "task": task,
                    "outcomes": histogram(outcomes, (*OUTCOMES, "not_observed")),
                    **{
                        field: histogram(
                            [r[field] if r else "not_observed" for r in observations],
                            tuple(dict.fromkeys((*categories, "not_observed"))),
                        )
                        for field, categories in (
                            ("assistance", ASSISTANCE),
                            ("time_band", TIME_BANDS),
                            ("fit", FIT),
                            ("barrier", BARRIERS),
                        )
                    },
                }
            )
    returns = []
    for participant in included:
        cycles = {
            row["cycle"]
            for row in participant["observations"]
            if row["task"] == "weekly_review" and row["outcome"] == "completed"
        }
        returns.append("observed" if len(cycles) >= 2 else "not_established")
    canonical = json.dumps(dataset, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema_version": "GG-M6L08-PRIVATE-SUMMARY-1.0",
        "protocol_version": VERSION,
        "product_revision": dataset["product_revision"],
        "data_kind": dataset["data_kind"],
        "input_sha256": hashlib.sha256(canonical).hexdigest(),
        "consented_participants": len(included),
        "observation_status": (
            "observations_present"
            if any(p["observations"] for p in included)
            else "no_observations"
        ),
        "task_rows": rows,
        "observed_multiple_weekly_reviews": histogram(returns, ("observed", "not_established")),
        "completed_axes": 0,
        "open_axes": list(AXES),
        "claim_boundary": (
            "Private descriptive preparation only. Operator-entered consent and provenance are "
            "not independently verified. Missing observations are not abandonment; observed "
            "returns are not retention or effectiveness. No assessment axis, accessibility "
            "conformance, mastery or specialist review is established. No participant-level "
            "rows are emitted. Suppression does not make this safe for public release."
        ),
    }


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field.")
        result[key] = value
    return result


def write_private(path, value):
    content = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create an empty private observation file.")
    init.add_argument("--revision", required=True)
    init.add_argument("--kind", choices=("synthetic", "participant"), default="synthetic")
    init.add_argument("--output", required=True, type=Path)
    analysis = commands.add_parser("summarize", help="Write a private aggregate; no DB or network.")
    analysis.add_argument("--input", required=True, type=Path)
    analysis.add_argument("--output", required=True, type=Path)
    analysis.add_argument("--confirm-sensitive-input", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "init":
            if not re.fullmatch("[0-9a-f]{40}", args.revision):
                raise ValueError("Revision must be the full lowercase source commit.")
            result = {
                "schema_version": VERSION,
                "product_revision": args.revision,
                "data_kind": args.kind,
                "participants": [],
            }
        else:
            if not args.confirm_sensitive_input:
                raise ValueError("Analysis requires --confirm-sensitive-input.")
            if args.input.resolve() == args.output.resolve():
                raise ValueError("Input and output must be different files.")
            if not args.input.is_file():
                raise ValueError("Input must be a regular file.")
            with args.input.open("rb") as stream:
                raw = stream.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Study input exceeds the size limit.")
            result = summarize(json.loads(raw, object_pairs_hook=no_duplicate_keys))
        write_private(args.output, result)
    except (OSError, ValueError, UnicodeError, RecursionError):
        # Do not copy arbitrary input, private paths or JSON fragments into logs.
        parser.exit(
            2,
            "Study command refused: check consent acknowledgement, input format "
            "and a new writable output path.\n",
        )
    print("Private study file created with mode 0600; zero empirical evidence axes completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
