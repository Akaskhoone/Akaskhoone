import json

from django import forms
from django.core import serializers
from .models import *
import redis

Redis = redis.StrictRedis(host='localhost', port=6379, db=0)


class CreatePostFrom(forms.Form):
    image = forms.ImageField(required=True)
    des = forms.CharField(required=False, max_length=250)
    location = forms.CharField(required=False, max_length=100)
    tags = forms.CharField(required=False, max_length=250)

    def save(self, user):
        tags = self.cleaned_data["tags"].split()
        for tag in tags:
            Tag.objects.get_or_create(name=tag)
        new_post = Post.objects.create(user=user, image=self.cleaned_data["image"], des=self.cleaned_data["des"],
                                       location=self.cleaned_data["location"])
        new_post.tags.add(*tags)
        Redis.lpush("notifications", json.dumps({"type": "post", "user": serializers.serialize('json', [user]),
                                                 "post": serializers.serialize('json', [new_post])}))
