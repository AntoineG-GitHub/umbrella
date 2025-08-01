# apps/data_ingestion/urls.py
from django.urls import path
from data_ingestion import views

urlpatterns = [
    path("fetch_and_save_data/<str:ticker>/", views.fetch_and_save_data, name='fetch_and_save_data'),
    path('fetch_and_save_data_exchange_rate/<str:from_currency>', views.fetch_and_save_exchange_rates, name='fetch_and_save_exchange_rates'),
    path('fetch_and_save_stock_info/<str:ticker>/', views.get_company_info, name='fetch_and_save_stock_info' ),
    path("get_company_info/<str:ticker>/", views.get_company_info, name="company-info"),
    path("get_prices/<str:ticker>/", views.get_prices, name="prices"),
    path("get_exchange_rates/<str:from_currency>/", views.get_exchange_rates, name="exchange-rates"),
]