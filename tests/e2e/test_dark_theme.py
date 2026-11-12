"""Real computed dark colors and native interaction, not a human accessibility signoff."""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from growth.services.assessment import persist_assessment_run
from tests.e2e.test_application_consistency import audit_page
from tests.e2e.test_core_flow import create_browser_user, log_in, seed_browser_data
from tests.test_assessment_integration import golden_payload
from tests.test_dark_theme import contrast

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def colors(locator):
    return locator.evaluate("""element => {
      const s = getComputedStyle(element);
      return { color: s.color, background: s.backgroundColor,
        border: s.borderTopColor, outline: s.outlineColor, style: s.outlineStyle };
    }""")


def hex_color(rgb):
    import re

    channels = re.fullmatch(r"rgb\((\d+), (\d+), (\d+)\)", rgb)
    assert channels, rgb
    return "#" + "".join(f"{int(value):02x}" for value in channels.groups())


def assert_dark(page):
    expect(page.locator('meta[name="color-scheme"]')).to_have_attribute("content", "dark")
    assert page.locator("html").evaluate("e => getComputedStyle(e).colorScheme") == "dark"
    root = colors(page.locator("html"))
    assert hex_color(root["background"]) == "#081114"
    assert contrast(hex_color(root["color"]), hex_color(root["background"])) >= 4.5
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")


def capture(page, state, width):
    assert_dark(page)
    audit_page(page)
    folder = Path("test-results/pilot-walkthrough")
    folder.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=folder / f"dark-{state}-{width}.png", full_page=True)


@pytest.mark.parametrize("width", [390, 1280])
def test_dark_native_fields_errors_dialogs_and_routes(live_server, page, width):
    user = create_browser_user()
    seed_browser_data()
    persist_assessment_run(user, golden_payload())
    page.set_viewport_size({"width": width, "height": 900})
    # Deliberately emulate a light OS preference: the requested default is dark.
    page.emulate_media(color_scheme="light", reduced_motion="reduce")
    page.goto(live_server.url + "/accounts/login/")
    field = page.get_by_label("Username", exact=True)
    palette = colors(field)
    assert hex_color(palette["background"]) == "#142328"
    assert contrast(hex_color(palette["color"]), hex_color(palette["background"])) >= 4.5
    assert contrast(hex_color(palette["border"]), hex_color(palette["background"])) >= 3
    page.keyboard.press("Tab")
    field.focus()
    focused = colors(field)
    assert focused["style"] == "solid"
    assert contrast(hex_color(focused["outline"]), hex_color(palette["background"])) >= 3
    primary = colors(page.get_by_role("button", name="Sign in", exact=True))
    assert hex_color(primary["background"]) == "#e6ad4b"
    assert contrast(hex_color(primary["color"]), hex_color(primary["background"])) >= 4.5
    capture(page, "login", width)
    field.fill("missing-synthetic-account")
    page.get_by_label("Password", exact=True).fill("Wrong-password-83947!")
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.locator(".form-error")).to_be_visible()
    error = colors(page.locator(".form-error"))
    assert contrast(hex_color(error["color"]), hex_color(error["background"])) >= 4.5
    capture(page, "login-error", width)
    log_in(live_server, page)
    for state, path in (
        ("home", "/"),
        ("personal-os", "/personal-os/"),
        ("practices", "/practices/"),
        ("weekly", "/weekly/"),
        ("account", "/account/data/"),
        ("profile", "/profile/"),
    ):
        page.goto(live_server.url + path)
        capture(page, state, width)
    share = page.get_by_role("button", name="Share", exact=True)
    share.focus()
    page.keyboard.press("Enter")
    dialog = page.get_by_role("dialog", name="Share assessment results")
    expect(dialog).to_be_visible()
    modal = colors(dialog)
    assert hex_color(modal["background"]) == "#0d181c"
    assert contrast(hex_color(modal["color"]), hex_color(modal["background"])) >= 4.5
    code = colors(page.get_by_label("Assessment share code"))
    assert hex_color(code["background"]) == "#142328"
    capture(page, "share", width)
    page.keyboard.press("Escape")
    expect(share).to_be_focused()
    page.goto(live_server.url + "/account/data/")
    danger = colors(page.get_by_role("button", name="Permanently delete account", exact=True))
    assert hex_color(danger["background"]) == "#e17555"
    assert contrast(hex_color(danger["color"]), hex_color(danger["background"])) >= 4.5
    # Native system high contrast remains in charge; no forced brand colors.
    page.emulate_media(forced_colors="active")
    expect(
        page.get_by_role("button", name="Permanently delete account", exact=True)
    ).to_be_visible()
    assert (
        page.locator(".button").first.evaluate("e => getComputedStyle(e).forcedColorAdjust")
        == "auto"
    )
