from django.urls import path
from .views import ComputeValuationView, UserShareSnapshotView, BatchValuationView
from portfolio_valuation import views

urlpatterns = [
    path("compute/", ComputeValuationView.as_view(), name="compute_valuation"),
    path("get_daily_portfolio_snapshot/", views.get_portfolio_valuations, name="get_daily_portfolio_snapshot"),
    path("user_snapshots/<int:user_id>/", UserShareSnapshotView.as_view(), name="user_snapshots"),
    path('batch-compute/', BatchValuationView.as_view(), name='batch_compute_valuations'),
]
