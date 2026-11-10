"""Display-only weekly language; captured values and frozen proof stay unchanged."""

from growth.practice_presentation import CHOICE_COPY, display_action_title


def present_review_form(form):
    form.fields["next_step"].label = "What would you like to do next?"
    form.fields["adjustment"].label = "What would help next time?"
    labels = {
        "none": "Keep it as it is",
        "timing": "Choose a better time",
        "scope": "Make the action more manageable",
        "support": "Ask for help or use an allowed aid",
        "context": "Try a more suitable situation",
        "recovery": "Make room for rest or other demands",
    }
    form.fields["adjustment"].choices = [
        (key, labels.get(key, label)) for key, label in form.fields["adjustment"].choices
    ]
    return form


def present_plan_form(form):
    if form is not None:
        form.fields["action"].label = "Which action will you work on?"
        form.fields["action"].label_from_instance = display_action_title
        form.fields["action"].help_text = "Choose from your current practice."
        form.fields["intended_on"].label = "Which day?"
    return form


def present_proof(rows):
    return tuple(
        {
            **row,
            "direction_label": CHOICE_COPY["evidence_direction"].get(
                row["direction"], "No result was recorded"
            ),
        }
        for row in rows
    )


def closeout_remaining(evidence):
    """Describe the existing service gate, never calculate an alternative gate."""
    reasons = []
    if not evidence.uses_composite_closeout and not evidence.all_actions_attempted:
        reasons.append("Submit a check-in for each action you have actually tried.")
    if not evidence.enough_actions_completed:
        reasons.append(
            f"Complete at least {evidence.minimum_completed} actions "
            f"({evidence.actions_completed} recorded so far)."
        )
    if not evidence.substantive_interaction_occurred:
        reasons.append("Record the practice's required observation in a submitted check-in.")
    return reasons
