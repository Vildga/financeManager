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
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View


class HomeView(LoginRequiredMixin, TemplateView):
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


class TableCreateView(LoginRequiredMixin, CreateView):
    model = Table
    form_class = TableForm
    template_name = 'add_table.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TableDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        table_id = request.POST.get('table_id')
        if not table_id:
            return HttpResponseForbidden("Table ID is missing.")

        table = get_object_or_404(Table, id=table_id, user=request.user)
        table.delete()
        return redirect('home')


class TableDetailView(LoginRequiredMixin, DetailView):
    model = Table
    template_name = 'table_detail.html'
    context_object_name = 'table'
    pk_url_kwarg = 'table_id'

    def get_object(self, queryset=None):
        table = get_object_or_404(Table, id=self.kwargs.get('table_id'))
        if table.user != self.request.user:
            return redirect('home')
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = self.get_object()

        context['transactions'] = Transaction.objects.filter(
            category__table=table
        ).order_by('-date')

        context['expense_summary'] = Transaction.objects.filter(
            category__table=table, type='expense'
        ).values('category__name').annotate(total=Sum('amount')).order_by('category__name')

        context['income_summary'] = Transaction.objects.filter(
            category__table=table, type='income'
        ).values('category__name').annotate(total=Sum('amount')).order_by('category__name')

        context['categories'] = Category.objects.filter(table=table)

        context['total_income'] = Transaction.objects.filter(
            category__table=table, type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['total_expense'] = Transaction.objects.filter(
            category__table=table, type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        context['net_total'] = context['total_income'] - context['total_expense']

        return context


class AddTransactionView(LoginRequiredMixin, View):
    def post(self, request, table_id):
        table = get_object_or_404(Table, id=table_id)
        transaction_date = request.POST.get("date")
        transaction_type = request.POST.get("type")
        category_id = request.POST.get("category")
        amount = request.POST.get("amount")
        description = request.POST.get("description")
        category = get_object_or_404(Category, id=category_id)

        Transaction.objects.create(
            date=transaction_date,
            type=transaction_type,
            category=category,
            amount=amount,
            description=description,
            table=table
        )

        return redirect(reverse('table_detail', kwargs={'table_id': table.id}))


class ManageCategoriesView(LoginRequiredMixin, View):
    def post(self, request, table_id):
        table = get_object_or_404(Table, id=table_id)
        category_name = request.POST.get("category_name")
        category_type = request.POST.get("type")
        if category_name and category_type:
            Category.objects.create(name=category_name, type=category_type, table=table)
        return redirect(reverse_lazy("table_detail", kwargs={"table_id": table.id}))

    def get(self, request, table_id):
        table = get_object_or_404(Table, id=table_id)
        categories = table.categories.all()
        return render(request, "manage_categories.html", {"table": table, "categories": categories})


class AddCategoryView(LoginRequiredMixin, View):
    def post(self, request):
        name = request.POST.get("name")
        table_id = request.POST.get("table_id")

        if not table_id:
            messages.error(request, "Table ID is required.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        table = get_object_or_404(Table, id=table_id, user=request.user)

        if name:
            Category.objects.create(name=name, table=table)
            messages.success(request, "Category added successfully!")
        else:
            messages.error(request, "Category name cannot be empty.")

        return redirect(request.META.get('HTTP_REFERER', '/'))



class DeleteCategoryView(LoginRequiredMixin, View):
    def post(self, request, table_id, category_id):
        category = get_object_or_404(Category, id=category_id, table_id=table_id, table__user=request.user)
        category_name = category.name
        category.delete()
        messages.success(request, f"Category '{category_name}' has been deleted.")
        return redirect(request.META.get('HTTP_REFERER', '/'))


class DeleteTransactionView(LoginRequiredMixin, View):
    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id, category__table__user=request.user)
        table_id = transaction.category.table.id
        transaction.delete()
        return redirect(reverse('table_detail', kwargs={'table_id': table_id}))


class LoadDefaultCategoriesView(LoginRequiredMixin, View):
    default_categories = [
        {"name": "Продукти", "type": "expense"},
        {"name": "Кафе", "type": "expense"},
        {"name": "Подарунки", "type": "expense"},
        {"name": "Моб. зв'язок", "type": "expense"},
        {"name": "Транспорт", "type": "expense"},
        {"name": "Переказ", "type": "expense"},
        {"name": "Зал", "type": "expense"},
        {"name": "Розваги", "type": "expense"},
        {"name": "Підписки", "type": "expense"},
        {"name": "Ремонт", "type": "expense"},
        {"name": "Аптека", "type": "expense"},
        {"name": "Косметика", "type": "expense"},
        {"name": "Інше", "type": "expense"},
        {"name": "Комунальні послуги", "type": "expense"},
        {"name": "Лікарня", "type": "expense"},
        {"name": "Шопінг", "type": "expense"},
        {"name": "Б'юті", "type": "expense"},
        {"name": "Неспішні покупки", "type": "expense"},
        {"name": "Стоянка", "type": "expense"},
        {"name": "Переказ", "type": "income"},
        {"name": "Депозит", "type": "income"},
        {"name": "Робота", "type": "income"},
    ]

    def post(self, request, table_id):
        table = get_object_or_404(Table, id=table_id, user=request.user)
        existing_categories = set(Category.objects.filter(table=table).values_list("name", flat=True))
        new_categories = [
            Category(name=cat["name"], type=cat["type"], table=table)
            for cat in self.default_categories if cat["name"] not in existing_categories
        ]

        if new_categories:
            Category.objects.bulk_create(new_categories)
            messages.success(request, "Standard categories have been loaded successfully.")
        else:
            messages.info(request, "All default categories are already added.")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class EditTransactionView(LoginRequiredMixin, View):
    def post(self, request):
        transaction_id = request.POST.get('transaction_id')
        transaction = get_object_or_404(Transaction, id=transaction_id, category__table__user=request.user)
        transaction.date = request.POST.get('date')
        transaction.category_id = request.POST.get('category_id')
        transaction.type = request.POST.get('type')
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')
        transaction.save()
        return redirect(reverse('table_detail', kwargs={'table_id': transaction.category.table.id}))


class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
