from django.urls import path
from . import views

urlpatterns = [
    path("add_user/", views.add_user, name="add_user"),
    path("get_user/", views.get_user, name="get_user"),
    path("login_user/", views.login_user, name="login_user"),
]