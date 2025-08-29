from django.contrib import admin
from .models import BaseHistoricalExchangeRate, HistoricalPrice, TickerInfo
from django.contrib import admin
from django.contrib import admin

@admin.register(HistoricalPrice)
class HistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ('date', 'open', 'ticker')  # Add relevant fields here
    search_fields = ('date', 'ticker')  # Add searchable fields
    list_filter = ('ticker',)  # Add filters based on fields
    ordering = ('-date',)  # Order by date (most recent first)

@admin.register(BaseHistoricalExchangeRate)
class BaseHistoricalExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('date', 'from_currency', 'to_currency', 'open')  
    search_fields = ('from_currency', 'to_currency') 
    list_filter = ('from_currency', 'to_currency')  
    ordering = ('-date',) 
    date_hierarchy = 'date'  

@admin.register(TickerInfo)
class TickerInfoAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'sector', 'industry')
    search_fields = ('ticker', 'name', 'sector', 'industry')  
    list_filter = ('sector', 'industry')  
    ordering = ('ticker',) 


