"""Compile explicit, per-competency source bundles into unscored learner guides.

No prose generation: teaching, prompts, keys and later packets retain their
authored text. Only navigation and document heading levels are adapted for HTML.
"""

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

from growth.domain.instructional_content import VERSION, validate_instructional_content

LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def resource_id(path: Path, directory: Path) -> str:
    return "file-" + re.sub(
        r"[^a-z0-9]+", "-", path.relative_to(directory).as_posix().lower()
    ).strip("-")


def load_companion_guides(root: Path) -> dict[str, dict]:
    sources = yaml.safe_load((root / "contracts/catalog-guide-sources.yaml").read_text())["sources"]
    guides = {}
    for cid, relative in sources.items():
        path = root / relative
        if (
            path.name != "learner-guide.md"
            or path.parent.name != cid
            or not path.resolve().is_relative_to((root / "docs/authoring").resolve())
        ):
            raise ValueError(f"{cid}: guide source must belong to its own competency folder")
        directory = path.parent
        source_register = directory.parent / "SOURCES.md"
        source_text = source_register.read_text()
        citations = list(
            dict.fromkeys(
                (label, url)
                for label, url in LINK.findall(source_text)
                if url.startswith(("https://", "http://"))
            )
        )
        linked_urls = {url for _, url in citations}
        for block in re.split(r"(?m)^## ", source_text)[1:]:
            for url in re.findall(r"https?://[^\s<>`\)]+", block):
                url = url.rstrip(".,;|")
                if url not in linked_urls:
                    citations.append((block.splitlines()[0].strip(), url))
                    linked_urls.add(url)
        if not citations:
            raise ValueError(f"{cid}: no source references found")
        resources = [
            {
                "id": "sources",
                "title": "Sources and further reading",
                "body": "These references support the bounded concepts described in the guide. "
                "They do not validate the fictional case or establish personal results.\n\n"
                + "\n".join(f"- [{label}]({url})" for label, url in citations),
            },
        ]
        # Author maps remain in the source tree. The learner scope is already
        # explained in the guide; resolve old map links back to that explanation.
        destinations = {
            path.resolve(): "?",
            (directory / "check-prompts.md").resolve(): "?attempt=practice-checks",
            (directory / "check-answers.md").resolve(): "?check=practice-answers",
            (directory / "SCOPE-MAP.md").resolve(): "?",
            source_register.resolve(): "?resource=sources",
        }
        extra = sorted(
            p
            for p in directory.rglob("*")
            if p.is_file()
            and p.name
            not in {"learner-guide.md", "check-prompts.md", "check-answers.md", "SCOPE-MAP.md"}
        )
        for item in extra:
            destinations[item.resolve()] = "?resource=" + resource_id(item, directory)

        def body(
            file: Path,
            source_register=source_register,
            source_text=source_text,
            destinations=destinations,
        ) -> str:
            raw = file.read_text()
            if file.suffix == ".txt":
                return "```text\n" + raw.rstrip() + "\n```"

            def link(match):
                label, target = match.groups()
                parsed = urlsplit(target)
                if parsed.scheme in {"https", "http"}:
                    return match.group()
                if parsed.scheme or parsed.netloc:
                    raise ValueError(f"{file}: unsupported link {target}")
                resolved = (file.parent / unquote(parsed.path)).resolve()
                if resolved.name == "SCOPE-MAP.md" and resolved in destinations:
                    return "scope and limits described in this guide"
                if resolved == source_register.resolve() and parsed.fragment:
                    heading = re.search(
                        r"^##\s+" + re.escape(parsed.fragment) + r"\b(.*?)(?=^##\s|\Z)",
                        source_text,
                        flags=re.M | re.S | re.I,
                    )
                    candidates = LINK.findall(heading.group(1)) if heading else []
                    if not candidates:
                        raise ValueError(f"{file}: missing citation {target}")
                    return f"[{label}]({candidates[0][1]})"
                if resolved not in destinations:
                    raise ValueError(f"{file}: unmapped learner link {target}")
                return f"[{label}]({destinations[resolved]})"

            raw = LINK.sub(link, raw)
            # One page title is supplied by the template; internal headings
            # start below the section heading rather than introducing extra h1s.
            raw = re.sub(r"\A# [^\n]+\n+", "", raw)
            raw = re.sub(r"^(#{2,5}) ", r"\1# ", raw, flags=re.M)
            return raw.strip()

        for item in extra:
            title = item.stem.replace("-", " ").capitalize()
            resources.append(
                {"id": resource_id(item, directory), "title": title, "body": body(item)}
            )
        guide = {
            "schema_version": VERSION,
            "competency_id": cid,
            "title": path.read_text().splitlines()[0].removeprefix("# "),
            "scored": False,
            "body_format": "markdown",
            "resources": resources,
            "sections": [
                {"id": "teaching", "kind": "concept", "title": "Learn and try", "body": body(path)},
                {
                    "id": "practice-checks",
                    "kind": "prompt",
                    "title": "Practice checks",
                    "body": body(directory / "check-prompts.md"),
                    "check_id": "practice-answers",
                    "attempt_mode": "practice",
                },
            ],
            "checks": [
                {
                    "id": "practice-answers",
                    "title": "Compare your responses",
                    "body": body(directory / "check-answers.md"),
                    "criteria": [
                        "Compare each saved response with its matching explanation; "
                        "keep revisions separate from your initial attempt."
                    ],
                }
            ],
        }
        validate_instructional_content(guide, cid)
        guides[cid] = guide
    return guides


def compact_guide(cid: str, exercise: dict) -> dict:
    """Expose an adequate compact exercise without inventing new checks."""
    return {
        "schema_version": VERSION,
        "competency_id": cid,
        "title": exercise["title"],
        "scored": False,
        "sections": [
            {
                "id": "prepare",
                "kind": "concept",
                "title": "Prepare",
                "body": "\n\n".join(
                    exercise[k] for k in ("goal", "setup", "scope_note", "burden", "adaptation")
                ),
            }
        ]
        + [
            {
                "id": f"action-{i}",
                "kind": "pathway",
                "title": row["title"],
                "body": row["instructions"],
            }
            for i, row in enumerate(exercise["actions"], 1)
        ]
        + [{"id": "review", "kind": "next_step", "title": "Review", "body": exercise["review"]}],
        "checks": [],
    }
