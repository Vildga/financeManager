from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import (
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy

from django.utils.timezone import now
from django.utils.translation import activate
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView, DetailView, TemplateView, DeleteView, UpdateView

from fmApp.utils import get_exchange_rate
from users.models import CustomUser

from .forms import LanguageForm, TableForm, CategoryForm
from .models import Category, Table, Transaction
from .permissions import IsTableOwnerMixin
from django.db.models import Max


MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


DEFAULT_CATEGORIES = [
    ("Groceries", "expense"), ("Cafe", "expense"), ("Gifts", "expense"),
    ("Mobile Connection", "expense"), ("Transport", "expense"), ("Transfer", "expense"),
    ("Gym", "expense"), ("Entertainment", "expense"), ("Subscriptions", "expense"),
    ("Repairs", "expense"), ("Pharmacy", "expense"), ("Cosmetics", "expense"),
    ("Other", "expense"), ("Utility Bills", "expense"), ("Hospital", "expense"),
    ("Shopping", "expense"), ("Beauty", "expense"), ("Planned Purchases", "expense"),
    ("Parking", "expense"), ("Transfer", "income"), ("Deposit", "income"),
    ("Salary", "income"),
]


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tables"] = Table.objects.filter(user=self.request.user)
        context["form"] = TableForm()
        return context

    def post(self, request, *args, **kwargs):
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.user = request.user
            table.save()
            return redirect("home")
        return self.get(request, *args, **kwargs)


class TableCreateView(CreateView):
    model = Table
    form_class = TableForm
    template_name = "modals/add_transaction_modal.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TableDeleteView(View):
    def post(self, request, *args, **kwargs):
        table_id = request.POST.get("table_id")
        if not table_id:
            return HttpResponseForbidden("Table ID is missing.")

        table = get_object_or_404(Table, id=table_id, user=request.user)
        table.delete()
        return redirect("home")


class TableDetailView(IsTableOwnerMixin, DetailView):
    model = Table
    template_name = "table_detail.html"
    context_object_name = "table"
    pk_url_kwarg = "table_id"

    # Ці змінні будемо виставляти в dispatch
    table = None
    selected_month = None
    selected_year = None

    def dispatch(self, request, *args, **kwargs):
        self.table = self.get_object()
        result = self._get_month_and_year_from_request(request)
        # якщо result – це HttpResponseRedirect, повертаймо його:
        if isinstance(result, HttpResponseRedirect):
            return result

        self.selected_month, self.selected_year = result

        if not self._has_transactions_for_month():
            last_date = self._get_last_transaction_date()
            if last_date:
                return self._redirect_to(last_date.month, last_date.year)

        return super().dispatch(request, *args, **kwargs)

    def _get_month_and_year_from_request(self, request):
        """
        Повертає (month, year) з GET-параметрів або виставляє поточні.
        Якщо їх немає, робимо редирект із доданими параметрами.
        """
        query_params = request.GET.copy()

        month = query_params.get("month")
        year = query_params.get("year")
        current_month = now().month
        current_year = now().year

        if not month or not year:
            # Робимо редірект на поточний місяць/рік
            query_params["month"] = str(current_month)
            query_params["year"] = str(current_year)
            return self._redirect_to_month_year_instant(request, query_params)

        # Якщо GET передав якісь значення, конвертуємо в int
        try:
            month_int = int(month)
            year_int = int(year)
        except ValueError:
            month_int = current_month
            year_int = current_year

        return month_int, year_int


    def _redirect_to_month_year_instant(self, request, query_params):
        url = f"{request.path}?{query_params.urlencode()}"
        # Просто повертаємо redirect тут, і все
        return redirect(url)

    def _has_transactions_for_month(self):
        """
        Перевіряє, чи є транзакції за self.selected_month, self.selected_year.
        """
        return Transaction.objects.filter(
            table=self.table,
            date__year=self.selected_year,
            date__month=self.selected_month
        ).exists()

    def _get_last_transaction_date(self):
        """
        Повертає max(date) для таблиці або None, якщо транзакцій немає.
        """
        result = Transaction.objects.filter(table=self.table).aggregate(last_date=Max("date"))
        return result["last_date"]

    def _redirect_to(self, month, year):
        """Редіректить на той самий URL, але з переданими month/year."""
        query_params = self.request.GET.copy()
        query_params["month"] = str(month)
        query_params["year"] = str(year)
        url = f"{self.request.path}?{query_params.urlencode()}"
        return redirect(url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # table уже збережений у self.table
        # selected_month/selected_year уже парсені
        transactions = (
            Transaction.objects
            .filter(
                table=self.table,
                date__year=self.selected_year,
                date__month=self.selected_month
            )
            .prefetch_related("category")
        )

        user_categories = Category.objects.filter(user=self.request.user)

        summaries = (
            transactions
            .values("category__name", "category__type")
            .annotate(total=Sum("amount_in_uah"))
            .order_by("category__name")
        )

        for summary in summaries:
            # Захист від None
            cat_name = summary["category__name"] or ""
            summary["category__name"] = _(cat_name)
            total_str = summary["total"] or 0
            summary["total"] = Decimal(str(total_str).replace(",", "."))

        income_summary = [s for s in summaries if s["category__type"] == "income"]
        expense_summary = [s for s in summaries if s["category__type"] == "expense"]

        totals = {
            "income": sum(s["total"] for s in income_summary),
            "expense": sum(s["total"] for s in expense_summary),
        }

        # Дістаємо усі доступні (рік, місяць) для цієї таблиці
        available_years_months = (
            Transaction.objects.filter(table=self.table)
            .annotate(year=ExtractYear("date"), month=ExtractMonth("date"))
            .values("year", "month")
            .distinct()
            .order_by("-year", "month")
        )

        available_years = sorted({item["year"] for item in available_years_months}, reverse=True)
        months_same_year = [item["month"] for item in available_years_months if item["year"] == self.selected_year]
        available_months = sorted(months_same_year)
        available_months = [
            {"month": m, "month_name": MONTH_NAMES[m]} for m in available_months
        ]

        context.update({
            "transactions": transactions,
            "categories": user_categories,
            "expense_summary": expense_summary,
            "income_summary": income_summary,
            "total_income": totals["income"],
            "total_expense": totals["expense"],
            "net_total": totals["income"] - totals["expense"],
            "selected_month": self.selected_month,
            "selected_year": self.selected_year,
            "available_months": available_months,
            "available_years": available_years,
            "month_names": MONTH_NAMES,
            "currency_choices": Transaction.CurrencyChoices.choices,
        })
        return context


class RedirectNow(Exception):
    """
    Власний виняток, щоб припинити процес і зробити редірект "до того, як"
    базовий class-based view встигне викликати get_context_data.

    Суть: в _redirect_to_month_year_instant() замість return redirect(),
    кинемо RedirectNow, який перехопимо у dispatch().
    """

# У dispatch для обробки:
def dispatch(self, request, *args, **kwargs):
    try:
        self.table = self.get_object()
        self.selected_month, self.selected_year = self._get_month_and_year_from_request(request)
        if not self._has_transactions_for_month():
            ...
    except RedirectNow as exc:
        return redirect(str(exc))
    return super().dispatch(request, *args, **kwargs)


class AddTransactionView(IsTableOwnerMixin, View):
    def post(self, request, table_id):

        table = get_object_or_404(Table, id=table_id)

        transaction_date = request.POST.get("date")
        category_ids = request.POST.getlist("category")
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        currency = request.POST.get("currency", "UAH")

        if not category_ids:
            messages.error(request, _("You must select at least one category."))
            return redirect(reverse("table_detail", kwargs={"table_id": table.id}))

        categories = list(Category.objects.filter(id__in=category_ids))

        if not categories:
            messages.error(request, _("Selected categories do not exist."))
            return redirect(reverse("table_detail", kwargs={"table_id": table.id}))

        with transaction.atomic():
            exchange_rate = Decimal(get_exchange_rate(currency, transaction_date))

            if exchange_rate is None:
                messages.error(
                    request, _("Failed to retrieve exchange rate. Please try again.")
                )
                return redirect(reverse("table_detail", kwargs={"table_id": table.id}))

            amount_decimal = Decimal(amount)
            amount_in_uah = amount_decimal * exchange_rate

            new_transaction = Transaction.objects.create(
                date=transaction_date,
                amount=amount,
                amount_in_uah=amount_in_uah,
                currency=currency,
                exchange_rate=exchange_rate,
                description=description,
                table=table,
            )
            new_transaction.category.add(*categories)

        messages.success(request, _("Transaction added successfully."))
        return redirect(reverse("table_detail", kwargs={"table_id": table.id}))


class DeleteTransactionView(View):
    def post(self, request, transaction_id):
        transaction = get_object_or_404(
            Transaction, id=transaction_id, table__user=request.user
        )
        table_id = transaction.table.id
        transaction.delete()
        return HttpResponseRedirect(
            reverse("table_detail", kwargs={"table_id": table_id})
        )


class EditTransactionView(View):
    def post(self, request):
        transaction_id = request.POST.get("transaction_id")
        transaction = get_object_or_404(
            Transaction, id=transaction_id, table__user=request.user
        )

        transaction.date = request.POST.get("date")
        new_amount = request.POST.get("amount")
        transaction.description = request.POST.get("description")
        new_currency = request.POST.get("currency", transaction.currency)

        category_id = request.POST.get("category_id")
        category = get_object_or_404(Category, id=category_id)

        transaction.category.set([category])

        if new_currency != transaction.currency or new_amount != transaction.amount:
            exchange_rate = get_exchange_rate(new_currency, transaction.date)

            if exchange_rate is None:
                exchange_rate = Decimal("1.00")

            transaction.currency = new_currency
            transaction.amount = new_amount
            transaction.exchange_rate = exchange_rate
            transaction.amount_in_uah = Decimal(new_amount) * Decimal(exchange_rate)

        transaction.save()

        return redirect(
            reverse("table_detail", kwargs={"table_id": transaction.table.id})
        )


class AboutView(View):
    def get(self, request):
        return render(request, "about.html")


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


class AvailableMonthsView(View):
    def get(self, request, *args, **kwargs):
        year = request.GET.get("year")

        if not year or not year.isdigit():
            return JsonResponse({"months": []})

        months = (
            Transaction.objects.filter(date__year=int(year))
            .annotate(month=ExtractMonth("date"))
            .values("month")
            .distinct()
            .order_by("month")
        )

        months_list = [
            {"month": m["month"], "month_name": MONTH_NAMES[m["month"]]} for m in months
        ]

        return JsonResponse({"months": months_list})


class SettingsView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = LanguageForm
    template_name = "settings.html"
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["django_language"] = self.request.user.language
        activate(self.request.user.language)
        return response

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            activate(request.user.language)
            request.session["django_language"] = request.user.language

        category_form = CategoryForm()
        categories = Category.objects.filter(user=request.user)
        return render(request, self.template_name, {
            "form": self.get_form(),
            "category_form": category_form,
            "categories": categories,
            "current_language": self.request.user.language,
        })

    def post(self, request, *args, **kwargs):
        if "add_category" in request.POST:
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category = category_form.save(commit=False)
                category.user = request.user

                existing_category = Category.objects.filter(
                    name=category.name, type=category.type, user=request.user
                ).exists()

                if existing_category:
                    messages.warning(request, "Ця категорія вже існує!")
                else:
                    category.save()
                    messages.success(request, "Категорію успішно додано!")

            return redirect("settings")

        return super().post(request, *args, **kwargs)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        return get_object_or_404(Category, id=self.kwargs["pk"], user=self.request.user)

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CategoryAddView(CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('settings')

    def form_valid(self, form):
        category = form.save()
        return JsonResponse({
            'success': True,
            'category_id': category.id,
            'category_name': category.name,
            'category_type': category.get_type_display(),
            'message': _("Category added successfully!")
        })

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


def load_default_categories(request):
    if request.method == "POST":
        created_count = 0

        for name, cat_type in DEFAULT_CATEGORIES:
            category, created = Category.objects.get_or_create(name=name, type=cat_type, user=request.user)
            if created:
                created_count += 1

    return redirect("settings")
