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

        transactions = (
            Transaction.objects
            .filter(table=table)
            .prefetch_related("category")
        )

        income_summary = (
            transactions
            .filter(category__type="income")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("category__name")
        )

        expense_summary = (
            transactions
            .filter(category__type="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("category__name")
        )

        total_income = transactions.filter(category__type="income").aggregate(total=Sum("amount"))["total"] or 0
        total_expense = transactions.filter(category__type="expense").aggregate(total=Sum("amount"))["total"] or 0

        context.update({
            "transactions": transactions,
            "categories": Category.objects.all(),
            "expense_summary": expense_summary,
            "income_summary": income_summary,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_total": total_income - total_expense,
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
