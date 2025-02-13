from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    class Meta:
        swappable = 'AUTH_USER_MODEL'


class Category(models.Model):

    class TypeChoices(models.TextChoices):
        INCOME = "income", "Дохід"
        EXPENSE = "expense", "Витрата"

    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    type = models.CharField(max_length=10, choices=TypeChoices.choices, verbose_name="Тип категорії")

    class Meta:
        unique_together = ('name', 'type')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.type})"


class Table(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва таблиці")
    description = models.TextField(verbose_name="Опис", blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tables")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):

    class CurrencyChoices(models.TextChoices):
            UAH = 'UAH', 'Гривня'
            USD = 'USD', 'Долар'
            EUR = 'EUR', 'Євро'

    category = models.ManyToManyField(Category, related_name="transactions")
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default='UAH')
    amount_in_uah = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)


    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.amount} {self.currency} ({self.amount_in_uah} UAH) on {self.date}"
