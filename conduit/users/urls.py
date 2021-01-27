# Django
from django.urls import path

# Local
from . import views

app_name = "account"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("accept-cookies/", views.accept_cookies, name="accept_cookies"),
    path("settings/", views.edit_settings, name="settings"),
    path("follow/<slug:username>/", views.follow, name="follow"),
    path("user/<slug:username>/", views.user_detail, name="detail"),
    path(
        "user/<slug:username>/favorites",
        views.user_detail,
        name="favorites",
        kwargs={"favorites": True},
    ),
]
