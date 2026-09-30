from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from growth.models import PracticeContext
from growth.services.canonical_import import seed_canonical_data


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [1280, 390])
def test_partial_fit_defer_explore_and_reconsider(live_server, page, width):
    get_user_model().objects.create_user(username="context-reviewer", password="Context-Test-2050!")
    seed_canonical_data()
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(live_server.url + "/personal-os/practices/")
    page.get_by_label("Username").fill("context-reviewer")
    page.get_by_label("Password").fill("Context-Test-2050!")
    page.get_by_role("button", name="Sign in").click()
    expect(page.locator("#context-shortlist .panel")).to_have_count(3)
    page.locator("#context-shortlist").get_by_role("link", name="Review current fit").first.click()
    context_url = page.url
    expect(page.get_by_label("Review a little at a time")).to_be_checked()
    page.get_by_label("Fit with your present role and situation").select_option("0")
    page.get_by_role("button", name="Save practice context").click()
    expect(page.get_by_label("Fit with your present role and situation")).to_have_value("0")
    expect(page.get_by_label("Current importance among competing goods")).to_have_value("")
    assert PracticeContext.objects.get().importance_state == "unknown"
    page.get_by_text("2. Is now a workable time?", exact=True).focus()
    page.keyboard.press("Enter")
    page.get_by_label("Readiness to attempt this bounded practice").select_option("2")
    page.get_by_role("button", name="Save practice context").click()
    expect(page.get_by_label("Readiness to attempt this bounded practice")).to_have_value("2")
    assert PracticeContext.objects.count() == 2
    artifacts = Path(__file__).resolve().parents[2] / "test-results/pilot-walkthrough"
    artifacts.mkdir(parents=True, exist_ok=True)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"context-partial-{width}.png", full_page=True)

    # Switching modes omits inactive fields; previously entered numbers cannot
    # obstruct an explicit deferral, and switching back preserves the form controls.
    page.get_by_label("Defer this practice for now").check()
    page.get_by_label("Which factor is deferred?").select_option("readiness")
    page.get_by_label("Reason for deferring").select_option("timing")
    page.get_by_label("Optional review horizon in days").fill("7")
    page.get_by_role("button", name="Save practice context").click()
    page.get_by_role("button", name="Request alternative").click()
    page.get_by_role("link", name="Explore another practice").click()
    expect(page.locator("#practice-results .practice-card")).to_have_count(12)
    assert PracticeContext.objects.count() == 3

    page.goto(live_server.url + "/personal-os/practices/")
    expect(page.locator("#saved-context .panel")).to_have_count(1)
    expect(page.locator("#context-shortlist .panel")).to_have_count(2)
    expect(page.locator("#saved-context").get_by_text("Review on", exact=False)).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.screenshot(path=artifacts / f"context-deferred-{width}.png", full_page=True)
    page.get_by_role("link", name="Reconsider this choice").click()
    assert page.url == context_url
    assert PracticeContext.objects.count() == 3
    page.get_by_label("Review a little at a time").check()
    page.get_by_label("Fit with your present role and situation").select_option("3")
    page.get_by_role("button", name="Save practice context").click()
    assert PracticeContext.objects.count() == 4
    page.goto(live_server.url + "/personal-os/practices/")
    expect(page.locator("#saved-context .panel")).to_have_count(0)
