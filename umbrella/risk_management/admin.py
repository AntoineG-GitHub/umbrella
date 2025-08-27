from django.contrib import admin
from .models import VARComputation

class VARComputationAdmin(admin.ModelAdmin):
    list_display = ('date', 'var_95_1day', 'var_99_1day', 'expected_shortfall_95_1day', 'expected_shortfall_99_1day')
    search_fields = ('date',)
    list_filter = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'

admin.site.register(VARComputation, VARComputationAdmin)