from django import forms
from django.core.validators import URLValidator, RegexValidator
from django.core.exceptions import ValidationError

class ShortenForm(forms.Form):
    url = forms.CharField(
        max_length=512,
        validators=[
            URLValidator(code="invalid")
        ],
        error_messages={
            "required": "Please provide an URL",
            "max_length": "URL is too long, it must be less than 512 characters",
            "invalid": "Invalid URL"
        }
    )

class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=4,
        max_length=32,
        validators=[
            RegexValidator("^[-a-zA-Z0-9_@\+. ]*$", code="invalid")
        ],
        error_messages={
            "required": "Please provide an username",
            "min_length": "Username must be between 4 and 32 characters",
            "max_length": "Username must be between 4 and 32 characters",
            "invalid": "This username contains invalid caracters"
        }
    )
    password = forms.CharField(
        min_length=8,
        max_length=32,
        validators=[
            RegexValidator("^[-a-zA-Z0-9@:%_\+~#=.,!~?&\*]*$", code="invalid")
        ],
        error_messages={
            "required": "Please provide a password",
            "min_length": "Password must be between 8 and 32 characters",
            "max_length": "Password must be between 8 and 32 characters",
            "invalid": "This password contains invalid caracters"
        }
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        min_length=4,
        max_length=32,
        validators=[
            RegexValidator("^[-a-zA-Z0-9_@\+. ]*$", code="invalid")
        ],
        error_messages={
            "required": "Please provide an username",
            "min_length": "Username must be between 4 and 32 characters",
            "max_length": "Username must be between 4 and 32 characters",
            "invalid": "This username contains invalid caracters"
        }
    )
    password = forms.CharField(
        min_length=8,
        max_length=32,
        validators=[
            RegexValidator("^[-a-zA-Z0-9@:%_\+~#=.,!~?&\*]*$", code="invalid")
        ],
        error_messages={
            "required": "Please provide a password",
            "min_length": "Password must be between 8 and 32 characters",
            "max_length": "Password must be between 8 and 32 characters",
            "invalid": "This password contains invalid caracters"
        }
    )
    confirm_password = forms.CharField(
        min_length=8,
        max_length=32,
        error_messages={
            "required": "Please provide a password"
        }
    )

    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]

        if password != confirm_password:
            raise ValidationError("Confirmation password does not match", code="not_matching")
        return confirm_password