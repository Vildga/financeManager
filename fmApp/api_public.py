from xmlrpc.client import INVALID_XMLRPC

from django.db.models import Sum, Avg, F
from django.db.models.functions import TruncMonth
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from fmApp.models import Transaction
from fmApp.serializers import (
    TotalTransactionsSerializer,
    AverageExpenseByCategorySerializer,
    ExpensesByMonthSerializer,
    ExpenseShareByCategorySerializer,
    IncomeExpenseTrendSerializer
)


class TotalTransactionsAPIView(APIView):
    """API: Загальна сума доходів і витрат всіх користувачів"""

    @swagger_auto_schema(
        operation_summary="Отримати загальну суму доходів і витрат",
        operation_description="Повертає загальні суми доходів і витрат у всіх користувачів у гривнях.",
        responses={200: TotalTransactionsSerializer()},
    )
    def get(self, request):
        total_income = Transaction.objects.filter(category__type="income").aggregate(total=Sum("amount_in_uah"))["total"] or 0
        total_expense = Transaction.objects.filter(category__type="expense").aggregate(total=Sum("amount_in_uah"))["total"] or 0

        data = {"total_income": total_income, "total_expense": total_expense}
        return Response(TotalTransactionsSerializer(data).data)


class AverageExpenseByCategoryAPIView(APIView):
    """API: Середні витрати за категоріями"""

    @swagger_auto_schema(
        operation_summary="Середні витрати по категоріях",
        operation_description="Повертає середню суму витрат на кожну категорію в UAH.",
        responses={200: AverageExpenseByCategorySerializer()}
    )
    def get(self, request):
        expenses = (
            Transaction.objects.filter(category__type="expense")
            .values("category__name")
            .annotate(avg_expense=Avg("amount_in_uah"))
            .order_by("-avg_expense")
        )
        return Response(AverageExpenseByCategorySerializer(expenses, many=True).data)


class ExpensesByMonthAPIView(APIView):
    """API: Загальна сума витрат по місяцях"""

    @swagger_auto_schema(
        operation_summary="Витрати по місяцях",
        operation_description="Повертає загальну суму витрат по всіх користувачах у розрізі місяців.",
        responses={200: ExpensesByMonthSerializer()},
    )
    def get(self, request):
        monthly_expenses = (
            Transaction.objects.filter(category__type="expense")
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_expense=Sum("amount_in_uah"))
            .order_by("month")
        )

        return Response(ExpensesByMonthSerializer(monthly_expenses, many=True).data)


class ExpenseShareByCategoryAPIView(APIView):
    """API: Частка витрат за категоріями"""

    @swagger_auto_schema(
        operation_summary="Частка витрат по категоріях",
        operation_description="Визначає відсоток від усіх витрат, що припадає на кожну категорію.",
        responses={200: ExpenseShareByCategorySerializer()},
    )
    def get(self, request):
        total_expense = Transaction.objects.filter(category__type="expense").aggregate(total=Sum("amount_in_uah"))["total"] or 1

        category_shares = (
            Transaction.objects.filter(category__type="expense")
            .values("category__name")
            .annotate(category_total=Sum("amount_in_uah"))
            .annotate(percentage=F("category_total") * 100 / total_expense)
            .order_by("-percentage")
        )
        return Response(ExpenseShareByCategorySerializer(category_shares, many=True).data)


class IncomeExpenseTrendAPIView(APIView):
    """API: Динаміка змін доходів і витрат"""

    @swagger_auto_schema(
        operation_summary="Динаміка змін доходів і витрат",
        operation_description="Повертає сумарні доходи та витрати по місяцях для аналізу трендів.",
        responses={200: IncomeExpenseTrendSerializer()},
    )
    def get(self, request):
        trends = (
            Transaction.objects.annotate(month=TruncMonth("date"))
            .values("month", "category__type")
            .annotate(total=Sum("amount_in_uah"))
            .order_by("month")
        )

        income_trend = {t["month"].strftime("%Y-%m") if t["month"] else None: t["total"]
                        for t in trends if t["category__type"] == "income"}

        expense_trend = {t["month"].strftime("%Y-%m") if t["month"] else None: t["total"]
                         for t in trends if t["category__type"] == "expense"}

        data = {"income_trend": income_trend, "expense_trend": expense_trend}
        return Response(IncomeExpenseTrendSerializer(data).data)
