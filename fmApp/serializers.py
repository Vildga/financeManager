from rest_framework import serializers

from .models import Category, Table, Transaction


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ["id", "name", "description", "user"]
        read_only_fields = ["id", "user"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type"]


class TransactionSerializer(serializers.ModelSerializer):
    description = serializers.CharField(allow_blank=True, required=False)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True, source="category"
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "date",
            "category",
            "category_id",
            "type",
            "amount",
            "description",
        ]


class TotalTransactionsSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(decimal_places=2, max_digits=10)
    total_expense = serializers.DecimalField(decimal_places=2, max_digits=10)


class AverageExpenseByCategorySerializer(serializers.Serializer):
    category_name = serializers.CharField(source="category__name")
    avg_expense = serializers.DecimalField(decimal_places=2, max_digits=10)


class ExpensesByMonthSerializer(serializers.Serializer):
    month = serializers.DateField(format="%Y-%m")
    total_expense = serializers.DecimalField(decimal_places=2, max_digits=10)


class ExpenseShareByCategorySerializer(serializers.Serializer):
    category_name = serializers.CharField(source="category__name")
    category_total = serializers.DecimalField(decimal_places=2, max_digits=10)
    percentage = serializers.FloatField()


class IncomeExpenseTrendSerializer(serializers.Serializer):
    income_trend = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
    expense_trend = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )
