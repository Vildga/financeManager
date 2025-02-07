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
from django.urls import path, include
from fmApp import views
# from fmApp.api_views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from fmApp import api_views
from fmApp.views import custom_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # path('login/', views.user_login, name='login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout'),
    # path('register/', views.register, name='register'),
    path('add_table/', views.add_table, name='add_table'),
    path('delete_table/', views.delete_table, name='delete_table'),
    path('table/<int:table_id>/', views.table_detail, name='table_detail'),
    path('table/<int:table_id>/add_transaction/', views.add_transaction, name='add_transaction'),
    path('add-category/', views.add_category, name='add_category'),
    path('manage-categories/<int:table_id>/', views.manage_categories, name='manage_categories'),
    path('table/<int:table_id>/category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('delete_transaction/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('load_default_categories/<int:table_id>/', views.load_default_categories, name='load_default_categories'),
    path('edit_transaction/', views.edit_transaction, name='edit_transaction'),
    path('about/', views.about, name='about'),
    path("users/", include("users.urls")),



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
    # path('api/transactions/<int:transaction_id>/delete/', api_views.delete_transaction_api, name='delete_transaction_api'),
    # path('api/transactions/<int:transaction_id>/edit/', api_views.edit_transaction_api, name='edit_transaction_api'),
    # path('api/categories/<int:table_id>/', api_views.get_categories_api, name='category-list'),
    # path('api/categories/add/<int:table_id>/', api_views.add_category_api, name='add-category'),
    # path('api/categories/delete/<int:category_id>/', api_views.delete_category_api, name='delete-category'),
    # path('api/categories/load-default/<int:table_id>/', api_views.load_default_categories, name='load-default-categories'),
    # path('api/register/', api_views.register_api, name='register_api'),
    # path('google-login-success/', api_views.google_login_success, name='google-login-success'),
    # path('google-login-error/', api_views.google_login_error, name='google-login-error'),
]

handler404 = custom_404_view

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
