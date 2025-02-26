from django import forms

from users.models import CustomUser

from .models import Category, Table


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ["name", "description"]


class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.SelectDateWidget())
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Category
        fields = ["date", "type", "amount"]


class LanguageForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["language"]
        widgets = {"language": forms.Select(attrs={"class": "form-select"})}
