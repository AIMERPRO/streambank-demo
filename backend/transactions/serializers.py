from rest_framework import serializers

from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализует объекты Category.
    Используется вложенным в TransactionSerializer для отображения полной информации о категории.  # noqa: E501
    """

    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = ["id"]  # id не должно меняться со стороны клиента


class TransactionSerializer(serializers.ModelSerializer):
    """
    Сериализует объекты Transaction.
    - Для записи принимает только поле category_id.
    - Для чтения отдаёт вложенный объект category (CategorySerializer).
    """

    # Вложенный сериализатор для чтения
    category = CategorySerializer(read_only=True)

    # Поле для записи: связывает transaction.category по PK
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "timestamp",
            "amount",
            "currency",
            "description",
            "category",
            "category_id",
            "is_anomaly",
        ]
        # Поля, которые клиент не может задавать напрямую
        read_only_fields = ["id", "is_anomaly"]
        extra_kwargs = {
            "description": {
                "required": False,
                "allow_blank": True,
                "max_length": 255,
                "help_text": "Краткое описание транзакции (необязательно)",
            },
            "currency": {
                "required": True,
                "help_text": "Валюта транзакции, например USD или EUR",
            },
        }

    def validate_amount(self, value):
        """
        Проверяет, что сумма транзакции положительна.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "Сумма транзакции должна быть больше нуля."
            )
        return value

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class DetectAnomaliesSerializer(serializers.Serializer):
    """
    Параметры для запуска алгоритма детектирования аномалий:
    threshold — число сигм (σ), выше которого транзакция считается аномальной.
    """

    threshold = serializers.FloatField(
        default=3, help_text="Порог σ для маркировки аномалий"
    )
