"""
URL configuration for FinanceManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from fmApp import api_public, views
from fmApp.views import custom_404_view

schema_view = get_schema_view(
    openapi.Info(
        title="Public Finance API",
        default_version="v1",
        description="Документація публічних API для аналітики витрат та доходів",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("social-auth/", include("social_django.urls", namespace="social")),
    path("add_table/", views.TableCreateView.as_view(), name="add_table"),
    path("delete_table/", views.TableDeleteView.as_view(), name="delete_table"),
    path("table/<int:table_id>/", views.TableDetailView.as_view(), name="table_detail"),
    path(
        "table/<int:table_id>/add_transaction/",
        views.AddTransactionView.as_view(),
        name="add_transaction",
    ),
    path(
        "delete_transaction/<int:transaction_id>/",
        views.DeleteTransactionView.as_view(),
        name="delete_transaction",
    ),
    path(
        "edit_transaction/",
        views.EditTransactionView.as_view(),
        name="edit_transaction",
    ),
    path("about/", views.AboutView.as_view(), name="about"),
    path("users/", include("users.urls")),
    path(
        "get-available-months/",
        views.AvailableMonthsView.as_view(),
        name="get_available_months",
    ),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "api/public/total-transactions/",
        api_public.TotalTransactionsAPIView.as_view(),
        name="api_total_transactions",
    ),
    path(
        "api/public/average-expense-by-category/",
        api_public.AverageExpenseByCategoryAPIView.as_view(),
        name="api_average_expense",
    ),
    path(
        "api/public/expenses-by-month/",
        api_public.ExpensesByMonthAPIView.as_view(),
        name="api_expenses_by_month",
    ),
    path(
        "api/public/expense-share-by-category/",
        api_public.ExpenseShareByCategoryAPIView.as_view(),
        name="api_expense_share",
    ),
    path(
        "api/public/income-expense-trend/",
        api_public.IncomeExpenseTrendAPIView.as_view(),
        name="api_income_expense_trend",
    ),
    path("delete-category/<int:pk>/", views.CategoryDeleteView.as_view(), name="delete_category"),
    path('add-category/', views.CategoryAddView.as_view(), name='add_category'),
    path("load-default-categories/", views.load_default_categories, name="load_default_categories"),

    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    re_path(
        r"^swagger\.json$", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    # API URLS
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    # path('api/logout/', api_views.LogoutView.as_view(), name='logout'),
    # path('api/tables/', api_views.get_tables, name='get_tables'),
    # path('api/tables/add/', api_views.add_table, name='add_table'),
    # path('api/tables/delete/<int:table_id>/', api_views.delete_table, name='delete_table'),
    # path('api/user/', api_views.get_user_info, name='get_user_info'),
    # path('api/tables/<int:table_id>/', api_views.table_detail_api, name='table-detail'),
    # path('api/transactions/add/<int:table_id>/', api_views.add_transaction_api, name='add-transaction'),
    # path(
    #     'api/transactions/<int:transaction_id>/delete/',
    #     api_views.delete_transaction_api,
    #     name='delete_transaction_api'),
    # path('api/transactions/<int:transaction_id>/edit/', api_views.edit_transaction_api, name='edit_transaction_api'),
    # path('api/categories/<int:table_id>/', api_views.get_categories_api, name='category-list'),
    # path('api/categories/add/<int:table_id>/', api_views.add_category_api, name='add-category'),
    # path('api/categories/delete/<int:category_id>/', api_views.delete_category_api, name='delete-category'),
    # path(
    # 'api/categories/load-default/<int:table_id>/',
    # api_views.load_default_categories,
    # name='load-default-categories'),
    # path('api/register/', api_views.register_api, name='register_api'),
    # path('google-login-success/', api_views.google_login_success, name='google-login-success'),
    # path('google-login-error/', api_views.google_login_error, name='google-login-error'),
]

handler404 = custom_404_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
