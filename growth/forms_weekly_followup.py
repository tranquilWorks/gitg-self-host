from django import forms
from django.utils import timezone

from growth.forms import WeeklyExecutionPlanForm


class RecurringWeeklyPlanForm(WeeklyExecutionPlanForm):
    expected_revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("intended_on") and cleaned["intended_on"] < timezone.localdate():
            self.add_error("intended_on", "Choose today or a later day this week.")
        return cleaned


class WeeklyTransitionForm(forms.Form):
    expected_status = forms.ChoiceField(
        choices=(("active", "Active"), ("paused", "Paused")), widget=forms.HiddenInput
    )
    expected_week = forms.DateField(widget=forms.HiddenInput)
