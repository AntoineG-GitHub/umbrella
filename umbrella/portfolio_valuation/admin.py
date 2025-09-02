from django.contrib import admin
from portfolio_valuation.models import DailyPortfolioSnapshot, UserShareSnapshot, PortfolioCompositionSnapshot

@admin.register(DailyPortfolioSnapshot)
class DailyPortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ("date", "total_value", "total_units", "nav_per_unit")
    ordering = ("-date",)
    search_fields = ("date",)
    list_filter = ("date",)

@admin.register(UserShareSnapshot)
class UserShareSnapshotAdmin(admin.ModelAdmin):
    list_display = ("date", "user_id", "units_held", "value_held")
    ordering = ("-date",)
    search_fields = ("date",)
    list_filter = ("date",)

@admin.register(PortfolioCompositionSnapshot)
class PortfolioCompositionSnapshotAdmin(admin.ModelAdmin):
    list_display = ("date", "ticker", "quantity", "value_eur")
    ordering = ("-date",)
    search_fields = ("date", "ticker")
    list_filter = ("date", "ticker")
