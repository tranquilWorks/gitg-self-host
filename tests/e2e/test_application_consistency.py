import pytest
from playwright.sync_api import expect

from tests.e2e.test_core_flow import (
    assert_no_horizontal_overflow,
    create_browser_user,
    log_in,
    save_walkthrough_screenshot,
    seed_browser_data,
)
from tests.test_weekly_execution import _sprint
from tests.test_weekly_followup import plan_for

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def audit_page(page):
    assert_no_horizontal_overflow(page)
    expect(page.locator("main h1")).to_have_count(1)
    defects = page.evaluate("""() => {
      const visible = e => e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden';
      const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
      return {
        duplicateIds: ids.filter((id, i) => ids.indexOf(id) !== i),
        unlabelled: [...document.querySelectorAll('input:not([type=hidden]), textarea, select')]
          .filter(visible).filter(e => !e.labels?.length && !e.getAttribute('aria-label')
            && !e.getAttribute('aria-labelledby')).map(e => e.id),
        brokenDescriptions: [...document.querySelectorAll('[aria-describedby]')].filter(visible)
          .flatMap(e => e.getAttribute('aria-describedby').split(/\\s+/)
            .filter(id => !document.getElementById(id)).map(id => [e.id,id]))
      };
    }""")
    assert defects == {"duplicateIds": [], "unlabelled": [], "brokenDescriptions": []}, (
        page.url,
        defects,
    )
    assert page.locator('.site-nav [aria-current="page"]').count() <= 1


@pytest.mark.parametrize("width", [320, 390, 1280])
def test_application_surface_reflow_and_semantics(live_server, page, width):
    page.set_viewport_size({"width": width, "height": 900})
    page.emulate_media(reduced_motion="reduce")
    user = create_browser_user()
    seed_browser_data()
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    slug = sprint.protocol.slug
    log_in(live_server, page)
    paths = [
        "/",
        "/personal-os/",
        "/personal-os/direction/",
        "/personal-os/practices/",
        f"/personal-os/practices/{slug}/context/",
        "/weekly/",
        f"/weekly/plans/{plan.pk}/",
        "/practices/",
        f"/practices/{slug}/",
        f"/practices/{slug}/direction/",
        f"/practices/{slug}/setup/1/",
        f"/practices/{slug}/guide/",
        f"/practice-sprints/{sprint.pk}/",
        f"/practice-sprints/{sprint.pk}/check-ins/new/",
        f"/practice-sprints/{sprint.pk}/review/",
        "/history/",
        f"/history/periods/{sprint.assessment_run_id}/",
        f"/history/plans/{plan.pk}/",
        "/profile/",
        "/account/data/",
        "/account/pilot-feedback/",
        "/accounts/password-change/",
        "/assessment/",
    ]
    for path in paths:
        response = page.goto(live_server.url + path)
        assert response.status == 200, (path, response.status)
        audit_page(page)
        if path in {"/", "/personal-os/", "/account/data/", "/profile/"}:
            save_walkthrough_screenshot(
                page, f"consistency-{width}-{path.strip('/').replace('/', '-') or 'home'}"
            )
    # 200% text sizing is separate from the 320 CSS-pixel reflow check.
    page.goto(live_server.url + "/personal-os/")
    page.add_style_tag(content="html { font-size: 200%; }")
    audit_page(page)
    save_walkthrough_screenshot(page, f"consistency-{width}-large-text")
    assert (
        page.locator(".skip-link").evaluate("(e) => getComputedStyle(e).transitionDuration") == "0s"
    )


def test_keyboard_assessment_and_error_recovery(live_server, page):
    create_browser_user()
    seed_browser_data()
    log_in(live_server, page)
    page.keyboard.press("Tab")
    expect(page.locator(".skip-link")).to_be_focused()
    page.keyboard.press("Enter")
    expect(page.locator("#main-content")).to_be_focused()
    more = page.locator(".nav-more > summary")
    more.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("link", name="Assessment", exact=True)).to_be_visible()
    page.keyboard.press("Escape")
    expect(more).to_be_focused()
    page.keyboard.press("Enter")
    page.get_by_role("link", name="Assessment", exact=True).click()
    page.get_by_role("button", name="Begin assessment").click()
    prompt = page.locator("#assessment-prompt")
    expect(prompt).to_be_focused()
    page.keyboard.press("3")
    expect(page.locator('.assessment-answer[aria-pressed="true"]')).to_have_count(0)
    answer = page.locator('.assessment-answer[data-value="3"]')
    answer.focus()
    page.keyboard.press("Enter")
    expect(answer).to_have_attribute("aria-pressed", "true")
    expect(page.locator("#assessment-count")).to_have_text("Question 1 of 50")
    page.get_by_label("Enable answer shortcuts").check()
    prompt.focus()
    page.keyboard.press("4")
    expect(page.locator('.assessment-answer[data-value="4"]')).to_have_attribute(
        "aria-pressed", "true"
    )
    more.focus()
    page.keyboard.press("2")
    expect(page.locator('.assessment-answer[data-value="4"]')).to_have_attribute(
        "aria-pressed", "true"
    )
    page.get_by_role("button", name="Next", exact=True).focus()
    page.keyboard.press("Enter")
    expect(prompt).to_be_focused()
    expect(page.locator("#assessment-count")).to_have_text("Question 2 of 50")
    page.get_by_role("button", name="Back", exact=True).click()
    expect(page.locator('.assessment-answer[data-value="4"]')).to_have_attribute(
        "aria-pressed", "true"
    )
    save_walkthrough_screenshot(page, "consistency-assessment-keyboard")
    page.goto(live_server.url + "/personal-os/")
    page.locator("#id_mission_state").select_option("provided")
    page.get_by_role("button", name="Save Personal OS").click()
    summary = page.locator("#form-errors")
    expect(summary).to_be_focused()
    summary.locator('a[href="#id_mission_value"]').click()
    expect(page.locator("#id_mission_value")).to_be_focused()
    audit_page(page)
    save_walkthrough_screenshot(page, "consistency-form-recovery")


