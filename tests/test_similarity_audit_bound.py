"""The fast LCS bound cannot remove a SequenceMatcher review finding."""

import random
from difflib import SequenceMatcher
from itertools import product

import pytest

from growth.services.practice_content_reports import (
    NEAR_DUPLICATE_WARNING_LIMIT,
    _near_duplicate_pairs,
    _normalize_text,
)


@pytest.mark.parametrize("threshold", [0, 0.5, 0.75, 0.8, 1.0])
def test_fast_audit_matches_original_decisions_order_rounding_and_cap(threshold):
    texts = ["", "A", "a", "ab", "ba", "aba", "bab", "tide", "diet", "é 🎨 café"]
    texts += ["".join(chars) for chars in product("abc", repeat=3)]
    rng = random.Random(383)
    texts += ["".join(rng.choices("abcd ", k=220)) for _ in range(8)]
    texts += [
        "Keep working notes private. " * 30 + ending
        for ending in ["first", "second", "first", "review the actual work"]
    ]
    values = {f"CASE-{index:03}.instructions": text for index, text in enumerate(texts)}
    expected = []
    items = sorted((key, _normalize_text(text)) for key, text in values.items())
    for i, (left_key, left_value) in enumerate(items):
        for right_key, right_value in items[i + 1 :]:
            ratio = SequenceMatcher(None, left_value, right_value).ratio()
            if ratio >= threshold:
                expected.append(
                    {"left": left_key, "right": right_key, "similarity": round(ratio, 4)}
                )
    assert (
        _near_duplicate_pairs(values, threshold=threshold)
        == expected[:NEAR_DUPLICATE_WARNING_LIMIT]
    )
