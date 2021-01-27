# Django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = User


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User


class UserForm(forms.ModelForm):

    password1 = forms.CharField(
        label=_("New Password"), required=False, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("New Password (again)"), required=False, widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("name", "image", "bio", "email")

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password1 != password2:
            raise ValidationError(_("Passwords don't match"))

    def save(self):
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            instance.set_password(password)
        instance.save()
        return instance
