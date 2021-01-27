# Standard Library
import http

# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..factories import UserFactory

pytestmark = pytest.mark.django_db


class TestLogin:
    def test_post_login_invalid(self, client):
        resp = client.post(
            reverse("account:login"), {"username": "user", "password": "wrong"}
        )
        assert resp.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY

    def test_post_login_valid(self, client, user, password):
        resp = client.post(
            reverse("account:login"), {"username": user.username, "password": password}
        )
        assert resp.url == settings.LOGIN_REDIRECT_URL

    def test_get(self, client):
        resp = client.get(reverse("account:login"))
        assert resp.status_code == http.HTTPStatus.OK

    def test_get_if_authenticated(self, client, login_user):
        resp = client.get(reverse("account:login"))
        assert resp.url == settings.LOGIN_REDIRECT_URL


class TestSignup:
    def test_get(self, client):
        resp = client.get(reverse("account:signup"))
        assert resp.status_code == http.HTTPStatus.OK

    def test_post_login_valid(self, client, user_model):
        resp = client.post(
            reverse("account:signup"),
            {"username": "user", "password1": "testpass1", "password2": "testpass1"},
        )
        assert resp.url == settings.LOGIN_REDIRECT_URL
        user = user_model.objects.get()
        assert user.username == "user"
        assert user.check_password("testpass1")


class TestLogout:
    def test_post(self, client, login_user):
        assert client.post(reverse("account:logout")).url == settings.LOGIN_REDIRECT_URL


class TestAcceptCookies:
    def test_post(self, client):
        assert (
            client.post(reverse("account:accept_cookies")).status_code
            == http.HTTPStatus.OK
        )


class TestEditSettings:
    def test_post(self, client, login_user):
        response = client.post(
            reverse("account:settings"),
            {
                "name": "Test user",
                "bio": "test",
                "avatar": "",
                "email": "tester@gmail.com",
                "password1": "",
                "password2": "",
            },
        )
        assert response.url == settings.HOME_URL
        login_user.refresh_from_db()
        assert login_user.name == "Test user"
        # check password unchanged
        assert login_user.check_password("testpass1")

    def test_post_change_password(self, client, login_user):
        response = client.post(
            reverse("account:settings"),
            {
                "name": "Test user",
                "bio": "test",
                "avatar": "",
                "email": "tester@gmail.com",
                "password1": "testpass2",
                "password2": "testpass2",
            },
        )
        assert response.url == settings.HOME_URL
        login_user.refresh_from_db()
        assert login_user.name == "Test user"
        assert login_user.check_password("testpass2")


class TestUserFollow:
    def test_post_follow(self, client, login_user):
        user = UserFactory()
        response = client.post(reverse("account:follow", args=[user.username]))
        assert response.status_code == http.HTTPStatus.OK
        assert user in login_user.follows.all()

    def test_post_follow_self(self, client, login_user):
        response = client.post(reverse("account:follow", args=[login_user.username]))
        assert response.status_code == http.HTTPStatus.NOT_FOUND

    def test_post_unfollow(self, client, login_user):
        user = UserFactory()
        login_user.follows.add(user)
        client.post(reverse("account:follow", args=[user.username]))
        assert user not in login_user.follows.all()
