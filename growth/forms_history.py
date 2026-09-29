from django import forms


class ReuseIntentionsForm(forms.Form):
    selected = forms.MultipleChoiceField(
        label="Choose what still fits this assessment period",
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, options, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["selected"].choices = [(row["key"], row["label"]) for row in options]


class ConfirmReuseForm(forms.Form):
    token = forms.CharField(max_length=8000, widget=forms.HiddenInput)
