from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control"}))
    first_name = forms.CharField(label="Ім'я", max_length=30, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(label="Прізвище", max_length=30, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "password1", "password2"]

class CustomUserLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}))
