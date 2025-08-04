from django.contrib import admin
from .models import DailyPortfolioSnapshot

@admin.register(DailyPortfolioSnapshot)
class DailyPortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ("date", "total_value", "total_units", "nav_per_unit")
    ordering = ("-date",)
    search_fields = ("date",)
    list_filter = ("date",)
