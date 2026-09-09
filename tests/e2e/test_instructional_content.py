import copy
from pathlib import Path

import pytest
import yaml
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from growth.domain.practice_content import load_practice_content_bundle
from growth.services.canonical_import import _seed_protocols, seed_canonical_data

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [1280, 390])
def test_learning_guide_keyboard_mobile_and_separate_reveal(live_server, page, width):
    get_user_model().objects.create_user(username="guide-reader", password="Guide-Test-2047!")
    seed_canonical_data()
    guide = yaml.safe_load((ROOT / "docs/authoring/exercises/10.yaml").read_text())["exercises"][
        "10.01"
    ]["instructional_content"]
    runtime = copy.deepcopy(load_practice_content_bundle(ROOT).runtime_protocols)
    chosen = next(p for p in runtime if p["parent_competency_id"] == "10.01")
    chosen["setup_copy"]["instructional_content"] = guide
    _seed_protocols(runtime)
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(live_server.url + "/")
    page.get_by_label("Username").fill("guide-reader")
    page.get_by_label("Password").fill("Guide-Test-2047!")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url(live_server.url + "/")
    page.goto(f"{live_server.url}/practices/{chosen['slug']}/guide/")
    expect(page.get_by_role("heading", level=1)).to_have_text(guide["title"])
    assert "2, 5 and 11" not in page.content()
    prompt = page.get_by_role("link", name="Open Delayed recall and new application", exact=True)
    prompt.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name="Delayed recall and new application")).to_be_visible()
    assert "mean 6 minutes" not in page.content()
    assert "Worked example: an even set" not in page.content()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    artifacts = ROOT / "test-results/pilot-walkthrough"
    artifacts.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=artifacts / f"m6k-guide-prompt-{width}.png", full_page=True)
    reveal = page.get_by_role("link", name="Reveal check for Delayed recall and new application")
    reveal.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name="Check the delayed application")).to_be_visible()
    assert "mean 6 minutes" in page.content()
    page.evaluate("document.documentElement.style.fontSize = '200%'")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"m6k-guide-check-zoom-{width}.png", full_page=True)


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [1280, 390])
@pytest.mark.parametrize(
    "competency_id,prompt_id,key_id,hidden_phrase",
    [
        ("10.12", "corrected-attempt", "corrected-attempt-key", "disparity decreases"),
        ("10.13", "correction-prompt", "correction-key", "D1 violates scope"),
        ("10.14", "adapted-attempt", "adapted-attempt-key", "R1 substitutes"),
    ],
)
def test_guided_learning_compiled_keyboard_and_mobile_reveal(
    live_server, page, width, competency_id, prompt_id, key_id, hidden_phrase
):
    from growth.models import PracticeProtocol

    get_user_model().objects.create_user(username="guided-reader", password="Guide-Test-2047!")
    seed_canonical_data()
    protocol = PracticeProtocol.objects.get(parent_competency_id=competency_id)
    guide = protocol.setup_copy["instructional_content"]
    prompt = next(row for row in guide["sections"] if row["id"] == prompt_id)
    key = next(row for row in guide["checks"] if row["id"] == key_id)
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(live_server.url + "/")
    page.get_by_label("Username").fill("guided-reader")
    page.get_by_label("Password").fill("Guide-Test-2047!")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url(live_server.url + "/")
    page.goto(f"{live_server.url}/practices/{protocol.slug}/guide/")
    expect(page.get_by_role("heading", level=1)).to_have_text(guide["title"])
    assert hidden_phrase not in page.content()
    page.get_by_role("link", name=f"Open {prompt['title']}", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name=prompt["title"], exact=True)).to_be_visible()
    assert hidden_phrase not in page.content()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    artifacts = ROOT / "test-results/pilot-walkthrough"
    artifacts.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=artifacts / f"m6k-{competency_id}-prompt-{width}.png", full_page=True)
    page.get_by_role("link", name=f"Reveal check for {prompt['title']}", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name=key["title"], exact=True)).to_be_visible()
    assert hidden_phrase in page.content()
    page.evaluate("document.documentElement.style.fontSize = '200%'")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"m6k-{competency_id}-check-{width}.png", full_page=True)
