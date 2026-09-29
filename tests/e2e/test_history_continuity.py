import pytest
from playwright.sync_api import expect

from growth.models import PersonalOSRevision
from growth.services.assessment import persist_assessment_run
from growth.services.practice import transition_sprint
from growth.services.weekly_followup import save_plan_review
from tests.e2e.test_core_flow import (
    assert_no_horizontal_overflow,
    create_browser_user,
    log_in,
    save_walkthrough_screenshot,
    seed_browser_data,
)
from tests.test_assessment_integration import golden_payload
from tests.test_history_continuity import save_intentions
from tests.test_weekly_execution import _sprint
from tests.test_weekly_followup import plan_for


@pytest.mark.e2e
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("width", [390, 1280])
def test_history_reuse_and_old_practice_continuity(live_server, page, width):
    page.set_viewport_size({"width": width, "height": 1000})
    user = create_browser_user()
    seed_browser_data()
    sprint = _sprint(user)
    source = sprint.assessment_run
    save_intentions(user, source, "Make time for deliberate learning")
    plan = plan_for(user, sprint)
    save_plan_review(user=user, plan=plan, next_step="continue_current", adjustment="timing")
    transition_sprint(sprint, "paused")
    target, _ = persist_assessment_run(user, golden_payload())
    log_in(live_server, page)
    if not page.get_by_role("link", name="Assessment", exact=True).is_visible():
        page.locator(".nav-more > summary").click()
    page.get_by_role("link", name="Assessment", exact=True).click()
    page.get_by_role("heading", name="What changes when you reassess").wait_for()
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"history-{width}-retake")
    page.get_by_role("link", name="History", exact=True).click()
    page.locator(f'a[href="/history/periods/{source.pk}/"]').click()
    page.get_by_text("Weekly plans and reviews", exact=True).wait_for()
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"history-{width}-period")
    page.get_by_role("link", name="Review selected intentions for reuse").click()
    expect(page.locator('input[type="checkbox"]:checked')).to_have_count(0)
    page.get_by_label("Mission", exact=True).check()
    page.get_by_label("Capacity", exact=True).check()
    page.get_by_role("button", name="Preview selected intentions").click()
    assert not PersonalOSRevision.objects.filter(assessment_run=target).exists()
    page.get_by_role("heading", name="Review the exact changes").wait_for()
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"history-{width}-preview")
    page.get_by_role("button", name="Confirm selected intentions").click()
    expect(
        page.get_by_text(
            "Selected intentions saved for your current assessment period.", exact=False
        )
    ).to_be_visible()
    assert (
        PersonalOSRevision.objects.get(assessment_run=target).mission_value
        == "Make time for deliberate learning"
    )
    page.goto(f"{live_server.url}/history/plans/{plan.pk}/")
    page.get_by_text("Saved review choice", exact=True).wait_for()
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"history-{width}-proof")
    page.get_by_role("link", name="Open original practice").click()
    page.get_by_text(
        "This practice belongs to an earlier assessment period.", exact=True
    ).wait_for()
    expect(page.get_by_role("button", name="Resume practice", exact=True)).to_be_visible()
    assert_no_horizontal_overflow(page)
    save_walkthrough_screenshot(page, f"history-{width}-older-practice")
    page.get_by_role("button", name="Stop practice", exact=True).click()
    sprint.refresh_from_db()
    assert sprint.status == "stopped"
    expect(page.get_by_text("This attempt is stopped.", exact=False)).to_be_visible()
    assert sprint.assessment_run_id == source.pk
