import copy
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml
from django.urls import reverse
from markdown_it import MarkdownIt

from growth.domain.instructional_content import learner_projection, render_text
from growth.domain.practice_content import load_practice_content_bundle
from growth.models import CompletionCreditEvent, EvidenceEvent, PracticeProtocol, PracticeSprint
from growth.templatetags.instructional import guide_body
from growth.views_instructional import guide_for_protocol
from scripts.catalog_learning_guides import load_companion_guides

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "source",
    [
        "docs/authoring/emotional-foundations/07.02/learner-guide.md",
        "docs/authoring/emotional-foundations/07.01/check-answers.md",
        "outside/07.01/learner-guide.md",
    ],
)
def test_competency_source_mapping_rejects_foreign_lesson_or_answer_as_teaching(tmp_path, source):
    (tmp_path / "contracts").mkdir()
    (tmp_path / "contracts/catalog-guide-sources.yaml").write_text(
        yaml.safe_dump({"sources": {"07.01": source}})
    )
    with pytest.raises(ValueError, match="own competency folder"):
        load_companion_guides(tmp_path)


def test_every_companion_has_exact_prompt_key_resource_and_safe_navigation():
    guides = load_companion_guides(ROOT)
    assert len(guides) == 275
    for cid, guide in guides.items():
        initial = learner_projection(guide, cid)
        attempt = learner_projection(guide, cid, attempt="practice-checks")
        answer = guide["checks"][0]["body"]
        assert answer not in render_text(initial)
        assert answer not in render_text(attempt)
        assert answer in render_text(learner_projection(guide, cid, check="practice-answers"))
        assert guide["sections"][1]["body"] not in render_text(initial)
        for resource in guide["resources"]:
            assert resource["body"] not in render_text(initial)
            assert resource["body"] not in render_text(attempt)
            opened = learner_projection(guide, cid, resource=resource["id"])
            assert opened["sections"][0]["body"] == resource["body"]
            assert opened["check"] is None
        # Resolve every local link in every learner-visible body, including
        # secondary materials. No source-tree paths leak into app navigation.
        for row in guide["sections"] + guide["checks"] + guide["resources"]:
            for token in MarkdownIt("js-default").parse(row["body"]):
                for child in token.children or []:
                    if child.type != "link_open":
                        continue
                    target = child.attrGet("href")
                    parsed = urlsplit(target)
                    if parsed.scheme:
                        assert parsed.scheme in {"http", "https"}
                    else:
                        assert not parsed.path and not parsed.netloc
                        params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
                        learner_projection(guide, cid, **params)


def test_resources_fail_closed_and_do_not_modify_the_document():
    guide = load_companion_guides(ROOT)["07.01"]
    before = copy.deepcopy(guide)
    with pytest.raises(ValueError, match="Unknown"):
        learner_projection(guide, "07.01", resource="../check-answers.md")
    with pytest.raises(ValueError, match="only one"):
        learner_projection(guide, "07.01", attempt="practice-checks", resource="sources")
    projection = learner_projection(guide, "07.01", resource="sources")
    projection["sections"][0]["body"] = "Changed outside the source"
    assert guide == before


def test_markdown_renders_tables_and_rejects_executable_html_and_remote_images():
    html = guide_body(
        "| Fact | Meaning |\n| --- | --- |\n| A | **B** |\n\n"
        "<script>alert(1)</script>\n\n[x](javascript:alert(1))\n\n"
        "![tracking](https://example.com/pixel.png)",
        "markdown",
    )
    assert "<table>" in html and "<strong>B</strong>" in html
    assert "<script>" not in html and "<img" not in html and 'href="javascript:' not in html
    assert "&lt;script&gt;" in html


@pytest.mark.django_db
def test_all_383_guides_reach_authenticated_app_without_writing_evidence(client, user, seeded):
    bundle = load_practice_content_bundle(ROOT)
    assert len(bundle.protocols) == 383
    client.force_login(user)
    before = (
        EvidenceEvent.objects.count(),
        CompletionCreditEvent.objects.count(),
        PracticeSprint.objects.count(),
    )
    companions = load_companion_guides(ROOT)
    for protocol in PracticeProtocol.objects.all():
        guide = guide_for_protocol(protocol)
        assert guide and guide["competency_id"] == protocol.parent_competency_id
        url = reverse("growth:practice-guide", args=[protocol.slug])
        response = client.get(url)
        assert response.status_code == 200, protocol.parent_competency_id
        assert response["Cache-Control"] == "private, no-store"
        if protocol.parent_competency_id in companions:
            expected = companions[protocol.parent_competency_id]
            assert guide == expected
            response = client.get(url, {"attempt": "practice-checks", "format": "md"})
            assert response.status_code == 200
            assert expected["checks"][0]["body"] not in response.content.decode()
            checked = client.get(url, {"check": "practice-answers", "format": "md"})
            assert expected["checks"][0]["body"] in checked.content.decode()
            for resource in expected["resources"]:
                result = client.get(url, {"resource": resource["id"], "format": "md"})
                assert result.status_code == 200
                assert resource["body"] in result.content.decode()
            assert client.get(url, {"resource": "missing"}).status_code == 404
    assert before == (
        EvidenceEvent.objects.count(),
        CompletionCreditEvent.objects.count(),
        PracticeSprint.objects.count(),
    )
    assert PracticeProtocol.objects.count() == 383
    assert len(json.dumps(companions)) > 100000
