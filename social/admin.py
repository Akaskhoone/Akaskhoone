from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import Tag, Post, Board, Comment


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@register(Post)
class PostAdmin(admin.ModelAdmin):
    filter_horizontal = ('tags', 'likes')


@register(Board)
class BoardAdmin(admin.ModelAdmin):
    filter_horizontal = ('posts',)


@register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
