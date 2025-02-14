from django.db.models import Sum, Avg, F
from django.db.models.functions import TruncMonth
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from fmApp.models import Transaction


class TotalTransactionsAPIView(APIView):
    """API: Загальна сума доходів і витрат всіх користувачів"""

    @swagger_auto_schema(
        operation_summary="Отримати загальну суму доходів і витрат",
        operation_description="Повертає загальні суми доходів і витрат у всіх користувачів у гривнях.",
        responses={200: openapi.Response("JSON з total_income та total_expense")}
    )
    def get(self, request):
        total_income = Transaction.objects.filter(category__type="income").aggregate(total=Sum("amount_in_uah"))["total"] or 0
        total_expense = Transaction.objects.filter(category__type="expense").aggregate(total=Sum("amount_in_uah"))["total"] or 0

        return Response({"total_income": total_income, "total_expense": total_expense})


class AverageExpenseByCategoryAPIView(APIView):
    """API: Середні витрати за категоріями"""

    @swagger_auto_schema(
        operation_summary="Середні витрати по категоріях",
        operation_description="Повертає середню суму витрат на кожну категорію в UAH.",
        responses={200: openapi.Response("JSON зі списком категорій і середніми витратами")}
    )
    def get(self, request):
        expenses = (
            Transaction.objects.filter(category__type="expense")
            .values("category__name")
            .annotate(avg_expense=Avg("amount_in_uah"))
            .order_by("-avg_expense")
        )
        return Response({"average_expense_by_category": list(expenses)})


class ExpensesByMonthAPIView(APIView):
    """API: Загальна сума витрат по місяцях"""

    @swagger_auto_schema(
        operation_summary="Витрати по місяцях",
        operation_description="Повертає загальну суму витрат по всіх користувачах у розрізі місяців.",
        responses={200: openapi.Response("JSON зі списком місяців і загальними витратами")}
    )
    def get(self, request):
        monthly_expenses = (
            Transaction.objects.filter(category__type="expense")
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_expense=Sum("amount_in_uah"))
            .order_by("month")
        )

        return Response({"expenses_by_month": list(monthly_expenses)})


class ExpenseShareByCategoryAPIView(APIView):
    """API: Частка витрат за категоріями"""

    @swagger_auto_schema(
        operation_summary="Частка витрат по категоріях",
        operation_description="Визначає відсоток від усіх витрат, що припадає на кожну категорію.",
        responses={200: openapi.Response("JSON з частками витрат по категоріях")}
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
        return Response({"expense_share_by_category": list(category_shares)})


class IncomeExpenseTrendAPIView(APIView):
    """API: Динаміка змін доходів і витрат"""

    @swagger_auto_schema(
        operation_summary="Динаміка змін доходів і витрат",
        operation_description="Повертає сумарні доходи та витрати по місяцях для аналізу трендів.",
        responses={200: openapi.Response("JSON з тенденціями доходів і витрат")}
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

        return Response({
            "income_trend": income_trend,
            "expense_trend": expense_trend
        })
