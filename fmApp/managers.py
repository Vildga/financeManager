from django.db import models
from django.db.models import Sum, Avg, F
from django.db.models.functions import TruncMonth


class TransactionManager(models.Manager):

    def get_total_income_expense(self):
        """Загальна суму доходів і витрат у гривнях"""

        return self.get_queryset().aggregate(
            total_income=Sum("amount_in_uah", filter=models.Q(category__type="income")) or 0,
            total_expense=Sum("amount_in_uah", filter=models.Q(category__type="expense")) or 0
        )

    def get_average_expense_by_category(self):
        """Cередні витрати за категоріями"""

        return (
            self.get_queryset()
            .filter(category__type="expense")
            .values("category__name")
            .annotate(avg_expense=Avg("amount_in_uah"))
            .order_by("-avg_expense")
        )


    def get_expenses_by_month(self):
        """Загальна сума витрат по місяцях"""

        return (
            self.get_queryset()
            .filter(category__type="expense")
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total_expense=Sum("amount_in_uah"))
            .order_by("month")
        )

    def get_expense_share_by_category(self):
        """Частка витрат по категоріях"""

        total_expense = self.get_queryset().filter(category__type="expense").aggregate(
            total=Sum("amount_in_uah")
        )["total"] or 1

        return (
            self.get_queryset()
            .filter(category__type="expense")
            .values("category__name")
            .annotate(category_total=Sum("amount_in_uah"))
            .annotate(percentage=F("category_total") * 100 / total_expense)
            .order_by("-percentage")
        )

    def get_income_expense_trend(self):
        """Динаміка змін доходів і витрат"""

        trends = (
            self.get_queryset()
            .annotate(month=TruncMonth("date"))
            .values("month", "category__type")
            .annotate(total=Sum("amount_in_uah"))
            .order_by("month")
        )

        income_trend = {t["month"].strftime("%Y-%m"): t["total"] for t in trends if t["category__type"] == "income"}
        expense_trend = {t["month"].strftime("%Y-%m"): t["total"] for t in trends if t["category__type"] == "expense"}

        return {"income_trend": income_trend, "expense_trend": expense_trend}