"""Explicit private intentions; never an input to recommendation or scoring."""

import hashlib
import json

CONTRACT_VERSION = "GG-PRACTICE-DIRECTION-1.0"
STATES = (
    ("unknown", "Not sure yet"),
    ("declined", "Prefer not to connect this practice"),
    ("priority", "A saved priority"),
    ("outcome", "An intended outcome"),
)


def direction_snapshot(record):
    payload = {
        "contract_version": CONTRACT_VERSION,
        "assessment_epoch": str(record.assessment_run_id),
        "protocol_id": str(record.protocol_id),
        "state": record.state,
        "intended_outcome": record.intended_outcome,
        "priority_index": record.priority_index,
        "personal_os_revision": record.personal_os.revision if record.personal_os_id else None,
        "personal_os_hash": record.personal_os.content_hash if record.personal_os_id else None,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return payload, hashlib.sha256(encoded.encode()).hexdigest()
