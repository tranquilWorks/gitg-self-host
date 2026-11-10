from datetime import date

import pytest
from django.urls import reverse

from growth.forms import WeeklyExecutionReviewForm
from growth.services.practice import complete_with_review, completion_evidence
from growth.services.weekly_execution import current_window
from growth.services.weekly_followup import save_plan_review
from growth.weekly_presentation import closeout_remaining, present_review_form
from tests.test_composite_score_state import _partial_closeout, _submit
from tests.test_weekly_execution import _sprint
from tests.test_weekly_followup import plan_for

pytestmark = pytest.mark.django_db


def test_calendar_week_does_not_start_when_practice_starts():
    assert current_window(today=date(2026, 10, 6)) == (date(2026, 10, 5), date(2026, 10, 11))


def test_weekly_missing_direction_and_plan_have_direct_actions(client, user, seeded):
    _sprint(user)
    client.force_login(user)
    page = client.get("/weekly/")
    assert page.status_code == 200
    for text in (b"No direction yet", b"Set direction", b"Create a weekly plan", b"Monday"):
        assert text in page.content
    assert b"No submitted proof" not in page.content
    assert b"no hidden analysis" not in page.content


def test_current_saved_review_not_displaced_by_older_unreviewed_plan(client, user, seeded):
    sprint = _sprint(user)
    older = plan_for(user, sprint, weeks_ago=2)
    current = plan_for(user, sprint)
    review = save_plan_review(
        user=user, plan=current, next_step="continue_current", adjustment="none"
    ).review
    frozen = review.canonical_snapshot
    client.force_login(user)
    page = client.get("/weekly/")
    assert page.context["review_target"] is None
    assert page.context["current_review"].pk == review.pk
    assert b"Act on your review" in page.content
    assert str(older.pk).encode() in page.content
    client.get(reverse("weekly-plan-detail", args=[current.pk]))
    review.refresh_from_db()
    assert review.canonical_snapshot == frozen


def test_unready_gate_is_disabled_and_direct_post_still_rejected(client, user, seeded):
    sprint = _sprint(user)
    client.force_login(user)
    evidence = completion_evidence(sprint)
    assert not evidence.ready_for_review
    assert closeout_remaining(evidence)
    page = client.get(reverse("growth:practice-sprint", args=[sprint.pk]))
    assert b'disabled type="button" aria-describedby="closeout-requirements"' in page.content
    response = client.post(
        reverse("growth:practice-review", args=[sprint.pk]),
        {"reflection": "Cannot replace missing activity.", "contradictory_evidence": ""},
    )
    assert response.status_code == 200
    sprint.refresh_from_db()
    assert sprint.status != "completed"
    assert not hasattr(sprint, "review")


def test_completed_handoff_agrees_and_does_not_change_saved_state(client, user, seeded):
    sprint, _ = _partial_closeout(user)
    client.force_login(user)
    for path in ("/", "/weekly/", "/profile/", "/practices/"):
        page = client.get(path)
        assert page.status_code == 200
        assert page.context.get("active_sprint") is None
        assert b"Find a starting point" not in page.content
    complete = client.get(reverse("growth:practice-review-complete", args=[sprint.pk]))
    assert b"Your practice is complete." in complete.content
    assert b"Choose your next practice" in complete.content
    assert b"mastery" in complete.content
    assert b"mastery-notice" not in complete.content


def test_display_form_preserves_choice_values():
    form = WeeklyExecutionReviewForm()
    before = {
        key: [value for value, _ in form.fields[key].choices] for key in ("next_step", "adjustment")
    }
    present_review_form(form)
    assert before == {key: [value for value, _ in form.fields[key].choices] for key in before}


def test_reviewed_plan_after_closeout_preserves_frozen_proof_and_next_step(client, user, seeded):
    sprint = _sprint(user)
    plan = plan_for(user, sprint)
    first, second, _ = sprint.protocol.actions.order_by("sequence")
    _submit(sprint, first, first=True, completed=True, moved_beyond_transactional=True)
    review = save_plan_review(
        user=user, plan=plan, next_step="continue_current", adjustment="none"
    ).review
    frozen = review.canonical_snapshot
    _submit(sprint, second, first=False, completed=True, future_interaction_scheduled=True)
    complete_with_review(
        sprint=sprint, reflection="Synthetic final reflection.", contradictory_evidence=""
    )
    client.force_login(user)
    response = client.get(reverse("weekly-plan-detail", args=[plan.pk]))
    assert response.status_code == 200
    assert b"Choose your next practice" in response.content
    assert b"Plan this action again" not in response.content
    assert b"No submitted proof" not in response.content
    review.refresh_from_db()
    assert review.canonical_snapshot == frozen
