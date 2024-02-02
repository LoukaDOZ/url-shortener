from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("r/<str:url_id>/", views.RedirectToTargetView.as_view(), name="redirect"),
    path("shorten/", views.ShortenView.as_view(), name="shorten"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("my-urls/", views.UserURLView.as_view(), name="user_urls"),
    path("<path:unknown_path>/", views.NotFoundView.as_view(), name="unknown")
]