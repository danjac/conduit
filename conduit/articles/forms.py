# Django
from django import forms

# Local
from .models import Article, Comment


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("slug", "title", "description", "body", "tags")
        labels = {
            "title": "Article Title",
            "description": "What's this article about?",
            "slug": "Article URL",
            "body": "Write your article (in Markdown)",
        }
        widgets = {"description": forms.TextInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        labels = {"body": "Write a comment..."}
