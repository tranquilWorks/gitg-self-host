from datetime import date
from pathlib import Path

import pytest
from playwright.sync_api import expect

from growth.models import PracticeProtocol, PracticeSprint, WeeklyExecutionReview
from growth.services.practice import start_practice
from tests.e2e.test_core_flow import create_browser_user, log_in, seed_browser_data

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("width", [390, 1280])
def test_weekly_through_real_closeout_and_next_practice(live_server, page, width):
    user = create_browser_user()
    seed_browser_data()
    page.set_viewport_size({"width": width, "height": 950})
    log_in(live_server, page)

    def capture(state):
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        folder = Path("test-results/pilot-walkthrough")
        folder.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=folder / f"uxa-weekly-{state}-{width}.png", full_page=True)

    page.goto(live_server.url + "/weekly/")
    expect(page.get_by_role("heading", name="No direction yet")).to_be_visible()
    expect(page.get_by_role("link", name="Set direction")).to_be_visible()
    capture("no-direction")
    sprint = start_practice(
        user=user,
        protocol=PracticeProtocol.objects.get(stable_id="PRACTICE-FRIENDSHIP-01"),
        person_or_context="Synthetic weekly friend",
        start_date=date.today(),
    )
    page.goto(live_server.url + f"/practice-sprints/{sprint.pk}/")
    expect(page.get_by_role("button", name="Open final review")).to_be_disabled()
    gate = page.locator('[tabindex="0"][aria-describedby="closeout-requirements"]')
    gate.focus()
    expect(gate).to_be_focused()
    expect(page.locator("#closeout-requirements")).to_contain_text("Complete at least")
    capture("gate")
    page.goto(live_server.url + "/weekly/")
    page.get_by_role("link", name="Create a weekly plan").click()
    capture("no-plan")
    page.get_by_label("Which day?", exact=True).fill(date.today().isoformat())
    page.get_by_role("button", name="Save weekly plan", exact=True).click()
    expect(page.get_by_text("Selected", exact=True)).to_be_visible()
    capture("planned")
    first, second, _ = sprint.protocol.actions.order_by("sequence")
    for action in (first, second):
        page.goto(
            live_server.url + f"/practice-sprints/{sprint.pk}/check-ins/new/?action={action.pk}"
        )
        page.get_by_label("I tried this action", exact=True).check()
        page.get_by_label("I completed this action", exact=True).check()
        if action == first:
            page.get_by_label("The interaction moved beyond logistics or small talk").check()
            page.get_by_label("Meaningful information was freely shared").check()
        else:
            page.get_by_label("A specific future interaction was mutually scheduled").check()
            page.get_by_label(
                "How does this setting compare with earlier check-ins?"
            ).select_option("same_context")
        page.get_by_label("How much support did you use?").select_option("independent")
        page.get_by_label("Did this go as you expected?").select_option("supports")
        page.get_by_role("button", name="Submit check-in", exact=True).click()
        expect(
            page.get_by_text("Check-in submitted and added to evidence history.")
        ).to_be_visible()
    assert sprint.check_ins.filter(status="submitted", action_completed=True).count() == 2
    page.goto(live_server.url + "/weekly/")
    expect(page.get_by_text("It went as expected", exact=True)).to_be_visible()
    capture("proof")
    page.get_by_role("button", name="Save proof-based weekly review").click()
    expect(page.get_by_role("heading", name="Your next step")).to_be_visible()
    review = WeeklyExecutionReview.objects.get()
    frozen = review.canonical_snapshot
    capture("reviewed")
    page.goto(live_server.url + f"/practice-sprints/{sprint.pk}/")
    page.get_by_role("link", name="Open final review", exact=True).click()
    page.get_by_label("What did this practice show you?").fill("Synthetic bounded learning.")
    page.get_by_role("button", name="Submit final review and record 75% credit").click()
    expect(page.get_by_role("heading", name="Your practice is complete.")).to_be_visible()
    capture("complete")
    assert PracticeSprint.objects.get(pk=sprint.pk).status == "completed"
    for path, state in (
        ("/", "home"),
        ("/weekly/", "completed"),
        ("/profile/", "profile"),
        ("/practices/", "browser"),
    ):
        page.goto(live_server.url + path)
        expect(page.locator("#current-practice-heading")).to_have_count(0)
        assert "Find a starting point" not in page.locator("main").inner_text()
        capture(state)
    page.goto(live_server.url + "/weekly/")
    page.get_by_role("link", name="Act on your review").click()
    expect(page.get_by_role("link", name="Choose your next practice", exact=True)).to_be_visible()
    expect(page.get_by_text("No submitted proof for this plan", exact=True)).to_have_count(0)
    review.refresh_from_db()
    assert review.canonical_snapshot == frozen
