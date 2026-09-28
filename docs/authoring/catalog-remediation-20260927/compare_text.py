import collections
import hashlib
import json
import re
from pathlib import Path

import yaml

E = Path(__file__).resolve().parent
ROOT = E.parents[2]
rows = json.loads((ROOT / "docs/authoring/catalog-quality-audit-20260927/audit.json").read_text())[
    "rows"
]
D = {}
loaded = {}
for row in rows:
    cid = row["competency_id"]
    p = ROOT / row["source_path"]
    if row["source_kind"] == "companion":
        t = p.read_text()
    else:
        if p not in loaded:
            loaded[p] = yaml.safe_load(p.read_text())["exercises"]
        t = yaml.safe_dump(loaded[p][cid], sort_keys=False, allow_unicode=True, width=110)
    D[cid] = {"text": t}
ids = list(D)
raw = {}
norm = {}
for c, x in D.items():
    # Remove Markdown headings; YAML field content, names and numbers remain.
    t = "\n".join(s for s in x["text"].splitlines() if not s.lstrip().startswith("#"))
    words = re.findall(r"[a-z]+|\d+", t.lower())
    norm[c] = " ".join(words)
    raw[c] = set(zip(*(words[i:] for i in range(5)), strict=False))
freq = collections.Counter(s for ss in raw.values() for s in ss)
filtered = {c: {s for s in ss if freq[s] <= 12} for c, ss in raw.items()}
nearest = {c: [] for c in ids}
pairs = []
for i, a in enumerate(ids):
    for b in ids[i + 1 :]:
        inter = len(raw[a] & raw[b])
        union = len(raw[a]) + len(raw[b]) - inter
        r = inter / union if union else 0
        fi = len(filtered[a] & filtered[b])
        fu = len(filtered[a]) + len(filtered[b]) - fi
        f = fi / fu if fu else 0
        row = {
            "a": a,
            "b": b,
            "raw_fivegram_jaccard": round(r, 5),
            "filtered_fivegram_jaccard": round(f, 5),
            "same_domain": a[:2] == b[:2],
        }
        pairs.append(row)
        nearest[a].append({**row, "other": b})
        nearest[b].append({**row, "other": a})
for c, v in nearest.items():
    v.sort(key=lambda r: r["filtered_fivegram_jaccard"], reverse=True)
    nearest[c] = v[:3]
byhash = collections.defaultdict(list)
for c, t in norm.items():
    byhash[hashlib.sha256(t.encode()).hexdigest()].append(c)
pairs.sort(key=lambda r: r["filtered_fivegram_jaccard"], reverse=True)
out = {
    "method": (
        "Lowercase alphanumeric token five-gram Jaccard. Filtered sets exclude five-grams "
        "occurring in more than twelve primary records. Headings removed; names and numeric "
        "case inputs retained. Screening only: no authorship, plagiarism, semantic originality "
        "or quality conclusion follows from a threshold."
    ),
    "exact_normalized_body_duplicates": [v for v in byhash.values() if len(v) > 1],
    "pair_count": len(pairs),
    "pairs": pairs[:100],
    "cross_domain_pairs": [r for r in pairs if not r["same_domain"]][:50],
    "nearest": nearest,
}
(E / "similarity.json").write_text(json.dumps(out, indent=2) + "\n")
print(
    "Compared",
    len(pairs),
    "pairs; exact normalized duplicate groups:",
    len(out["exact_normalized_body_duplicates"]),
)
