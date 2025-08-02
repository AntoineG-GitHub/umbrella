from django.urls import path
from . import views

urlpatterns = [
    path("create_user/", views.create_user, name="create_user"),
    path("get_user/", views.get_user, name="get_user"),
    path("login_user/", views.login_user, name="login_user"),
]