from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms


class UserAdminCreationForm(UserCreationForm):
    """
    A Custom form for creating new users.
    """
    password1 = forms.CharField(
    label="Heslo",
    strip=False,
    widget=forms.PasswordInput,
    help_text="Minimálně 8 znaků, kombinace malé velké písmeno a číslo"
    )
    password2 = forms.CharField(
    label="Heslo znovu",
    strip=False,
    widget=forms.PasswordInput
    )
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name']
        labels = {'email': 'Email', 'first_name' : 'Jméno', 'last_name' : 'Příjmení'}

class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        fields = ["email", "password"]
