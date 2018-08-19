from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile
from .froms import UserCreationForm, UserChangeForm


@register(User)
class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['email', 'username', 'password']


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
