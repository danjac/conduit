# Standard Library
import datetime

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import (
    TurboStream,
    TurboStreamIterableResponse,
    redirect_303,
    render_form_response,
)

# Real World App
from conduit.articles.models import Article
from conduit.pagination import paginate
from conduit.shortcuts import handle_form

# Local
from .forms import UserCreationForm, UserForm


def user_detail(request, username, favorites=False):
    user = get_object_or_404(get_user_model(), username=username)
    if request.user.is_authenticated:
        is_following = request.user.follows.filter(pk=user.id).exists()
        can_follow = request.user != user
    else:
        is_following = False
        can_follow = False

    articles = Article.objects.filter(author=user).with_num_likes().order_by("-created")

    if favorites:
        articles = articles.filter(num_likes__gt=0)

    return TemplateResponse(
        request,
        "account/detail.html",
        {
            "user_obj": user,
            "is_following": is_following,
            "can_follow": can_follow,
            "page_obj": paginate(request, articles),
        },
    )


@require_POST
@login_required
def follow(request, username):
    user = get_object_or_404(
        get_user_model().objects.exclude(pk=request.user.id), username=username
    )

    if request.user.follows.filter(pk=user.id).exists():
        request.user.follows.remove(user)
        is_following = False
    else:
        request.user.follows.add(user)
        is_following = True

    return TurboStreamIterableResponse(
        [
            TurboStream(target)
            .replace.template(
                "account/_follow.html",
                {"user_obj": user, "is_following": is_following, "target": target},
                request=request,
            )
            .render()
            for target in ["follow-header", "follow-footer"]
        ]
    )


@login_required
def edit_settings(request):
    with handle_form(request, UserForm, instance=request.user) as (form, is_success):
        if is_success:
            form.save()
            messages.success(request, _("Your settings have been saved"))
            return redirect_303(settings.HOME_URL)
        return render_form_response(
            request,
            form,
            "account/settings_form.html",
        )


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    redirect_url = get_redirect_url(request) or settings.LOGIN_REDIRECT_URL
    if request.user.is_authenticated:
        return redirect(redirect_url)

    with handle_form(request, AuthenticationForm, _request=request) as (
        form,
        is_success,
    ):
        if is_success:
            auth_login(request, form.get_user())
            return redirect_303(redirect_url)

        return render_form_response(
            request,
            form,
            "account/login.html",
            {
                "redirect_field_name": REDIRECT_FIELD_NAME,
                "redirect_field_value": redirect_url,
            },
        )


@sensitive_post_parameters()
@csrf_protect
@never_cache
def signup(request):
    with handle_form(request, UserCreationForm) as (form, is_success):
        if is_success:
            form.save()
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            auth_login(request, user)
            return redirect_303(settings.LOGIN_REDIRECT_URL)
        return render_form_response(request, form, "account/signup.html")


@require_POST
@never_cache
def logout(request):
    auth_logout(request)
    return redirect(get_redirect_url(request) or settings.LOGOUT_REDIRECT_URL)


@require_POST
def accept_cookies(request):
    response = TurboStream("accept-cookies").remove.response()
    response.set_cookie(
        "accept-cookies",
        value="true",
        expires=timezone.now() + datetime.timedelta(days=30),
        samesite="Lax",
    )
    return response


def get_redirect_url(request):
    redirect_to = request.POST.get(
        REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, "")
    )
    if redirect_to and url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect_to
    return None
