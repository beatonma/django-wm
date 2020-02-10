from django import forms


class ManualSubmitWebmentionForm(forms.Form):
    target = forms.URLField(label='The URL of my page')
    source = forms.URLField(label='The URL of your page')
