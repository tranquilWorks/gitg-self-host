from datetime import date, timedelta

import pytest
from playwright.sync_api import expect

from growth.models import EvidenceEvent, PracticeProtocol, WeeklyExecutionPlan
from growth.services.practice import start_practice
from growth.services.weekly_execution import (
    current_window,
    record_weekly_plan,
    record_weekly_review,
)
from tests.e2e.test_core_flow import (
    assert_no_horizontal_overflow,
    create_browser_user,
    log_in,
    save_walkthrough_screenshot,
    seed_browser_data,
)


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [390, 1280])
def test_weekly_recovery_calendar_and_explicit_pause(live_server, page, width):
    page.set_viewport_size({"width": width, "height": 950})
    user = create_browser_user()
    seed_browser_data()
    sprint = start_practice(
        user=user,
        protocol=PracticeProtocol.objects.get(stable_id="PRACTICE-FRIENDSHIP-01"),
        person_or_context="Private calendar exclusion sentinel",
        start_date=date.today(),
    )
    day = date.today() - timedelta(weeks=2)
    plan = record_weekly_plan(
        user=user,
        assessment_run=sprint.assessment_run,
        sprint=sprint,
        action=sprint.protocol.actions.order_by("sequence").first(),
        week_start=current_window(today=day)[0],
        intended_on=day,
        today=day,
    ).plan
    record_weekly_review(user=user, plan=plan, next_step="plan_next_action", adjustment="timing")
    log_in(live_server, page)
    page.goto(f"{live_server.url}/weekly/")
    page.get_by_role("heading", name="Carry forward what you learned").wait_for()
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"weekly-followup-{width}-previous")
    page.get_by_role("link", name="Open previous plan and next step").click()
    page.get_by_role("link", name="Choose the next action", exact=True).click()
    assert WeeklyExecutionPlan.objects.count() == 1
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"weekly-followup-{width}-replan")
    page.get_by_role("button", name="Save replanned action").click()
    expect(page.get_by_text("This week's plan is saved.", exact=False)).to_be_visible()
    assert WeeklyExecutionPlan.objects.count() == 2
    with page.expect_download() as download_info:
        page.get_by_role("link", name="Download calendar entry").click()
    assert download_info.value.suggested_filename.endswith(".ics")
    page.get_by_label("Pause and reconsider").check()
    page.get_by_role("button", name="Save proof-based weekly review").click()
    page.get_by_role("link", name="Review pause", exact=True).click()
    sprint.refresh_from_db()
    assert sprint.status == "active"
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"weekly-followup-{width}-confirm")
    page.get_by_role("button", name="Confirm pause", exact=True).click()
    page.get_by_role("link", name="Open current practice", exact=True).wait_for()
    sprint.refresh_from_db()
    assert sprint.status == "paused"
    assert EvidenceEvent.objects.count() == 0
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"weekly-followup-{width}-paused")
