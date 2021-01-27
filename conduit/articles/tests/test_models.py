# Third Party Libraries
import pytest

# Local
from ..models import Article

pytestmark = pytest.mark.django_db


class TestArticleManager:
    def test_with_num_likes_if_none(self, article):
        first = Article.objects.with_num_likes().first()
        assert first.num_likes == 0

    def test_with_num_likes_if_has_likes(self, article, user):
        user.likes.add(article)
        first = Article.objects.with_num_likes().first()
        assert first.num_likes == 1
