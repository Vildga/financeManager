from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import TableForm
from .models import Table
from django.shortcuts import render, get_object_or_404
from .models import Table, Category, Transaction
from django.db.models import Sum


@login_required
def home(request):
    tables = Table.objects.filter(user=request.user)
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.user = request.user
            table.save()
            return redirect('home')
    else:
        form = TableForm()

    return render(request, 'home.html', {'tables': tables, 'form': form})


def user_login(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'You have successfully logged in.')
                return redirect('home')  # Убедитесь, что маршрут 'home' существует
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Error in form submission. Please try again.')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Указываем бэкенд аутентификации
            backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)

            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})


@login_required
def add_table(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.user = request.user
            table.save()
            return redirect('home')  # Перенаправление на главную страницу или другую нужную
    else:
        form = TableForm()



@login_required
def delete_table(request):
    if request.method == "POST":
        table_id = request.POST.get('table_id')
        if not table_id:
            return HttpResponseForbidden("Table ID is missing.")

        table = get_object_or_404(Table, id=table_id, user=request.user)
        table.delete()
        return redirect('home')
    return HttpResponseForbidden("Invalid request method.")


@login_required
def table_detail(request, table_id):
    # Получаем таблицу
    table = get_object_or_404(Table, id=table_id)

    # Проверяем, принадлежит ли таблица текущему пользователю
    if table.user != request.user:
        # Если не принадлежит, перенаправляем на главную страницу или другую страницу
        return redirect('home')  # Замените 'home' на URL-имя вашей страницы

    # Получаем все транзакции для этой таблицы, сортируя по дате (по убыванию)
    transactions = Transaction.objects.filter(category__table=table).order_by('-date')

    # Агрегируем расходы по категориям
    expense_summary = Transaction.objects.filter(
        category__table=table,
        type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('category__name')

    # Агрегируем доходы по категориям
    income_summary = Transaction.objects.filter(
        category__table=table,
        type='income'
    ).values('category__name').annotate(total=Sum('amount')).order_by('category__name')

    # Категории для выпадающего списка в форме
    categories = Category.objects.filter(table=table)

    # Общая сумма доходов и расходов
    total_income = Transaction.objects.filter(
        category__table=table, type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expense = Transaction.objects.filter(
        category__table=table, type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    net_total = total_income - total_expense

    context = {
        'table': table,
        'transactions': transactions,
        'expense_summary': expense_summary,
        'income_summary': income_summary,
        'categories': categories,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_total': net_total,
    }

    return render(request, 'table_detail.html', context)


def add_transaction(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    if request.method == "POST":
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
        return redirect("table_detail", table_id=table.id)

    categories = Category.objects.filter(table=table)
    return render(request, "table_detail.html", {"table": table, "categories": categories})


def manage_categories(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        category_type = request.POST.get("type")

        if category_name and category_type:
            Category.objects.create(name=category_name, type=category_type, table=table)
        return redirect("table_detail", table_id=table.id)

    categories = table.categories.all()
    return render(request, "manage_categories.html", {"table": table, "categories": categories})


def add_category(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            messages.success(request, "Category added successfully!")
        else:
            messages.error(request, "Category name cannot be empty.")
        return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_category(request, table_id, category_id):
    if request.method == "POST":
        category = get_object_or_404(Category, id=category_id, table_id=table_id)
        category_name = category.name
        category.delete()
        messages.success(request, f"Category '{category_name}' has been deleted.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_transaction(request, transaction_id):
    # Получаем транзакцию по ID
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == 'POST':
        # Удаляем транзакцию
        transaction.delete()
        # Перенаправляем пользователя на страницу с таблицей транзакций
        return redirect('table_detail', table_id=transaction.category.table.id)

    # В случае GET запроса (например, если мы не подтверждаем удаление)
    return redirect('table_detail', table_id=transaction.category.table.id)


def load_default_categories(request, table_id):
    if request.method == "POST":
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

        # Добавление категорий в базу данных
        for cat in default_categories:
            Category.objects.get_or_create(
                name=cat["name"], type=cat["type"], table_id=table_id
            )

        # Сообщение об успешной загрузке
        messages.success(request, "Standard categories have been loaded successfully.")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def edit_transaction(request):
    if request.method == "POST":
        transaction_id = request.POST.get('transaction_id')
        transaction = get_object_or_404(Transaction, id=transaction_id, category__table__user=request.user)

        transaction.date = request.POST.get('date')
        transaction.category_id = request.POST.get('category_id')
        transaction.type = request.POST.get('type')
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')
        transaction.save()

        return redirect('table_detail', table_id=transaction.category.table.id)


def about(request):
    return render(request, 'about.html',)
