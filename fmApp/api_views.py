from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Table, Transaction, Category
from .serializers import TableSerializer, TransactionSerializer, CategorySerializer
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def google_login_success(request):
    user = request.user

    # Генерируем JWT токены
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    print("Access Token:", access_token)  # Отладка
    print("Refresh Token:", refresh_token)  # Отладка

    # Редиректим на Vue
    frontend_url = 'http://localhost:5173/oauth/callback/'
    redirect_url = f"{frontend_url}?token={access_token}&refresh={refresh_token}"
    print("Redirect URL:", redirect_url)  # Отладка
    return redirect(redirect_url)


def google_login_error(request):
    """
    Вызывается, если при авторизации через Google возникла ошибка.
    Можно перенаправить на Vue-страницу логина и отобразить сообщение об ошибке.
    """
    # Например, редиректим на страницу /login?error=google_auth_failed
    return redirect("http://localhost:5173/login?error=google_auth_failed")


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Проверка, что оба поля заполнены
        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tables(request):
    tables = Table.objects.filter(user=request.user)
    serializer = TableSerializer(tables, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_table(request):
    serializer = TableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_table(request, table_id):
    try:
        table = Table.objects.get(id=table_id, user=request.user)
        table.delete()
        return Response(status=204)
    except Table.DoesNotExist:
        return Response({"error": "Table not found."}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def table_detail_api(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)

    # Получаем транзакции
    transactions = Transaction.objects.filter(category__table=table).order_by('-date')

    # Сводка расходов
    expense_summary = Transaction.objects.filter(category__table=table, type='expense') \
        .values('category__name').annotate(total=Sum('amount'))

    # Сводка доходов
    income_summary = Transaction.objects.filter(category__table=table, type='income') \
        .values('category__name').annotate(total=Sum('amount'))

    # Категории
    categories = Category.objects.filter(table=table)

    # Общая сумма доходов и расходов
    total_income = Transaction.objects.filter(category__table=table, type='income') \
        .aggregate(total=Sum('amount'))['total'] or 0

    total_expense = Transaction.objects.filter(category__table=table, type='expense') \
        .aggregate(total=Sum('amount'))['total'] or 0

    net_total = total_income - total_expense

    # Формируем ответ
    response_data = {
        'table': TableSerializer(table).data,
        'transactions': TransactionSerializer(transactions, many=True).data,
        'expense_summary': list(expense_summary),
        'income_summary': list(income_summary),
        'categories': CategorySerializer(categories, many=True).data,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_total': net_total
    }

    return Response(response_data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_transaction_api(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)

    data = request.data
    category_id = data.get('category')
    category = get_object_or_404(Category, id=category_id, table=table)

    transaction = Transaction.objects.create(
        date=data.get('date'),
        type=data.get('type'),
        category=category,
        amount=data.get('amount'),
        description=data.get('description'),
        table=table
    )

    return Response(TransactionSerializer(transaction).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_transaction_api(request, transaction_id):
    """
    Удаляет транзакцию по её ID.
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id, category__table__user=request.user)
        transaction.delete()
        return Response({"message": "Transaction deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found or access denied."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_transaction_api(request, transaction_id):
    """
    Редактирует существующую транзакцию.
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id, category__table__user=request.user)
    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found or access denied."}, status=status.HTTP_404_NOT_FOUND)

    # Логируем входящие данные
    print("Incoming data:", request.data)

    serializer = TransactionSerializer(transaction, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Transaction updated successfully.", "transaction": serializer.data},
                        status=status.HTTP_200_OK)

    # Логируем ошибки сериализатора
    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories_api(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    categories = Category.objects.filter(table=table)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category_api(request, table_id):
    table = get_object_or_404(Table, id=table_id, user=request.user)
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(table=table)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category_api(request, category_id):
    category = get_object_or_404(Category, id=category_id, table__user=request.user)
    category.delete()
    return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def load_default_categories(request, table_id):
    # Проверь, что таблица существует и принадлежит текущему пользователю
    table = Table.objects.filter(id=table_id, user=request.user).first()
    if not table:
        return Response({"error": "Table not found or access denied."}, status=404)

    # Стандартные категории
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
        Category.objects.get_or_create(name=cat["name"], type=cat["type"], table=table)

    return Response({"message": "Standard categories have been loaded successfully."}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    """
    API для регистрации пользователя.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    password2 = request.data.get('password2')

    # Проверяем пароли
    if password != password2:
        return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    # Проверяем существующего пользователя
    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Создаём пользователя
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def social_login(request):
    """
    Обрабатывает код авторизации Google и возвращает JWT токены.
    """
    code = request.data.get('code')  # Получаем код авторизации
    redirect_uri = request.data.get('redirect_uri')  # URL редиректа

    if not code or not redirect_uri:
        return Response({"error": "Missing code or redirect_uri"}, status=400)

    try:
        strategy = load_strategy(request)
        backend = load_backend(strategy, 'google-oauth2', redirect_uri=redirect_uri)

        # Завершаем процесс авторизации
        user = backend.auth_complete(code=code)

        # Генерация токенов
        refresh = RefreshToken.for_user(user)
        return Response({
            'accessToken': str(refresh.access_token),
            'refreshToken': str(refresh),
        })
    except MissingBackend:
        return Response({"error": "Invalid backend"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

