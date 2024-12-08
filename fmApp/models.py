from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    class Meta:
        swappable = 'AUTH_USER_MODEL'


class Table(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название таблицы")
    description = models.TextField(verbose_name="Описание")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tables")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="categories")
    type = models.CharField(max_length=10, choices=[('income', 'Доход'), ('expense', 'Расход')], verbose_name="Тип категории")

    def __str__(self):
        return f"{self.name} ({self.type})"
