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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
