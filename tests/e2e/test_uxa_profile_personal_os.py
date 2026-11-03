from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from growth.services.assessment import persist_assessment_run
from growth.services.canonical_import import seed_canonical_data
from tests.test_assessment_integration import golden_payload

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def capture(page, name, width):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    folder = Path("test-results/pilot-walkthrough")
    folder.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=folder / f"uxa-{name}-{width}.png", full_page=True)


@pytest.mark.parametrize("width", [390, 1280])
def test_profile_help_and_guided_personal_os(live_server, page, width):
    user = get_user_model().objects.create_user(
        username=f"guided-{width}", password="Guided-Flow-2048!"
    )
    seed_canonical_data()
    page.set_viewport_size({"width": width, "height": 1000})
    page.goto(live_server.url + "/accounts/login/")
    page.get_by_label("Username").fill(user.username)
    page.get_by_label("Password", exact=True).fill("Guided-Flow-2048!")
    page.get_by_role("button", name="Sign in").click()
    page.goto(live_server.url + "/profile/")
    expect(page.get_by_role("heading", name="Your starting point and progress")).to_be_visible()
    expect(page.locator("#current-state-heading")).to_have_count(0)
    help_control = page.locator(".inline-help summary").first
    help_control.focus()
    page.keyboard.press("Enter")
    expect(page.locator(".inline-help[open]").first).to_be_visible()
    capture(page, "profile-help", width)
    page.keyboard.press("Escape")
    expect(page.locator(".inline-help[open]")).to_have_count(0)

    page.goto(live_server.url + "/personal-os/")
    expect(page.locator(".reflection-fieldset:visible")).to_have_count(1)
    page.locator("#id_mission_state").select_option("provided")
    page.locator("#id_mission_value").fill("Make more time for my family")
    capture(page, "personal-os-fillout", width)
    for _ in range(8):
        page.get_by_role("button", name="Next question", exact=True).click()
        expect(page.locator(".reflection-fieldset:visible")).to_have_count(1)
    page.get_by_role("button", name="Save Personal OS revision", exact=True).click()
    expect(page.get_by_role("heading", name="Your current direction")).to_be_visible()
    expect(page.get_by_text("Make more time for my family", exact=True)).to_be_visible()
    expect(page.locator(".personal-os-form")).to_have_count(0)
    capture(page, "personal-os-summary", width)
    page.get_by_role("link", name="Review or change your answers").click()
    expect(page.locator("#id_mission_value")).to_have_value("Make more time for my family")
    capture(page, "personal-os-revision", width)
    run, _ = persist_assessment_run(user, golden_payload())
    assert run.original_share_code
    page.goto(live_server.url + "/profile/")
    share = page.get_by_role("button", name="Share", exact=True)
    expect(page.locator("#profile-share")).not_to_be_visible()
    share.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("dialog", name="Share assessment results")).to_be_visible()
    expect(page.get_by_label("Assessment share code")).to_have_value(run.original_share_code)
    capture(page, "profile-share", width)
    page.keyboard.press("Escape")
    expect(page.locator("#profile-share")).not_to_be_visible()
    expect(share).to_be_focused()
    page.goto(live_server.url + "/personal-os/")
    expect(page.get_by_text("Make more time for my family", exact=True)).to_have_count(0)
    page.get_by_role("link", name="Review earlier choices from", exact=False).click()
    assert "/history/?reuse=" in page.url
    capture(page, "personal-os-reuse", width)
    page.get_by_label("Mission", exact=True).check()
    page.get_by_role("button", name="Preview selected intentions").click()
    page.get_by_role("button", name="Confirm selected intentions").click()
    expect(page.get_by_text("Make more time for my family", exact=True)).to_be_visible()
    page.goto(live_server.url + "/personal-os/practices/")
    assert page.url.startswith(live_server.url + "/practices/")
