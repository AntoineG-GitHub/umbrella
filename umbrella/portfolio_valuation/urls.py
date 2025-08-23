from django.urls import path
from .views import UserShareSnapshotView
from portfolio_valuation import views

urlpatterns = [
    path("get_daily_portfolio_snapshot/", views.get_portfolio_valuations, name="get_daily_portfolio_snapshot"),
    path("get_portfolio_stocks/", views.get_portfolio_stock, name="get_portfolio_stocks"),
    path("user_snapshots/<int:user_id>/", UserShareSnapshotView.as_view(), name="user_snapshots")
]
