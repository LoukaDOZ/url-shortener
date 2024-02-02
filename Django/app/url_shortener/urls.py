from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("r/<str:url_id>/", views.RedirectToTargetView.as_view(), name="redirect"),
    path("shorten/", views.ShortenView.as_view(), name="shorten"),
    path("login/", views.log_in, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.log_out, name="logout"),
    path("my-urls/", views.UserURLView.as_view(), name="user_urls"),
    path("<path:unknown_path>/", views.NotFoundView.as_view(), name="unknown")
]