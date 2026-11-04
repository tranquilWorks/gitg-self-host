from datetime import date
from pathlib import Path

import pytest
from playwright.sync_api import expect

from growth.models import EvidenceEvent, PracticeSprint
from growth.services.evidence import build_privacy_safe_evidence_export, verify_evidence_event
from growth.services.practice import complete_with_review
from tests.e2e.test_core_flow import create_browser_user, log_in, seed_browser_data
from tests.test_composite_score_state import _submit

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def capture(page, name, width):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    folder = Path("test-results/pilot-walkthrough")
    folder.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=folder / f"uxa-{name}-{width}.png", full_page=True)


@pytest.mark.parametrize("width", [390, 1280])
def test_selected_attempt_stays_identical_and_readable(live_server, page, width):
    user = create_browser_user()
    seed_browser_data()
    page.set_viewport_size({"width": width, "height": 1000})
    log_in(live_server, page)
    page.goto(live_server.url + "/practices/?q=Deepen%20One%20Existing%20Friendship&browse=1")
    expect(page.locator("#practice-results .practice-card")).to_have_count(1)
    capture(page, "practices-filtered", width)
    page.locator("#practice-results").get_by_role(
        "link", name="Review practice", exact=True
    ).click()
    page.get_by_role("link", name="Start guided setup", exact=True).click()
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_label("Yes, this relationship is available").check()
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_label("Private label for the person or context").fill("SYNTHETIC friend")
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_role("checkbox").check()
    page.get_by_role("button", name="I understand and will respect these boundaries").click()
    expect(page.get_by_text("Plan the first 7 days", exact=False)).to_be_visible()
    page.get_by_label("Start date", exact=True).fill(date.today().isoformat())
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_role("button", name="I have reviewed the defined actions").click()
    page.get_by_role("button", name="Begin practice", exact=True).click()
    sprint = PracticeSprint.objects.get(user=user)
    attempt_url = live_server.url + f"/practice-sprints/{sprint.pk}/"
    assert page.url == attempt_url
    expect(page.locator("[data-attempt]")).to_have_attribute("data-protocol", sprint.protocol_id)
    capture(page, "practice-work", width)
    page.get_by_role("link", name="Learning guide and resources", exact=True).click()
    expect(
        page.get_by_role("link", name="Back to your current practice", exact=False)
    ).to_have_attribute("href", f"/practice-sprints/{sprint.pk}/")
    assert "/" + sprint.protocol.slug + "/guide/" in page.url
    expect(page.get_by_role("link", name="Teaching and materials")).to_have_count(0)
    capture(page, "practice-guide", width)
    page.get_by_role("link", name="Back to your current practice", exact=False).click()
    assert page.url == attempt_url
    page.goto(live_server.url + "/practices/?q=Deepen%20One%20Existing%20Friendship&browse=1")
    expect(page.locator("#browser-current-practice")).to_have_attribute(
        "data-attempt", str(sprint.pk)
    )
    expect(page.locator("#practice-results .practice-card")).to_have_attribute(
        "data-protocol", sprint.protocol_id
    )
    page.locator("#practice-results").get_by_role(
        "link", name="Open current practice", exact=True
    ).click()
    assert page.url == attempt_url
    capture(page, "practice-current", width)
    page.goto(live_server.url + "/weekly/")
    expect(page.locator('input[name="sprint_id"]')).to_have_value(str(sprint.pk))
    expect(page.get_by_text(sprint.protocol.name, exact=True).last).to_be_visible()
    page.goto(live_server.url + "/")
    expect(page.locator("#current-practice-heading")).to_have_text(sprint.protocol.name)
    page.get_by_role("link", name="Open current practice", exact=True).click()
    assert page.url == attempt_url
    page.get_by_role("link", name="Add check-in", exact=True).click()
    expect(page.get_by_label("I tried this action", exact=True)).to_be_visible()
    expect(page.get_by_label("Expected reciprocity", exact=True)).to_have_count(0)
    expect(page.locator("#id_future_interaction_scheduled")).not_to_be_visible()
    expect(page.locator("#id_moved_beyond_transactional")).to_be_visible()
    capture(page, "practice-checkin", width)
    # Keep submission/error/privacy/scoring semantics in the existing full journey;
    # this case checks state identity and the exact currently selected action.
    page.get_by_role("button", name="Submit check-in", exact=True).click()
    expect(page.locator("#form-errors")).to_be_focused()
    expect(page.locator("#id_action_attempted_error")).to_be_visible()
    assert EvidenceEvent.objects.count() == 0
    capture(page, "practice-checkin-error", width)
    page.get_by_label("I tried this action", exact=True).check()
    page.get_by_label("How much support did you use?").select_option("independent")
    page.get_by_label("Did this go as you expected?").select_option("inconclusive")
    page.get_by_role("button", name="Submit check-in", exact=True).click()
    event = EvidenceEvent.objects.get()
    before = build_privacy_safe_evidence_export(user)
    page.goto(live_server.url + "/evidence/")
    expect(page.get_by_label("How did it go?", exact=True)).to_be_visible()
    capture(page, "practice-evidence", width)
    page.get_by_role("link", name="Read check-in", exact=True).click()
    expect(page.get_by_role("heading", name="What happened", exact=True)).to_be_visible()
    expect(page.get_by_text("Technical audit details")).to_have_count(0)
    capture(page, "practice-submitted", width)
    verify_evidence_event(event)
    assert build_privacy_safe_evidence_export(user) == before
    # Seed a genuine service-verified closeout, then exercise post-completion
    # browser state. The existing full journey separately performs UI closeout.
    first, second, _ = sprint.protocol.actions.order_by("sequence")
    _submit(
        sprint,
        first,
        first=False,
        completed=True,
        user_initiated=True,
        moved_beyond_transactional=True,
        meaningful_information_shared=True,
    )
    _submit(sprint, second, first=False, completed=True, future_interaction_scheduled=True)
    complete_with_review(
        sprint=sprint, reflection="Synthetic bounded closeout", contradictory_evidence=""
    )
    page.goto(live_server.url + "/practices/")
    expect(page.locator("#browser-current-practice")).to_have_count(0)
    expect(page.get_by_role("heading", name=sprint.protocol.name, exact=True).first).to_be_visible()
    expect(page.get_by_text("Last completed practice", exact=True)).to_be_visible()
    capture(page, "practice-completed", width)
    page.goto(live_server.url + "/")
    expect(page.locator("#current-practice-heading")).to_have_count(0)
    expect(page.locator("#last-practice-heading")).to_have_text(sprint.protocol.name)
    expect(
        page.get_by_role("heading", name="Choose your next practice", exact=True)
    ).to_be_visible()
