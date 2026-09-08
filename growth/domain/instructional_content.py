"""Unscored teaching and explicit, server-side prompt/check reveal."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

VERSION = "GG-INSTRUCTIONAL-CONTENT-1.0"
SCHEMA_PATH = Path(__file__).resolve().parents[2] / (
    "data/practices/schema/instructional_content_v1.schema.json"
)


def validate_instructional_content(document: dict, competency_id: str) -> None:
    Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(document)
    if document["competency_id"] != competency_id:
        raise ValueError("Instructional content belongs to a different competency.")
    sections = {row["id"]: row for row in document["sections"]}
    checks = {row["id"]: row for row in document["checks"]}
    if len(sections) != len(document["sections"]) or len(checks) != len(document["checks"]):
        raise ValueError("Instructional section/check IDs must be unique.")
    if set(sections) & set(checks):
        raise ValueError("Section and check IDs must be distinct.")
    linked = []
    for section in sections.values():
        for reference in section.get("references", []):
            if reference not in sections or sections[reference]["kind"] != "material":
                raise ValueError(f"Missing or non-material instructional reference: {reference}")
        if section.get("check_id"):
            linked.append(section["check_id"])
            if section["check_id"] not in checks:
                raise ValueError("Missing instructional check key.")
    if set(linked) != set(checks) or len(linked) != len(set(linked)):
        raise ValueError("Each check must belong to exactly one prompt.")


def content_fingerprint(document: dict) -> str:
    return hashlib.sha256(
        json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def learner_projection(
    document: dict, competency_id: str, *, attempt: str | None = None, check: str | None = None
) -> dict:
    """Never return unrevealed key text or an unrequested evaluation prompt."""
    validate_instructional_content(document, competency_id)
    if attempt and check:
        raise ValueError("Request an attempt or a check, not both.")
    sections = document["sections"]
    requested = None
    revealed = None
    if check:
        requested = next((s for s in sections if s.get("check_id") == check), None)
        revealed = next((c for c in document["checks"] if c["id"] == check), None)
        if requested is None or revealed is None:
            raise ValueError("Unknown instructional check.")
    elif attempt:
        requested = next(
            (s for s in sections if s["id"] == attempt and s["kind"] == "prompt"), None
        )
        if requested is None:
            raise ValueError("Unknown instructional prompt.")
    visible, prompts = [], []
    if requested:
        allowed = set(requested.get("references", [])) | {requested["id"]}
        visible = [s for s in sections if s["id"] in allowed]
    else:
        for section in sections:
            if section["kind"] == "prompt":
                prompts.append({"id": section["id"], "title": section["title"]})
            else:
                visible.append(section)
    return deepcopy(
        {
            "title": document["title"],
            "competency_id": competency_id,
            "scored": False,
            "sections": visible,
            "prompts": prompts,
            "check": revealed,
            "attempt_id": requested["id"] if requested else None,
        }
    )


def render_text(projection: dict) -> str:
    lines = [projection["title"], "", "Learning guide — unscored", ""]
    for section in projection["sections"]:
        lines.extend([section["title"], "", section["body"], ""])
    lines.extend(
        f"Open the prompt in the practice guide: {prompt['title']}"
        for prompt in projection["prompts"]
    )
    if projection["check"]:
        key = projection["check"]
        lines.extend(["Check your attempt: " + key["title"], "", key["body"], ""])
        lines.extend(f"- {criterion}" for criterion in key["criteria"])
    return "\n".join(lines) + "\n"
