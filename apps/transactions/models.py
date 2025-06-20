from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit"
        WITHDRAWAL = "withdrawal"
        BUY = "buy"
        SELL = "sell"
        DIVIDEND = "dividend"
        FEE = "fee"

    type = models.CharField(max_length=20, choices=TransactionType.choices)
    user= models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)  # always in EUR
    currency = models.CharField(max_length=10, default="EUR")  # in case you want to expand
    ticker = models.CharField(max_length=10, null=True, blank=True)  # for buy/sell/dividend
    shares = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)  # for buy/sell
    metadata = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self):
        return f"{self.date} - {self.type} - {self.amount} EUR"

class CustomUser(AbstractUser):
    pass