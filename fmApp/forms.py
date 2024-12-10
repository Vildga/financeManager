from django import forms
from django.contrib.auth.models import User
from .models import Table, Category


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'description']


class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget())
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Category
        fields = ['date', 'type', 'amount']