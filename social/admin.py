from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import *


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass


@register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@register(NOtificationData)
class NotificationDataAdmin(admin.ModelAdmin):
    pass
