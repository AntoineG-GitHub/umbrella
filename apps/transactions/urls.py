from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_transaction, name="create_transaction"),
    path("list/", views.list_transactions, name="list_transactions"),
    path("get_transaction/<int:transaction_id>/", views.get_transaction, name="get_transaction"),
    path("delete/<int:transaction_id>/", views.delete_transaction, name="delete_transaction"),
    path("create_user/", views.create_user, name="create_user"),
    path("list_user/", views.list_users, name="list_users"),
]
