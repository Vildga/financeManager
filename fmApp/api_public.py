from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from fmApp.models import Transaction
from fmApp.serializers import (
    AverageExpenseByCategorySerializer,
    ExpensesByMonthSerializer,
    ExpenseShareByCategorySerializer,
    IncomeExpenseTrendSerializer,
    TotalTransactionsSerializer,
)


class TotalTransactionsAPIView(APIView):
    """API: Загальна сума доходів і витрат всіх користувачів"""

    @swagger_auto_schema(
        operation_summary="Отримати загальну суму доходів і витрат",
        operation_description="Повертає загальні суми доходів і витрат у всіх користувачів у гривнях.",
        responses={200: TotalTransactionsSerializer()},
    )
    def get(self, request):
        data = Transaction.my_manager.get_total_income_expense()
        return Response(TotalTransactionsSerializer(data).data)


class AverageExpenseByCategoryAPIView(APIView):
    """API: Середні витрати за категоріями"""

    @swagger_auto_schema(
        operation_summary="Середні витрати по категоріях",
        operation_description="Повертає середню суму витрат на кожну категорію в UAH.",
        responses={200: AverageExpenseByCategorySerializer()},
    )
    def get(self, request):
        expenses = Transaction.my_manager.get_average_expense_by_category()
        return Response(AverageExpenseByCategorySerializer(expenses, many=True).data)


class ExpensesByMonthAPIView(APIView):
    """API: Загальна сума витрат по місяцях"""

    @swagger_auto_schema(
        operation_summary="Витрати по місяцях",
        operation_description="Повертає загальну суму витрат по всіх користувачах у розрізі місяців.",
        responses={200: ExpensesByMonthSerializer()},
    )
    def get(self, request):
        monthly_expenses = Transaction.my_manager.get_expenses_by_month()
        return Response(ExpensesByMonthSerializer(monthly_expenses, many=True).data)


class ExpenseShareByCategoryAPIView(APIView):
    """API: Частка витрат за категоріями"""

    @swagger_auto_schema(
        operation_summary="Частка витрат по категоріях",
        operation_description="Визначає відсоток від усіх витрат, що припадає на кожну категорію.",
        responses={200: ExpenseShareByCategorySerializer()},
    )
    def get(self, request):
        category_shares = Transaction.my_manager.get_expense_share_by_category()
        return Response(
            ExpenseShareByCategorySerializer(category_shares, many=True).data
        )


class IncomeExpenseTrendAPIView(APIView):
    """API: Динаміка змін доходів і витрат"""

    @swagger_auto_schema(
        operation_summary="Динаміка змін доходів і витрат",
        operation_description="Повертає сумарні доходи та витрати по місяцях для аналізу трендів.",
        responses={200: IncomeExpenseTrendSerializer()},
    )
    def get(self, request):
        trends = Transaction.my_manager.get_income_expense_trend()
        return Response(IncomeExpenseTrendSerializer(trends).data)
