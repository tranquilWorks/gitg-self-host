import re
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from playwright.sync_api import expect

from growth.assessment_copy import PROMPTS
from growth.models import AssessmentRun, PracticeContext
from growth.services.assessment import persist_assessment_run
from growth.services.canonical_import import seed_canonical_data
from tests.test_assessment_integration import golden_payload
from tests.test_practice_workflow import create_sprint
from tests.test_uxa_entry_assessment import complete_loop

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def login(live_server, page, username):
    page.goto(live_server.url + "/")
    page.get_by_label("Username").fill(username)
    page.get_by_label("Password").fill("Entry-Test-Password-2047!")
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url(live_server.url + "/")


def capture(page, name):
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    artifacts = Path("test-results/pilot-walkthrough")
    artifacts.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=artifacts / f"uxa-{name}.png", full_page=True)


@pytest.mark.parametrize("width", [390, 1280])
def test_all_four_home_stages_and_explicit_skip(live_server, page, width):
    user = get_user_model().objects.create_user(
        username=f"entry-{width}", password="Entry-Test-Password-2047!"
    )
    page.set_viewport_size({"width": width, "height": 900})
    login(live_server, page, user.username)
    expect(page.get_by_role("link", name="Start assessment", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", name="How it works", exact=True)).to_be_visible()
    for label in ("Practices", "Personal OS", "Weekly", "Profile", "History", "Evidence"):
        expect(page.get_by_role("link", name=label, exact=True)).to_have_count(0)
    expect(page.locator(".practice-card")).to_have_count(0)
    capture(page, f"home-fresh-{width}")
    page.get_by_role("link", name="Start assessment", exact=True).click()
    expect(page.locator("#assessment-intro")).to_be_visible()

    seed_canonical_data()
    persist_assessment_run(user, golden_payload())
    page.goto(live_server.url + "/")
    expect(
        page.get_by_role("heading", name="Choose your next practice", exact=True)
    ).to_be_visible()
    expect(page.locator(".onboarding-progress s")).to_have_text("Take the assessment")
    expect(page.get_by_role("heading", name="How it works", exact=True)).to_have_count(0)
    capture(page, f"home-assessed-{width}")
    card = page.locator(".practice-card").first
    skipped_name = card.locator("h3").inner_text()
    card.locator("summary").focus()
    page.keyboard.press("Enter")
    card.get_by_role("button", name="Skip for now", exact=True).click()
    expect(page.get_by_text("Skipped for now. Choose another suggestion below.")).to_be_visible()
    expect(page.locator(".practice-card h3").filter(has_text=skipped_name)).to_have_count(0)
    assert (
        PracticeContext.objects.filter(
            user=user, disposition="deferred", defer_reason="user_choice"
        ).count()
        == 1
    )

    sprint = create_sprint(user)
    page.reload()
    expect(page.locator("#current-practice-heading")).to_have_text(sprint.protocol.name)
    expect(page.get_by_role("link", name="Open current practice", exact=True)).to_be_visible()
    expect(page.locator(".practice-card h3").filter(has_text=sprint.protocol.name)).to_have_count(0)
    capture(page, f"home-active-{width}")
    # Finish through the actual check-in/review workflow, reusing the same active practice.
    completed = complete_loop(Client(), user, sprint)
    page.reload()
    expect(page.locator("#last-practice-heading")).to_have_text(completed.protocol.name)
    expect(page.locator("#current-practice-heading")).to_have_count(0)
    expect(page.get_by_text("Find your starting point", exact=True)).to_have_count(0)
    expect(page.locator(".onboarding-progress")).to_have_count(0)
    page.get_by_role("link", name="Read the review", exact=True).click()
    expect(
        page.get_by_role("heading", name="Your practice is complete.", exact=True)
    ).to_be_visible()
    page.goto(live_server.url + "/")
    capture(page, f"home-completed-{width}")


@pytest.mark.parametrize("width", [390, 1280])
def test_single_key_assessment_automatic_followups_and_completed_retake(live_server, page, width):
    user = get_user_model().objects.create_user(
        username=f"answers-{width}", password="Entry-Test-Password-2047!"
    )
    seed_canonical_data()
    page.set_viewport_size({"width": width, "height": 900})
    login(live_server, page, user.username)
    page.goto(live_server.url + "/assessment/")
    expect(page.locator(".assessment-import")).not_to_have_attribute("open", "")
    expect(page.get_by_label("Share code", exact=True)).not_to_be_visible()
    page.get_by_role("button", name="Begin assessment", exact=True).click()
    first_id = page.evaluate("window.GroundedGrowthAssessmentApp.getState().index")
    assert first_id == 0
    displayed_id = page.evaluate(
        "JSON.parse(document.querySelector('#assessment-spec').textContent).assessment.display_order[0]"
    )
    expect(page.locator("#assessment-prompt")).to_have_text(PROMPTS[displayed_id])
    # Ordinary answers still use Next; shortcuts are explicitly opt-in.
    page.keyboard.press("4")
    expect(page.locator("#assessment-count")).to_have_text("Question 1 of 50")
    page.get_by_label("Enable answer shortcuts").check()
    page.locator("#assessment-prompt").focus()
    capture(page, f"assessment-question-{width}")
    for index in range(50):
        expect(page.locator("#assessment-count")).to_have_text(f"Question {index + 1} of 50")
        page.keyboard.press("1" if index < 12 and index % 2 == 0 else "5" if index < 12 else "4")
    expect(page.locator("#assessment-count")).to_have_text(re.compile(r"Follow-up 1 of (8|9|10)"))
    followups = int(page.locator("#assessment-count").inner_text().split()[-1])
    capture(page, f"assessment-followup-{width}")
    # Going back across the phase boundary keeps the last core answer and
    # automatically reselects valid follow-ups, with no mode-selection screen.
    page.keyboard.press("ArrowLeft")
    expect(page.locator("#assessment-count")).to_have_text("Question 50 of 50")
    page.keyboard.press("4")
    for index in range(followups):
        expect(page.locator("#assessment-count")).to_have_text(
            f"Follow-up {index + 1} of {followups}"
        )
        page.keyboard.press("4")
    expect(page.get_by_role("heading", name="Assessment complete", exact=True)).to_be_visible()
    expect(page.locator("#assessment-save-status")).to_have_text("Saved")
    run = AssessmentRun.objects.get(user=user, source="application")
    assert len(run.answers) == 50
    assert len(run.clarifier_answers) == followups
    assert len([key for key in run.clarifier_answers if key.startswith("C_")]) == 8
    expect(page.locator("#assessment-intro")).not_to_be_visible()
    expect(page.get_by_role("link", name="See results", exact=True)).to_be_visible()
    expect(page.get_by_text("Response-quality modifier", exact=False)).to_have_count(0)
    capture(page, f"assessment-completed-{width}")
    page.reload()
    expect(page.get_by_role("heading", name="Assessment complete", exact=True)).to_be_visible()
    expect(page.locator("#assessment-intro")).not_to_be_visible()
    page.get_by_role("button", name="Retake", exact=True).click()
    expect(page.get_by_role("dialog")).to_be_visible()
    expect(page.get_by_role("button", name="Keep current results")).to_be_focused()
    capture(page, f"assessment-retake-{width}")
    page.keyboard.press("Escape")
    expect(page.get_by_role("dialog")).not_to_be_visible()
    expect(page.get_by_role("button", name="Retake", exact=True)).to_be_focused()
    assert AssessmentRun.objects.filter(user=user, source="application").count() == 1
    page.get_by_role("button", name="Retake", exact=True).click()
    page.get_by_role("button", name="Start a new assessment", exact=True).click()
    expect(page.locator("#assessment-intro")).to_be_visible()
    page.get_by_role("button", name="Begin assessment", exact=True).click()
    page.get_by_label("Enable answer shortcuts").check()
    page.locator("#assessment-prompt").focus()
    page.keyboard.press("3")
    page.reload()
    page.get_by_role("button", name="Resume assessment", exact=True).click()
    expect(page.locator("#assessment-count")).to_have_text("Question 2 of 50")
    assert AssessmentRun.objects.filter(user=user, source="application").count() == 1


def test_assessment_import_error_and_save_retry_keep_answers(live_server, page):
    user = get_user_model().objects.create_user(
        username="retry-answers", password="Entry-Test-Password-2047!"
    )
    seed_canonical_data()
    login(live_server, page, user.username)
    page.goto(live_server.url + "/assessment/")
    page.locator(".assessment-import > summary").click()
    page.get_by_label("Share code", exact=True).fill("not-a-share-code")
    page.get_by_role("button", name="Import profile", exact=True).click()
    expect(page.locator("#assessment-import-error")).to_be_visible()
    payload = golden_payload()
    page.route(
        "**/assessment/runs/",
        lambda route: route.fulfill(
            status=503,
            content_type="application/json",
            body='{"error":"Synthetic temporary save failure"}',
        ),
    )
    page.evaluate(
        "(payload) => window.GroundedGrowthAssessmentApp.completeWithState(payload)", payload
    )
    expect(page.locator("#assessment-save-status")).to_have_text("Save failed")
    expect(page.locator("#assessment-profile-link")).not_to_be_visible()
    assert page.evaluate(
        "Object.keys(window.GroundedGrowthAssessmentApp.getState().responses).length"
    ) == len(payload["responses"])
    page.unroute("**/assessment/runs/")
    page.get_by_role("button", name="Retry save", exact=True).click()
    expect(page.locator("#assessment-save-status")).to_have_text("Saved")
    expect(page.locator("#assessment-profile-link")).to_be_visible()
    assert AssessmentRun.objects.filter(user=user, source="application").count() == 1
