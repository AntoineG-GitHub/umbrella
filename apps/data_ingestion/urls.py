# apps/data_ingestion/urls.py
from django.urls import path
from data_ingestion import views

urlpatterns = [
    path("get_company_info/<str:ticker>/", views.get_company_info, name="company-info"),
    path("get_prices/<str:ticker>/", views.get_prices, name="prices"),
    path("get_exchange_rates/<str:from_currency>/", views.get_exchange_rates, name="exchange-rates"),
]