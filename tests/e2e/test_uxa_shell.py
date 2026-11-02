from pathlib import Path

import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [390, 1280])
def test_public_signup_policy_and_keyboard_help(live_server, page, width):
    page.set_viewport_size({"width": width, "height": 844})
    page.goto(live_server.url + "/accounts/login/")
    page.get_by_role("link", name="Create account", exact=True).click()
    page.get_by_label("Username:", exact=True).fill(f"new-{width}")
    page.get_by_label("Password:", exact=True).fill("Unrelated-phrase-83947!")
    page.get_by_label("Password confirmation:", exact=True).fill("Unrelated-phrase-83947!")
    page.get_by_role("button", name="Create account", exact=True).click()
    expect(page.get_by_role("heading", name="Sign in", exact=True)).to_be_visible()
    page.get_by_role("link", name="Disclaimer / Data Policy", exact=True).focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("heading", name="Disclaimer / Data Policy", exact=True)).to_be_visible()
    help_control = page.locator(".inline-help summary")
    help_control.focus()
    page.keyboard.press("Enter")
    expect(page.locator(".inline-help")).to_have_attribute("open", "")
    page.keyboard.press("Escape")
    expect(page.locator(".inline-help")).not_to_have_attribute("open", "")
    expect(help_control).to_be_focused()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    artifacts = Path("test-results/pilot-walkthrough")
    artifacts.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=artifacts / f"uxa-policy-{width}.png", full_page=True)
