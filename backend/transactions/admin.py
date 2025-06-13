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
        # 'data',
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

    # Если поле `data` содержит много текста (JSON), лучше отображать его усечённо:  # noqa: E501
    # def truncated_data(self, obj):
    #     txt = str(obj.data)
    #     return txt if len(txt) < 75 else txt[:75] + '…'
    # truncated_data.short_description = 'Data'
    # list_display = (..., 'truncated_data')
