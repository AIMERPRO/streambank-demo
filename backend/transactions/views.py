from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Category, Transaction
from .serializers import (
    CategorySerializer,
    DetectAnomaliesSerializer,
    TransactionSerializer,
)
from .tasks import detect_anomalies
from .utils import run_sql_file


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD для категорий транзакций.
    """

    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]  # Неавторизованный доступ к спискам, но запрещена запись
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD + дополнительные действия для транзакций:

      • GET  /transactions/anomalies/       – список аномальных транзакций
      • POST /transactions/detect/          – запустить задачу детектирования аномалий   # noqa: E501
      • GET  /transactions/monthly-totals/  – агрегаты по месяцам (CTE SQL)
      • GET  /transactions/jsonb-demo/      – пример JSONB-запроса
      • GET  /transactions/window-stats/    – пример оконных функций
    """

    # Подтягиваем категорию одним JOIN-ом во избежание N+1
    # кешируем только список

    permission_classes = [IsAdminUser]  # Только Администраторам
    queryset = Transaction.objects.select_related("category").all()
    serializer_class = TransactionSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category_id"]

    @action(detail=False, methods=["get"], url_path="anomalies")
    def anomalies(self, request):
        """
        Список транзакций, помеченных как аномалии (is_anomaly=True).
        Поддерживает пагинацию.
        """
        qs = self.get_queryset().filter(is_anomaly=True)
        qs = self.filter_queryset(
            qs
        )  # применить filter_backends, если они есть

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="detect",
        serializer_class=DetectAnomaliesSerializer,
    )
    def detect(self, request):
        """
        Запускает фоновую Celery-задачу
         detect_anomalies с параметром threshold.
        Возвращает ID задачи и HTTP 202.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        threshold = serializer.validated_data["threshold"]
        task = detect_anomalies.delay(threshold)

        return Response(
            {"task_id": task.id, "status": "started"},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["get"], url_path="monthly-totals")
    @method_decorator(cache_page(60 * 5))  # Кешируем на 5 минут
    def monthly_totals(self, request):
        """
        Выполняет SQL из docs/sql/cte_monthly_category_totals.sql,
        возвращает результаты агрегатов по месяцам.
        """
        data = run_sql_file("cte_monthly_category_totals.sql")
        return Response(data)

    @action(detail=False, methods=["get"], url_path="jsonb-demo")
    def jsonb_demo(self, request):
        """
        Демонстрация работы с JSONB-полем через SQL из docs/sql/jsonb_select.sql.  # noqa: E501
        """
        data = run_sql_file("jsonb_select.sql")
        return Response(data)

    @action(detail=False, methods=["get"], url_path="window-stats")
    def window_stats(self, request):
        """
        Демонстрация оконных функций SQL из docs/sql/window_func_accumulate.sql.   # noqa: E501
        """
        data = run_sql_file("window_func_accumulate.sql")
        return Response(data)

    def perform_create(self, serializer):
        instance = serializer.save()
        cache.delete_pattern("**/transactions/*")
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete_pattern("**/transactions/*")
        return instance

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete_pattern("**/transactions/*")
