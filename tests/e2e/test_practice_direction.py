from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from playwright.sync_api import expect

from growth.models import PersonalOSRevision, PracticeDirectionRevision, PracticeProtocol
from growth.services.canonical_import import seed_canonical_data
from growth.services.practice import start_practice


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [1280, 390])
def test_choose_revise_and_review_direction(live_server, page, width):
    user = get_user_model().objects.create_user(
        username="direction-owner", password="Direction-Test-2050!"
    )
    seed_canonical_data()
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(live_server.url + "/personal-os/direction/")
    page.get_by_label("Username").fill("direction-owner")
    page.get_by_label("Password").fill("Direction-Test-2050!")
    page.get_by_role("button", name="Sign in").click()
    page.locator("#id_priority_stack_state").select_option("provided")
    page.locator("#id_priority_stack_value").fill(
        "Make time for friendship\nProtect quiet evenings"
    )
    page.get_by_role("button", name="Save direction review").click()
    expect(page.get_by_text("Direction review saved.", exact=True)).to_be_visible()
    protocol = PracticeProtocol.objects.get(slug="deepen-one-existing-friendship")
    page.goto(live_server.url + f"/practices/{protocol.slug}/setup/1/")
    page.get_by_role("link", name="Choose or revise the connection").click()
    page.get_by_label("What does this practice serve?").select_option("priority")
    page.get_by_label("Saved priority").select_option("0")
    page.get_by_role("button", name="Save connection").click()
    expect(page.get_by_text("Make time for friendship", exact=True)).to_be_visible()
    assert PracticeDirectionRevision.objects.get().state == "priority"
    artifacts = Path(__file__).resolve().parents[2] / "test-results/pilot-walkthrough"
    artifacts.mkdir(parents=True, exist_ok=True)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=artifacts / f"direction-setup-{width}.png", full_page=True)
    # Existing seven-step setup has separate full journey coverage. Here the
    # service starts the practice so this case isolates the new weekly connection.
    start_practice(
        user=user, protocol=protocol, person_or_context="A friend", start_date=timezone.localdate()
    )
    page.goto(live_server.url + "/weekly/")
    expect(page.get_by_role("heading", name="Current practice connection")).to_be_visible()
    page.get_by_role("link", name="Choose or revise the connection").click()
    page.get_by_label("What does this practice serve?").select_option("outcome")
    page.get_by_label("Intended outcome").fill("Arrange one relaxed catch-up")
    page.get_by_role("button", name="Save connection").click()
    expect(page.get_by_text("Arrange one relaxed catch-up", exact=True)).to_be_visible()
    page.get_by_role("link", name="Choose or revise the connection").click()
    page.get_by_label("What does this practice serve?").select_option("declined")
    page.get_by_role("button", name="Save connection").click()
    expect(page.get_by_text("You chose not to connect this practice", exact=False)).to_be_visible()
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=artifacts / f"direction-weekly-{width}.png", full_page=True)
    page.get_by_role("link", name="Choose or revise the connection").click()
    page.get_by_text("Choice 1 ·", exact=False).focus()
    page.keyboard.press("Enter")
    expect(
        page.locator(".stage-panel-body").get_by_text("Make time for friendship", exact=True)
    ).to_be_visible()
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=artifacts / f"direction-history-{width}.png", full_page=True)
    page.goto(live_server.url + "/personal-os/direction/")
    page.locator("#id_priority_stack_value").fill("A quieter season")
    page.get_by_role("button", name="Save direction review").click()
    page.get_by_text("Revision 1 ·", exact=False).click()
    expect(page.get_by_text("Protect quiet evenings", exact=True)).to_be_visible()
    assert PersonalOSRevision.objects.count() == 2
    assert PracticeDirectionRevision.objects.count() == 3
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=artifacts / f"direction-review-{width}.png", full_page=True)
