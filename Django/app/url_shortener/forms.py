from django import forms
from django.core.validators import URLValidator, MaxLengthValidator

class ShortenForm(forms.Form):
    url = forms.CharField(
        max_length=512,
        validators=[
            URLValidator(code="invalid")
        ],
        error_messages={
            "required": "Mandatory field",
            "max_length": "URL is too long",
            "invalid": "Invalid URL"
        }
    )