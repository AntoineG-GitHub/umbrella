from django.urls import path
from risk_management import views

urlpatterns = [
    path("get_historical_var/", views.get_historical_var, name="historical-var"),
]