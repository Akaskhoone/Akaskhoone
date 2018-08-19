from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from .models import User


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = BaseUserChangeForm.Meta.fields
