from django import forms

from mentions import config

__all__ = [
    "SubmitWebmentionForm",
]


class SubmitWebmentionForm(forms.Form):
    target = forms.URLField(
        label="The URL of my page", max_length=config.MAX_URL_LENGTH
    )
    source = forms.URLField(
        label="The URL of your page", max_length=config.MAX_URL_LENGTH
    )
