from django import forms

from growth.domain.practice_direction import STATES
from growth.forms import PersonalOSForm
from growth.services.practice_direction import DIRECTION_SECTIONS


class DirectionReviewForm(PersonalOSForm):
    expected_revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in tuple(self.fields):
            if name not in {"assessment_epoch", "expected_revision"} and not any(
                name == f"{section}_{suffix}"
                for section in DIRECTION_SECTIONS
                for suffix in ("state", "value")
            ):
                del self.fields[name]
        for key in DIRECTION_SECTIONS:
            self.fields[f"{key}_state"].label = "Response state"


class PracticeDirectionForm(forms.Form):
    assessment_epoch = forms.CharField(widget=forms.HiddenInput)
    expected_revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    expected_personal_os = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    state = forms.ChoiceField(
        label="What does this practice serve?", choices=(("", "Choose a connection"), *STATES)
    )
    priority_index = forms.TypedChoiceField(
        label="Saved priority", coerce=int, empty_value=None, required=False
    )
    intended_outcome = forms.CharField(
        label="Intended outcome",
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text=(
            "A small change you choose to work toward. Use at most 500 characters "
            "and only the private detail you need."
        ),
    )

    def __init__(self, *args, personal_os=None, **kwargs):
        super().__init__(*args, **kwargs)
        priorities = (
            personal_os.priority_stack_value
            if personal_os and personal_os.priority_stack_state == "provided"
            else []
        )
        self.fields["priority_index"].choices = [
            ("", "Choose a saved priority"),
            *[(index, value) for index, value in enumerate(priorities)],
        ]
        self.fields["priority_index"].help_text = (
            "Used only when you choose a saved priority. "
            "Review your direction to add or revise priorities."
        )

    def clean(self):
        cleaned = super().clean()
        state = cleaned.get("state")
        if state == "priority" and cleaned.get("priority_index") is None:
            self.add_error("priority_index", "Choose one of your saved priorities.")
        if state == "outcome" and not cleaned.get("intended_outcome"):
            self.add_error("intended_outcome", "Describe the outcome you intend.")
        # Only the explicitly chosen input is recorded; changing to unknown or
        # declining must not require clearing the previously selected control.
        if state != "priority":
            cleaned["priority_index"] = None
        if state != "outcome":
            cleaned["intended_outcome"] = ""
        return cleaned
