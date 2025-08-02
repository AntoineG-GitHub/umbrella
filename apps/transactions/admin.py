from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "type", "user", "amount", "ticker", "shares")
    list_filter = ("type", "user", "ticker")
    search_fields = ("ticker", "user__username")