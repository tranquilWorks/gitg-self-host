"""Resolve byte-pinned source-stage inputs after the prospective app integration.

Historical source contracts and test receipts remain immutable. Current compiler,
383-route tests and recovery verification separately enforce the new projection.
Only explicitly enumerated inputs are redirected; all other bytes remain current.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/authoring/catalog-product-integration-20260928"
INPUTS = json.loads((BASE / "historical-inputs.json").read_text())


def historical_input_path(path: Path) -> Path:
    relative = path.resolve().relative_to(ROOT).as_posix()
    return ROOT / INPUTS.get(relative, relative)
