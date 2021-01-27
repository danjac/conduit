# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

# Third Party Libraries
from taggit.models import TaggedItem
from turbo_response import redirect_303, render_form_response

# Real World App
from conduit.pagination import paginate
from conduit.shortcuts import handle_form

# Local
from .forms import ArticleForm
from .models import Article


def article_list(request, follows=False, tag=None):
    """Show list of articles"""

    articles = (
        Article.objects.with_num_likes().select_related("author").order_by("-created")
    )

    tags = (
        TaggedItem.objects.select_related("tag")
        .values_list("tag__slug", "tag__name")
        .distinct()
    )

    if tag:
        articles = articles.filter(tags__slug__in=[tag])

    if follows and request.user.is_authenticated:
        articles = articles.filter(author__in=request.user.follows.all())

    return TemplateResponse(
        request,
        "articles/index.html",
        {
            "page_obj": paginate(request, articles),
            "tags": tags,
            "follows": follows,
            "tag": tag,
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
            return redirect_303("articles:index")
        return render_form_response(
            request,
            form,
            "articles/article_form.html",
        )
