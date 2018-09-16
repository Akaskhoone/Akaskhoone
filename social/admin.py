from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import Tag, Post, Board, Comment, Notification


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    sortable_by = ('name',)


@register(Post)
class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (('user', 'location'),)}),
        (None, {'fields': (('image', 'des'),)}),
        (None, {'fields': ('tags', 'likes')}),
    )
    filter_horizontal = ('tags', 'likes')
    autocomplete_fields = ('user',)
    list_display = ('id', 'user', 'des', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')


@register(Board)
class BoardAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (('user', 'name'), 'posts')}),
    )
    filter_horizontal = ('posts',)
    autocomplete_fields = ('user',)
    list_display = ('id', 'user', 'name')
    search_fields = ('user__username', 'user__email')


@register(Comment)
class CommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (('user', 'post'), 'text')}),
    )
    autocomplete_fields = ('user', 'post')
    list_display = ('id', 'user', 'post', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')


@register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (('type', 'post'), ('user', 'user_notified'))}),
    )
    autocomplete_fields = ('user', 'post', 'user_notified')
    list_display = ('id', 'type', 'user', 'user_notified', 'post', 'date')
    list_filter = ('type', 'date')
    search_fields = ('user__username', 'user__email')
