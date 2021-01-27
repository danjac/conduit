# Django
from django.urls import path

# Local
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.article_list, name="index"),
    path("follows/", views.article_list, name="follows", kwargs={"follows": True}),
    path("tag/<slug:tag>/", views.article_list, name="tag"),
    path("~submit/", views.create_article, name="create"),
    path("<int:article_id>/~edit/", views.edit_article, name="edit"),
    path("<int:article_id>/~like/", views.like_article, name="like"),
    path(
        "<int:article_id>/~submit-comment/", views.submit_comment, name="submit_comment"
    ),
    path(
        "<int:comment_id>/~delete-comment/", views.delete_comment, name="delete_comment"
    ),
    path("<slug:slug>/", views.article_detail, name="detail"),
]
