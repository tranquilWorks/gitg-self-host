from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from growth.services.canonical_import import seed_canonical_data


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [1280, 390])
def test_guided_entry_search_and_keyboard_pagination(live_server, page, width):
    get_user_model().objects.create_user(username="explorer", password="Explorer-Test-2047!")
    seed_canonical_data()
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(live_server.url + "/")
    page.get_by_label("Username").fill("explorer")
    page.get_by_label("Password").fill("Explorer-Test-2047!")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Make room for what matters.")).to_be_visible()
    expect(page.get_by_text("You are exploring a demonstration profile.")).to_be_visible()
    expect(page.get_by_role("link", name="Start my own assessment")).to_be_visible()
    artifacts = Path(__file__).resolve().parents[2] / "test-results/pilot-walkthrough"
    artifacts.mkdir(parents=True, exist_ok=True)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"guided-home-{width}.png", full_page=True)

    page.get_by_role("link", name="Practices", exact=True).click()
    expect(page.locator("#practice-suggestions .practice-card")).to_have_count(3)
    expect(page.locator("#practice-results")).to_have_count(0)
    page.get_by_label("Area of life").select_option("10")
    page.get_by_role("button", name="Find practices").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#practice-results .practice-card")).to_have_count(12)
    expect(page.get_by_text("Page 1 of 2", exact=True)).to_be_visible()
    page.get_by_role("link", name="Next page", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.locator("#practice-results .practice-card")).to_have_count(2)
    expect(page.get_by_label("Area of life")).to_have_value("10")
    expect(page.get_by_text("Page 2 of 2", exact=True)).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"guided-explorer-{width}.png", full_page=True)

    page.get_by_label("Search practices").fill("10.12")
    page.get_by_role("button", name="Find practices").click()
    expect(page.locator("#practice-results .practice-card")).to_have_count(1)
    page.locator("#practice-results").get_by_role(
        "link", name="Review practice", exact=True
    ).click()
    expect(page.get_by_role("link", name="Start guided setup")).to_be_visible()
    page.go_back()
    page.get_by_label("Search practices").fill("no matching synthetic topic")
    page.get_by_role("button", name="Find practices").click()
    expect(page.get_by_role("heading", name="No matching practices")).to_be_visible()
    page.get_by_role("link", name="Clear filters and browse all practices").click()
    expect(page.get_by_text("Page 1 of 32", exact=True)).to_be_visible()
    expect(page.get_by_label("Search practices")).to_have_value("")
    expect(page.get_by_label("Area of life")).to_have_value("")
