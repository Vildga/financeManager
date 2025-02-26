from django.contrib import admin
from .models import Category, Table, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    search_fields = ("name",)
    list_filter = ("type",)
    ordering = ("name",)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "description")
    search_fields = ("name", "description")
    list_filter = ("user",)
    ordering = ("name",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "currency", "table", "display_categories", "description")
    search_fields = ("description", "table__name", "category__name")
    list_filter = ("currency", "date", "category")
    ordering = ("-date",)
    list_per_page = 20

    def display_categories(self, obj):
        return ", ".join([cat.name for cat in obj.category.all()])
    display_categories.short_description = "Categories"
