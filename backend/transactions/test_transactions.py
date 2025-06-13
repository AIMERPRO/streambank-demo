import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from transactions.models import Category


# ------------------------------------------------------------------------
# Фикстуры для клиента и данных
# ------------------------------------------------------------------------
@pytest.fixture
def api_client():
    """Общий DRF APIClient."""
    return APIClient()


@pytest.fixture
def user(db):
    """Тестовый пользователь для получения токена."""
    return User.objects.create_user(
        username="alice", password="secret", is_superuser=True, is_staff=True
    )


@pytest.fixture
def auth_headers(api_client, user):
    """
    Получаем JWT через /api/token/ и возвращаем нужный заголовок для запросов.
    """
    resp = api_client.post(
        "/api/token/",
        {"username": user.username, "password": "secret"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK, "Не удалось получить токен"
    access = resp.json()["access"]
    return {"HTTP_AUTHORIZATION": f"Bearer {access}"}


@pytest.fixture
def category(db):
    """Создаёт и возвращает категорию для транзакций."""
    return Category.objects.create(name="TestCat")


@pytest.fixture
def transaction_payload(category):
    """
    Фабрика полезной нагрузки для создания транзакции.
    Можно переопределять поля через **overrides.
    """

    def _payload(**overrides):
        base = {
            "timestamp": timezone.now().isoformat(),
            "amount": "123.45",
            "currency": "USD",
            "description": "Test transaction",
            "category_id": category.id,
        }
        base.update(overrides)
        return base

    return _payload


# ------------------------------------------------------------------------
# 1) Тест базовой JWT-авторизации
# ------------------------------------------------------------------------
@pytest.mark.django_db
def test_jwt_auth_and_access(api_client, user, auth_headers):
    # без токена — 401/403
    resp = api_client.get("/api/transactions/")
    assert resp.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    )

    # с токеном — 200
    resp = api_client.get("/api/transactions/", **auth_headers)
    assert resp.status_code == status.HTTP_200_OK


# ------------------------------------------------------------------------
# 2) Остальные CRUD-тесты уже с auth_headers
# ------------------------------------------------------------------------
@pytest.mark.django_db
class TestTransactionAPI:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, auth_headers):
        """
        Сохраняем повторно api_client и auth_headers
         для всех тестов этого класса.
        Автоматически применяется ко всем методам.
        """
        self.client = api_client
        self.auth_headers = auth_headers
        # Пути
        self.list_url = reverse("transaction-list")
        self.detail_url = lambda pk: reverse("transaction-detail", args=[pk])

    def test_create_transaction_success(self, transaction_payload):
        payload = transaction_payload()
        resp = self.client.post(
            self.list_url, payload, format="json", **self.auth_headers
        )
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["amount"] == payload["amount"]
        assert data["category"]["id"] == payload["category_id"]

    def test_list_transactions_includes_new(self, transaction_payload):
        create_resp = self.client.post(
            self.list_url,
            transaction_payload(),
            format="json",
            **self.auth_headers,
        )
        created_id = create_resp.json()["id"]

        list_resp = self.client.get(self.list_url, **self.auth_headers)
        results = list_resp.json()
        assert any(item["id"] == created_id for item in results)

    @pytest.mark.parametrize("invalid_amount", ["-5.00", "0", "abc"])
    def test_create_transaction_invalid_amount(
        self, transaction_payload, invalid_amount
    ):
        payload = transaction_payload(amount=invalid_amount)
        resp = self.client.post(
            self.list_url, payload, format="json", **self.auth_headers
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "amount" in resp.json()

    def test_retrieve_transaction_detail(self, transaction_payload):
        create = self.client.post(
            self.list_url,
            transaction_payload(),
            format="json",
            **self.auth_headers,
        )
        pk = create.json()["id"]

        detail_resp = self.client.get(self.detail_url(pk), **self.auth_headers)
        assert detail_resp.status_code == status.HTTP_200_OK
        assert detail_resp.json()["id"] == pk

    def test_filter_transactions_by_category(
        self, transaction_payload, category
    ):
        other_cat = Category.objects.create(name="OtherCat")
        # создаём одну транзакцию в каждой категории
        self.client.post(
            self.list_url,
            transaction_payload(),
            format="json",
            **self.auth_headers,
        )
        self.client.post(
            self.list_url,
            transaction_payload(category_id=other_cat.id),
            format="json",
            **self.auth_headers,
        )

        resp = self.client.get(
            f"{self.list_url}?category_id={category.id}", **self.auth_headers
        )
        results = resp.json()
        assert all(item["category"]["id"] == category.id for item in results)
