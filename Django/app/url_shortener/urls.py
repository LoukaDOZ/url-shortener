from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("r/<int:url_id>/", views.redirect, name="redirect"),
    path("shorten/", views.shorten, name="shorten"),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("logout", views.logout, name="logout"),
    path("my-urls/", views.my_urls, name="user_urls"),
    path("<path:unknown_path>/", views.not_found, name="unknown")
]