"""One real UI lifecycle; no persisted-assessment or synthetic-closeout shortcuts."""

import json
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from growth.models import (
    AssessmentRun,
    CompletionCreditEvent,
    EvidenceEvent,
    PersonalOSRevision,
    PracticeSprint,
    WeeklyExecutionReview,
)
from growth.services.canonical_import import seed_canonical_data
from growth.services.evidence import build_privacy_safe_evidence_export, verify_evidence_event
from growth.services.profile import build_profile_summary
from tests.e2e.test_application_consistency import audit_page

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.parametrize("width", [390, 1280])
def test_actual_account_assessment_practice_and_closeout(live_server, page, width):
    # Import global canonical content before ANY account exists. Do not seed a
    # demo profile for the fresh owner, or short-circuit assessment/setup/closeout.
    assert get_user_model().objects.count() == 0
    seed_canonical_data()
    page.set_viewport_size({"width": width, "height": 950})
    page.emulate_media(reduced_motion="reduce")
    username = f"integrated-owner-{width}"
    password = "Bounded-Local-Journey-83947!"
    direction = "Make dependable time for friends"
    private = "SYNTHETIC-PRIVATE-INTEGRATED-CONTEXT"

    def capture(state):
        audit_page(page)
        main = page.locator("main").inner_text()
        for debug in (
            "Technical audit details",
            "Base evidence mass",
            "GG-EVIDENCE-1.0",
            "Response-quality modifier",
        ):
            assert debug not in main
        folder = Path("test-results/pilot-walkthrough")
        folder.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=folder / f"uxa-integrated-{state}-{width}.png", full_page=True)

    # Pass 0: actual registration/login, ordinary privileges and no seeded run.
    page.goto(live_server.url + "/accounts/login/")
    page.get_by_role("link", name="Create account", exact=True).click()
    page.get_by_label("Username:", exact=True).fill(username)
    page.get_by_label("Password:", exact=True).fill(password)
    page.get_by_label("Password confirmation:", exact=True).fill(password)
    page.get_by_role("button", name="Create account", exact=True).click()
    expect(page.get_by_role("button", name="Sign in", exact=True)).to_be_visible()
    user = get_user_model().objects.get(username=username)
    assert not user.is_staff and not user.is_superuser
    assert not AssessmentRun.objects.filter(user=user).exists()
    page.get_by_label("Username", exact=True).fill(username)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    expect(page.get_by_role("link", name="Start assessment", exact=True)).to_be_visible()
    for label in ("Profile", "Practices", "Weekly", "Personal OS", "History", "Evidence"):
        expect(page.get_by_role("link", name=label, exact=True)).to_have_count(0)
    capture("fresh")
    for path in ("/profile/", "/practices/", "/weekly/"):
        page.goto(live_server.url + path)
        assert page.url.startswith(live_server.url + "/assessment/")
    expect(page.locator(".assessment-import")).not_to_have_attribute("open", "")
    page.get_by_role("button", name="Begin assessment", exact=True).click()
    page.get_by_label("Enable answer shortcuts").check()
    page.locator("#assessment-prompt").focus()
    for index in range(50):
        expect(page.locator("#assessment-count")).to_have_text(f"Question {index + 1} of 50")
        page.keyboard.press("1" if index < 12 and index % 2 == 0 else "5" if index < 12 else "4")
    expect(page.locator("#assessment-count")).to_have_text(re.compile(r"Follow-up 1 of (8|9|10)"))
    followups = int(page.locator("#assessment-count").inner_text().split()[-1])
    for index in range(followups):
        expect(page.locator("#assessment-count")).to_have_text(
            f"Follow-up {index + 1} of {followups}"
        )
        page.keyboard.press("4")
    expect(page.locator("#assessment-save-status")).to_have_text("Saved")
    run = AssessmentRun.objects.get(user=user, source="application")
    assert len(run.answers) == 50 and len(run.clarifier_answers) == followups
    assert sum(key.startswith("C_") for key in run.clarifier_answers) == 8
    run_before = AssessmentRun.objects.values().get(pk=run.pk)
    page.get_by_role("button", name="Retake", exact=True).click()
    expect(page.get_by_role("button", name="Keep current results")).to_be_focused()
    page.keyboard.press("Escape")
    expect(page.get_by_role("button", name="Retake", exact=True)).to_be_focused()

    # Pass 1: both kinds of help by mouse and keyboard; share is opt-in.
    page.goto(live_server.url + "/profile/")
    for selector in (".score-list .inline-help", ".archetype-list .inline-help"):
        details = page.locator(selector).first
        summary = details.locator("summary")
        summary.click()
        expect(details).to_have_attribute("open", "")
        summary.click()
        summary.focus()
        page.keyboard.press("Enter")
        expect(details.locator("p")).to_be_visible()
        capture("help" if "score-list" in selector else "archetype")
        page.keyboard.press("Escape")
        expect(details).not_to_have_attribute("open", "")
        expect(summary).to_be_focused()
    share = page.get_by_role("button", name="Share", exact=True)
    expect(page.locator("#profile-share")).not_to_be_visible()
    share.focus()
    page.keyboard.press("Enter")
    expect(page.get_by_role("dialog", name="Share assessment results")).to_be_visible()
    expect(page.get_by_label("Assessment share code")).to_have_value(run.original_share_code)
    capture("share")
    page.keyboard.press("Escape")
    expect(share).to_be_focused()
    expect(page.get_by_role("link", name="Open final review", exact=True)).to_have_count(0)
    page.goto(live_server.url + "/weekly/")
    expect(page.get_by_role("heading", name="Look back at your action")).to_have_count(0)
    expect(page.get_by_text("No submitted proof", exact=False)).to_have_count(0)
    capture("assessed")

    # Explicit direction through the actual progressive form, not a direct POST.
    page.goto(live_server.url + "/personal-os/")
    for index in range(9):
        expect(page.locator(".reflection-fieldset:visible")).to_have_count(1)
        if page.locator("#id_twelve_month_direction_state").is_visible():
            page.locator("#id_twelve_month_direction_state").select_option("provided")
            page.locator("#id_twelve_month_direction_value").fill(direction)
        if index < 8:
            page.get_by_role("button", name="Next question", exact=True).click()
    page.get_by_role("button", name="Save Personal OS revision", exact=True).click()
    expect(page.get_by_role("heading", name="Your current direction")).to_be_visible()
    assert PersonalOSRevision.objects.get(user=user).twelve_month_direction_value == direction

    # Select one known protocol explicitly from the bounded browser, regardless
    # of this genuinely answered assessment's suggestion order.
    page.goto(live_server.url + "/practices/?browse=1&q=Deepen%20One%20Existing%20Friendship")
    page.locator("#practice-results").get_by_role(
        "link", name="Review practice", exact=True
    ).click()
    page.get_by_role("link", name="Start guided setup", exact=True).click()
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_label("Yes, this relationship is available").check()
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_label("Private label for the person or context").fill(private)
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_label(re.compile(r"I will choose welcome contact")).check()
    page.get_by_role("button", name="I understand and will respect these boundaries").click()
    page.get_by_label("Start date", exact=True).fill(date.today().isoformat())
    page.get_by_role("button", name="Continue", exact=True).click()
    page.get_by_role("button", name="I have reviewed the defined actions").click()
    page.get_by_role("button", name="Begin practice", exact=True).click()
    sprint = PracticeSprint.objects.get(user=user)
    assert sprint.assessment_run_id == run.pk
    attempt_url = live_server.url + f"/practice-sprints/{sprint.pk}/"
    assert page.url == attempt_url
    expect(page.get_by_role("button", name="Open final review")).to_be_disabled()
    gate = page.locator('[tabindex="0"][aria-describedby="closeout-requirements"]')
    gate.focus()
    expect(gate).to_be_focused()
    expect(page.locator("#closeout-requirements")).to_be_visible()
    capture("gate")

    # Pass 2: same saved attempt/version across all entry surfaces.
    page.goto(live_server.url + "/")
    expect(page.locator("#current-practice-heading")).to_have_text(sprint.protocol.name)
    expect(page.get_by_text(direction, exact=True)).to_be_visible()
    page.get_by_role("link", name="Open current practice", exact=True).click()
    assert page.url == attempt_url
    capture("active")
    page.goto(live_server.url + f"/practices/{sprint.protocol.slug}/guide/")
    expect(page.locator("[data-attempt]").first).to_have_attribute("data-attempt", str(sprint.pk))
    page.get_by_role("link", name="Back to your current practice", exact=False).click()
    assert page.url == attempt_url
    page.goto(live_server.url + "/practices/?browse=1&q=Deepen%20One%20Existing%20Friendship")
    expect(page.locator("#browser-current-practice")).to_have_attribute(
        "data-attempt", str(sprint.pk)
    )
    page.locator("#practice-results").get_by_role(
        "link", name="Open current practice", exact=True
    ).click()
    assert page.url == attempt_url
    page.goto(live_server.url + "/weekly/")
    expect(page.locator('input[name="sprint_id"]')).to_have_value(str(sprint.pk))
    expect(page.get_by_text(direction, exact=True)).to_be_visible()
    page.get_by_label("Which day?", exact=True).fill(date.today().isoformat())
    page.get_by_role("button", name="Save weekly plan", exact=True).click()
    capture("planned")
    first, second, _ = sprint.protocol.actions.order_by("sequence")
    for index, action in enumerate((first, second)):
        page.goto(attempt_url + f"check-ins/new/?action={action.pk}")
        if index == 0:
            page.get_by_role("button", name="Submit check-in", exact=True).click()
            expect(page.locator("#form-errors")).to_be_focused()
            assert EvidenceEvent.objects.filter(check_in__sprint__user=user).count() == 0
            capture("error")
        page.get_by_label("I tried this action", exact=True).check()
        page.get_by_label("I completed this action", exact=True).check()
        if index == 0:
            page.get_by_label("The interaction moved beyond logistics or small talk").check()
            page.get_by_label("Meaningful information was freely shared").check()
            page.get_by_role("button", name="Save draft", exact=True).click()
            expect(page.get_by_role("heading", name="Draft check-ins")).to_be_visible()
            assert EvidenceEvent.objects.filter(check_in__sprint__user=user).count() == 0
            page.locator(".draft-list a").click()
            expect(page.get_by_label("I completed this action", exact=True)).to_be_checked()
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
    assert not CompletionCreditEvent.objects.filter(sprint=sprint).exists()
    before_export = build_privacy_safe_evidence_export(user)
    page.goto(live_server.url + "/evidence/")
    capture("evidence")
    page.goto(live_server.url + "/account/data/")
    expect(page.locator("#evidence-download")).not_to_have_attribute("open", "")
    page.locator("#evidence-download > summary").click()
    with page.expect_download() as download:
        page.get_by_role("link", name="Download minimized evidence JSON").click()
    exported = json.loads(Path(download.value.path()).read_text())
    assert exported == before_export
    assert private not in json.dumps(exported) and run.original_share_code not in json.dumps(
        exported
    )
    for event in EvidenceEvent.objects.filter(check_in__sprint__user=user):
        verify_evidence_event(event)
    page.goto(live_server.url + "/weekly/")
    page.get_by_role("button", name="Save proof-based weekly review").click()
    review = WeeklyExecutionReview.objects.get(plan__user=user)
    frozen = review.canonical_snapshot
    page.goto(attempt_url)
    page.get_by_role("link", name="Open final review", exact=True).click()
    expect(
        page.get_by_text("Completing this practice does not establish mastery.", exact=True)
    ).to_be_visible()
    capture("review")
    page.get_by_label("What did this practice show you?").fill(
        "Making a specific invitation helped us act on our conversation."
    )
    page.get_by_role("button", name="Submit final review and record 75% credit").click()
    expect(page.get_by_role("heading", name="Your practice is complete.")).to_be_visible()
    capture("complete")
    sprint.refresh_from_db()
    assert sprint.status == "completed"
    assert CompletionCreditEvent.objects.get(sprint=sprint).completion_credit == Decimal("0.75")

    # Pass 3: recomputed suggestions, retained direction, no duplicate current
    # practice. 75% credit does not mean this protocol can never recur later.
    for path, state in (
        ("/", "home"),
        ("/weekly/", "weekly"),
        ("/profile/", "profile"),
        ("/practices/", "browser"),
    ):
        page.goto(live_server.url + path)
        expect(page.locator("#current-practice-heading, #browser-current-practice")).to_have_count(
            0
        )
        assert "Find a starting point" not in page.locator("main").inner_text()
        if path == "/":
            expect(
                page.get_by_role("heading", name="Choose your next practice", exact=True)
            ).to_be_visible()
            expect(page.get_by_text(direction, exact=True)).to_be_visible()
        if path == "/weekly/":
            expect(page.get_by_role("link", name="Choose a practice", exact=True)).to_be_visible()
        capture("completed-" + state)
    expected = [p.pk for p in build_profile_summary(user).recommendations]
    displayed = page.locator("#practice-suggestions [data-protocol]").evaluate_all(
        "els => els.map(e => e.dataset.protocol)"
    )
    assert displayed == expected[: len(displayed)] and displayed
    assert PracticeSprint.objects.filter(user=user).count() == 1
    assert AssessmentRun.objects.values().get(pk=run.pk) == run_before
    assert build_privacy_safe_evidence_export(user) == before_export
    review.refresh_from_db()
    assert review.canonical_snapshot == frozen
