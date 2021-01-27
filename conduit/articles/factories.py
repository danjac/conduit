# Third Party Libraries
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

# Real World App
# Conduit
from conduit.users.factories import UserFactory

# Local
from .models import Article, Comment


class ArticleFactory(DjangoModelFactory):
    slug = Faker("slug")
    author = SubFactory(UserFactory)

    class Meta:
        model = Article


class CommentFactory(DjangoModelFactory):
    article = SubFactory(ArticleFactory)
    author = SubFactory(UserFactory)

    class Meta:
        model = Comment
