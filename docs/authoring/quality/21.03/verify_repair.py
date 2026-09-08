"""Reproduce QA-01's supplied plain-text desk cases; never score participant work."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = {"Date": "date", "Time": "time", "Location": "location", "Contact": "contact"}


def notice(row):
    return "\n".join([row["name"], *(f"{label}: {row[key]}" for label, key in LABELS.items())])


def inspect_notice(brief, output):
    """Only this supplied labeled-text format; no general layout/access certification."""
    lines = output.splitlines()
    values = {"name": lines[0] if lines else ""}
    problems = []
    for line in lines[1:]:
        label, separator, value = line.partition(":")
        key = LABELS.get(label)
        if not separator or key is None:
            problems.append("unexpected_line")
        elif key in values:
            problems.append("duplicate_" + key)
        else:
            values[key] = value.strip()
    problems.extend(k for k in ("name", *LABELS.values()) if values.get(k) != brief[k])
    return sorted(problems)


def run():
    briefs = {b["id"]: b for b in json.loads((HERE / "event-briefs.json").read_text())}
    cases = json.loads((HERE / "desk-test.json").read_text())
    outputs = []
    for label, row, expected in [
        *(("complete", row, []) for row in cases["competent_outputs"]),
        ("partial", cases["partial_output"], ["contact"]),
        ("plausible_incorrect", cases["plausible_incorrect_output"], ["date"]),
    ]:
        rendered = notice(row)
        failures = inspect_notice(briefs[row["id"]], rendered)
        if failures != expected:
            raise ValueError(f"Unexpected QA-01 result for {label}/{row['id']}: {failures}")
        outputs.append(
            {"case": label, "brief": row["id"], "notice": rendered, "failures": failures}
        )
    return {
        "execution": "executed_synthetic_author_desk_run",
        "cases": outputs,
        "accuracy_cases_verified": len(outputs),
        "usability": "U1 supplied text order inspected; "
        "U2 live audience/access testing unperformed.",
        "formal_abc_or_human_acceptance": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
