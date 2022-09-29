from django import forms

__all__ = [
    "SubmitWebmentionForm",
]


class SubmitWebmentionForm(forms.Form):
    target = forms.URLField(label="The URL of my page")
    source = forms.URLField(label="The URL of your page")
