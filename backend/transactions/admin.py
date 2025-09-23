from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Отображение для модели Category в Django Admin.
    """

    list_display = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Отображение и фильтрация для модели Transaction в Django Admin.
    """

    list_display = (
        "id",
        "timestamp",
        "amount",
        "currency",
        "category",
        "description",
        "is_anomaly",
    )
    list_filter = (
        "currency",
        "is_anomaly",
        "category",
    )
    search_fields = (
        "description",
        "category__name",
    )

    list_display_links = (
        "id",
        "description",
    )
    list_select_related = ("category",)
