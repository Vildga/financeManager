from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
# from .forms import RegistrationForm
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import TableForm
from .models import Table
from django.shortcuts import render, get_object_or_404
from .models import Table, Category, Transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View
from .permissions import IsTableOwnerMixin
from django.db.models import Sum, Case, When, Value, DecimalField, F
from django.db import transaction
from django.utils.timezone import now
from django.db.models.functions import ExtractYear, ExtractMonth


MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tables'] = Table.objects.filter(user=self.request.user)
        context['form'] = TableForm()
        return context

    def post(self, request, *args, **kwargs):
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.user = request.user
            table.save()
            return redirect('home')
        return self.get(request, *args, **kwargs)


class TableCreateView(CreateView):
    model = Table
    form_class = TableForm
    template_name = 'modals/add_transaction_modal.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TableDeleteView(View):
    def post(self, request, *args, **kwargs):
        table_id = request.POST.get('table_id')
        if not table_id:
            return HttpResponseForbidden("Table ID is missing.")

        table = get_object_or_404(Table, id=table_id, user=request.user)
        table.delete()
        return redirect('home')


class TableDetailView(IsTableOwnerMixin, DetailView):
    model = Table
    template_name = 'table_detail.html'
    context_object_name = 'table'
    pk_url_kwarg = 'table_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.get_object()

        selected_month = self.request.GET.get('month')
        selected_year = self.request.GET.get('year')

        selected_month = int(selected_month) if selected_month and selected_month.isdigit() else now().month
        selected_year = int(selected_year) if selected_year and selected_year.isdigit() else now().year

        transactions = (
            Transaction.objects
            .filter(table=table, date__year=selected_year, date__month=selected_month)
            .prefetch_related("category")
        )

        summaries = (
            transactions
            .values("category__name", "category__type")
            .annotate(total=Sum("amount"))
            .order_by("category__name")
        )

        income_summary = [s for s in summaries if s["category__type"] == "income"]
        expense_summary = [s for s in summaries if s["category__type"] == "expense"]

        totals = {"income": 0, "expense": 0}
        for t in transactions.values("category__type").annotate(total=Sum("amount")):
            totals[t["category__type"]] = t["total"]

        available_years = list(
            Transaction.objects
            .filter(table=table)
            .annotate(year=ExtractYear("date"))
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )

        available_months = list(
            Transaction.objects
            .filter(table=table, date__year=selected_year)
            .annotate(month=ExtractMonth("date"))
            .values_list("month", flat=True)
            .distinct()
            .order_by("month")
        )

        available_months = [{"month": m, "month_name": MONTH_NAMES[m]} for m in available_months]

        context.update({
            "transactions": transactions,
            "categories": Category.objects.all(),
            "expense_summary": expense_summary,
            "income_summary": income_summary,
            "total_income": totals["income"],
            "total_expense": totals["expense"],
            "net_total": totals["income"] - totals["expense"],
            "selected_month": selected_month,
            "selected_year": selected_year,
            "available_months": available_months,
            "available_years": available_years,
            "month_names": MONTH_NAMES,
        })

        return context


class AddTransactionView(IsTableOwnerMixin, View):
    def post(self, request, table_id):

        table = self.get_table()

        transaction_date = request.POST.get("date")
        category_ids = request.POST.getlist("category")
        amount = request.POST.get("amount")
        description = request.POST.get("description")

        if not category_ids:
            messages.error(request, "You must select at least one category.")
            return redirect(reverse('table_detail', kwargs={'table_id': table.id}))

        categories = list(Category.objects.filter(id__in=category_ids))

        if not categories:
            messages.error(request, "Selected categories do not exist.")
            return redirect(reverse('table_detail', kwargs={'table_id': table.id}))

        with transaction.atomic():
            new_transaction = Transaction.objects.create(
                date=transaction_date,
                amount=amount,
                description=description,
                table=table
            )
            new_transaction.category.add(*categories)

        messages.success(request, "Transaction added successfully.")
        return redirect(reverse('table_detail', kwargs={'table_id': table.id}))


class DeleteTransactionView(LoginRequiredMixin, View):
    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id, table__user=request.user)
        table_id = transaction.table.id
        transaction.delete()
        return HttpResponseRedirect(reverse('table_detail', kwargs={'table_id': table_id}))




class EditTransactionView(LoginRequiredMixin, View):
    def post(self, request):
        transaction_id = request.POST.get('transaction_id')
        transaction = get_object_or_404(Transaction, id=transaction_id, table__user=request.user)

        transaction.date = request.POST.get('date')
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')

        category_id = request.POST.get('category_id')
        category = get_object_or_404(Category, id=category_id)

        transaction.category.set([category])
        transaction.save()

        return redirect(reverse('table_detail', kwargs={'table_id': transaction.table.id}))


class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)


class AvailableMonthsView(View):
    def get(self, request, *args, **kwargs):
        year = request.GET.get("year")

        if not year or not year.isdigit():
            return JsonResponse({"months": []})

        months = (
            Transaction.objects
            .filter(date__year=int(year))
            .annotate(month=ExtractMonth("date"))
            .values("month")
            .distinct()
            .order_by("month")
        )

        months_list = [{"month": m["month"], "month_name": MONTH_NAMES[m["month"]]} for m in months]

        return JsonResponse({"months": months_list})
