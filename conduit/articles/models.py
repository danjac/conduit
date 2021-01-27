# Django
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

# Third Party Libraries
import markdown
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager


class ArticleQuerySet(models.QuerySet):
    def with_num_likes(self):
        return self.annotate(num_likes=models.Count("likers"))


class ArticleManager(models.Manager.from_queryset(ArticleQuerySet)):
    ...


class Article(TimeStampedModel):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    tags = TaggableManager()

    objects = ArticleManager()

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["created", "-created"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("articles:detail", args=[self.slug])

    def as_markdown(self):
        return mark_safe(markdown.markdown(self.body))


class Comment(TimeStampedModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    body = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["created", "-created"]),
        ]

    def as_markdown(self):
        return mark_safe(markdown.markdown(self.body))
