"""Synthetic formula desk check; not a spreadsheet engine or participant assessment."""

import json
import re
from pathlib import Path


def inspect(formula, values):
    """Evaluate only this exercise's simple inclusive SUM or literal counterexample."""
    match = re.fullmatch(r"=SUM\(A([1-5]):A([1-5])\)", formula)
    cells = list(range(int(match[1]), int(match[2]) + 1)) if match else []
    if not match and not formula.isdecimal():
        raise ValueError("Desk fixture supports only inclusive SUM or a numeric literal.")
    changed = {**values, 4: values[4] + 1}
    before = sum(values[i] for i in cells) if match else int(formula)
    after = sum(changed[i] for i in cells) if match else int(formula)
    checks = {
        "C1": all(cells.count(i) == 1 for i in range(1, 5)),
        "C2": all(i in range(1, 5) for i in cells),
        "C3": before == sum(values[i] for i in range(1, 5)),
        "C4": after == sum(changed[i] for i in range(1, 5)),
    }
    return {
        "before": before,
        "after": after,
        "checks": checks,
        "observed_fraction": f"{sum(checks.values())}/4",
    }


def run():
    cases = []
    for label, formula, values in (
        ("competent_baseline", "=SUM(A1:A4)", [3, 5, 7, 9, 100]),
        ("omitted_first_input", "=SUM(A2:A4)", [3, 5, 7, 9, 100]),
        ("plausible_typed_total", "24", [3, 5, 7, 9, 100]),
        ("unrelated_input_included", "=SUM(A1:A5)", [4, 6, 8, 10, 100]),
        ("competent_retry", "=SUM(A1:A4)", [4, 6, 8, 10, 100]),
    ):
        cases.append(
            {
                "case": label,
                "formula": formula,
                "values": values,
                **inspect(formula, dict(enumerate(values, 1))),
            }
        )
    return {
        "validation_level": "synthetic arithmetic and formula-selection desk check",
        "spreadsheet_application_executed": False,
        "learner_or_qualified_acceptance": False,
        "cases": cases,
    }


if __name__ == "__main__":
    Path(__file__).with_name("component-desk-run.json").write_text(
        json.dumps(run(), indent=2) + "\n"
    )
