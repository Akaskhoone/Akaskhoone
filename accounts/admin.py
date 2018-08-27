from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import User, Profile


@register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
