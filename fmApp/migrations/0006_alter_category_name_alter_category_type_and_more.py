# Generated by Django 4.2.19 on 2025-02-18 09:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fmApp", "0005_alter_category_name_alter_category_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=100, verbose_name="Назва категорії"),
        ),
        migrations.AlterField(
            model_name="category",
            name="type",
            field=models.CharField(
                choices=[("income", "Дохід"), ("expense", "Витрата")],
                max_length=10,
                verbose_name="Тип категорії",
            ),
        ),
        migrations.AlterField(
            model_name="table",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Опис"),
        ),
        migrations.AlterField(
            model_name="table",
            name="name",
            field=models.CharField(max_length=100, verbose_name="Назва таблиці"),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="amount_in_uah",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="category",
            field=models.ManyToManyField(
                related_name="transactions", to="fmApp.category"
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="currency",
            field=models.CharField(
                choices=[("UAH", "Гривня"), ("USD", "Долар"), ("EUR", "Євро")],
                default="UAH",
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="date",
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="exchange_rate",
            field=models.DecimalField(
                blank=True, decimal_places=4, max_digits=10, null=True
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="table",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="fmApp.table"
            ),
        ),
    ]
