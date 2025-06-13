from django.db import models


class Category(models.Model):
    """Категории транзакций (еда, транспорт, развлечения и т.п.)."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Банковская транзакция."""

    timestamp = models.DateTimeField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
    )
    is_anomaly = models.BooleanField(default=False)
    data = models.JSONField(
        null=True, blank=True, help_text="Дополнительные метаданные (JSON)"
    )

    def __str__(self):
        return f"{self.timestamp.date()} — {self.amount} {self.currency}"