def test_navigation_and_form_recovery_without_javascript(live_server, browser):
    create_browser_user()
    seed_browser_data()
    context = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 900})
    page = context.new_page()
    try:
        log_in(live_server, page)
        page.locator(".nav-more > summary").click()
        page.get_by_role("link", name="Account", exact=True).click()
        expect(
            page.get_by_role("heading", name="Keep control of your private record.")
        ).to_be_visible()
        page.goto(live_server.url + "/accounts/password-change/")
        page.get_by_label("Old password").fill("incorrect-password")
        page.get_by_label("New password:", exact=True).fill("Browser-Replacement-Password-2047!")
        page.get_by_label("New password confirmation:").fill("Browser-Replacement-Password-2047!")
        page.get_by_role("button", name="Update password").click()
        expect(page.locator("#form-errors")).to_be_visible()
        expect(page.locator('#form-errors a[href="#id_old_password"]')).to_be_visible()
        assert_no_horizontal_overflow(page)
        page.goto(live_server.url + "/assessment/")
        expect(page.locator("noscript .status-note")).to_be_visible()
        expect(page.locator("noscript .status-note")).to_contain_text(
            "The assessment runs on this device and needs JavaScript."
        )
        page.goto(live_server.url + "/personal-os/")
        page.locator("details.stage-panel").last.locator("summary").click()
        page.locator("#id_current_truth_state").select_option("provided")
        page.get_by_role("button", name="Save Personal OS revision").click()
        expect(page.locator("#id_current_truth_value")).to_be_visible()
        expect(page.locator('#form-errors a[href="#id_current_truth_value"]')).to_be_visible()
    finally:
        context.close()


def test_conditional_forms_and_conflict_recovery(live_server, page):
    from growth.services.assessment import persist_assessment_run
    from growth.services.assessment_calibration import record_assessment_calibration_consent
    from growth.services.weekly_followup import save_plan_review
    from tests.test_assessment_integration import golden_payload
    from tests.test_history_continuity import save_intentions

    page.set_viewport_size({"width": 390, "height": 900})
    user = create_browser_user()
    seed_browser_data()
    sprint = _sprint(user)
    save_intentions(user, sprint.assessment_run, "Make time to learn")
    plan = plan_for(user, sprint)
    save_plan_review(user=user, plan=plan, next_step="pause_reconsider", adjustment="timing")
    log_in(live_server, page)
    for path in [f"/weekly/plans/{plan.pk}/replan/", f"/weekly/plans/{plan.pk}/decision/pause/"]:
        assert page.goto(live_server.url + path).status == 200
        audit_page(page)
    target, _ = persist_assessment_run(user, golden_payload())
    record_assessment_calibration_consent(user=user, assessment_run=target, state="consented")
    page.goto(live_server.url + "/account/data/")
    expect(page.get_by_label("Completed assessment:", exact=True)).to_be_visible()
    expect(page.get_by_label("Included assessment:", exact=True)).to_be_visible()
    audit_page(page)
    save_walkthrough_screenshot(page, "consistency-consent-forms")
    page.goto(live_server.url + "/history/reuse/")
    audit_page(page)
    page.get_by_role("button", name="Preview selected intentions").click()
    expect(page.locator("#form-errors")).to_be_focused()
    page.locator('#form-errors a[href="#id_selected"]').click()
    expect(page.locator('input[name="selected"]').first).to_be_focused()
    page.get_by_label("Mission", exact=True).check()
    page.get_by_role("button", name="Preview selected intentions").click()
    audit_page(page)
    response = page.goto(live_server.url + f"/weekly/plans/{plan.pk}/")
    assert response.status == 409
    audit_page(page)
    save_walkthrough_screenshot(page, "consistency-conflict-recovery")
    page.get_by_role("link", name="Open this week", exact=True).click()
    expect(
        page.get_by_role("heading", name="Turn one direction into one concrete action.")
    ).to_be_visible()
