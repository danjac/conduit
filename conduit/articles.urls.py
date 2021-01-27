# Django
from django.urls import path

# Local
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.article_index, name="index"),
    path("follows/", views.article_index, name="follows", kwargs={"follows": True}),
    path("tag/<slug:tag>/", views.article_index, name="tag"),
    path("~submit/", views.create_article, name="create"),
    # path("<int:article_id>/~edit/", views.edit_article, name="edit"),
    # path("<int:article_id>/~delete/", views.delete_article, name="delete"),
    # path("<int:article_id>/~like/", views.like_article, name="like"),
    # path("<slug:slug>/", views.article_detail, name="detail"),
]
