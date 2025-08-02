from django.urls import path
from . import views

urlpatterns = [
    path("add_transaction/", views.add_transaction, name="add_transaction"),
    path("get_transaction/", views.get_transaction, name="get_transaction"),
    path("delete_transaction/<int:transaction_id>/", views.delete_transaction, name="delete_transaction"),
    path("create_user/", views.create_user, name="create_user"),
    path("list_user/", views.list_users, name="list_users"),
]
