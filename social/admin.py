from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import Tag, Post


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
