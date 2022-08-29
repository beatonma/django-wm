from django import forms

__all__ = [
    "ManualSubmitWebmentionForm",
]


class ManualSubmitWebmentionForm(forms.Form):
    target = forms.URLField(label="The URL of my page")
    source = forms.URLField(label="The URL of your page")
