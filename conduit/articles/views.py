# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from taggit.models import TaggedItem
from turbo_response import (
    TurboFrame,
    TurboStream,
    TurboStreamResponse,
    redirect_303,
    render_form_response,
)

# Real World App
from conduit.pagination import paginate
from conduit.shortcuts import handle_form

# Local
from .forms import ArticleForm, CommentForm
from .models import Article, Comment


def article_list(request, follows=False, tag=None):
    """Show list of articles"""

    articles = (
        Article.objects.with_num_likes().select_related("author").order_by("-created")
    )

    if tag:
        articles = articles.filter(tags__slug__in=[tag])

    if follows and request.user.is_authenticated:
        articles = articles.filter(author__in=request.user.follows.all())

    context = {
        "page_obj": paginate(request, articles),
        "follows": follows,
        "tag": tag,
    }

    if request.turbo.frame:
        return (
            TurboFrame(request.turbo.frame)
            .template("articles/_articles.html", context)
            .response(request)
        )

    return TemplateResponse(
        request,
        "articles/index.html",
        {
            **context,
            "tags": (
                TaggedItem.objects.select_related("tag")
                .values_list("tag__slug", "tag__name")
                .distinct()
            ),
        },
    )


@login_required
def create_article(request):
    with handle_form(request, ArticleForm) as (form, is_success):
        if is_success:
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            # save tags
            form.save_m2m()
            messages.success(request, _("Your article has been published!"))
            return redirect_303(article)
        return render_form_response(
            request,
            form,
            "articles/article_form.html",
        )


def article_detail(request, slug):

    article = get_object_or_404(
        Article.objects.with_num_likes().select_related("author"),
        slug=slug,
    )

    comments = article.comment_set.select_related("author").order_by("-created")

    context = {"article": article, "page_obj": paginate(request, comments)}

    if request.turbo.frame:
        return (
            TurboFrame(request.turbo.frame)
            .template("articles/_comments.html", context)
            .response(request)
        )

    is_following = False
    can_follow = False
    can_like = False
    can_edit = False

    comment_form = None

    if request.user.is_authenticated:
        comment_form = CommentForm()

        if request.user == article.author:

            can_edit = True

        else:

            is_following = article.author.followers.filter(pk=request.user.id).exists()
            can_follow = True
            can_like = True

    return TemplateResponse(
        request,
        "articles/detail.html",
        {
            **context,
            "comment_form": comment_form,
            "is_following": is_following,
            "can_follow": can_follow,
            "can_like": can_like,
            "can_edit": can_edit,
        },
    )


@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, author=request.user, pk=article_id)
    with handle_form(request, ArticleForm, instance=article) as (form, is_success):
        if is_success:
            form.save()
            messages.success(request, _("Your article has been updated!"))
            return redirect_303(article)
        return render_form_response(
            request, form, "articles/article_form.html", {"article": article}
        )


@require_POST
@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, author=request.user, pk=article_id)
    article.delete()
    messages.info(request, _("Your article has been deleted"))
    return redirect(settings.HOME_URL)


@require_POST
@login_required
def like_article(request, article_id):
    article = get_object_or_404(
        Article.objects.exclude(author=request.user), pk=article_id
    )

    if request.user.likes.filter(pk=article_id).exists():
        request.user.likes.remove(article)
    else:
        request.user.likes.add(article)

    num_likes = article.likers.count()

    return TurboStreamResponse(
        [
            TurboStream(target).update.render(str(num_likes))
            for target in [
                f"article-likes-{article.id}",
                "article-likes-header",
                "article-likes-body",
            ]
        ]
    )


@require_POST
@login_required
def submit_comment(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    form = CommentForm(request.POST)
    tmpl = TurboFrame("new-comment").template(
        "articles/_new_comment.html", {"article": article}
    )

    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.save()
        tmpl.context.update({"form": CommentForm(), "comment": comment})
    else:
        tmpl.context.update({"form": form})

    return tmpl.response(request)


@require_POST
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, author=request.user, pk=comment_id)
    comment.delete()
    if request.turbo:
        return TurboStream(f"comment-{comment_id}").remove.response()
    return redirect(comment.article)
