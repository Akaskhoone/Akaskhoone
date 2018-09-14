import json
import redis
from rest_framework.views import APIView
from django.core import serializers
from social.models import *
from accounts.models import *
from rest_framework.permissions import AllowAny

Redis = redis.StrictRedis(host='localhost', port=6379, db=0)


class Private(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        for obj in serializers.deserialize("json", request.data["user"]):
            user = obj.object
        if request.data["type"] == "post":
            for obj in serializers.deserialize("json", request.data["post"]):
                post = obj.object
            data = NotificationData.objects.create(
                type="post",
                user=user,
                post=post
            )
            for follower in user.profile.followers.all():
                Notification.objects.create(
                    user=follower.user,
                    data=data
                )
        elif request.data["type"] == "like":
            for obj in serializers.deserialize("json", request.data["post"]):
                post = obj.object
            data = NotificationData.objects.create(
                type="like",
                user=user,
                post=post,
            )
            Notification.objects.create(
                user=post.user,
                data=data
            )
        elif request.data["type"] == "dislike":
            for obj in serializers.deserialize("json", request.data["post"]):
                post = obj.object
            data = NotificationData.objects.create(
                type="dislike",
                user=user,
                post=post
            )
            Notification.objects.create(
                user=post.user,
                data=data
            )
        elif request.data["type"] == "comment":
            for obj in serializers.deserialize("json", request.data["post"]):
                post = obj.object
            data = NotificationData.objects.create(
                type="comment",
                user=user,
                post=post
            )
            Notification.objects.create(
                user=post.user,
                data=data
            )
        elif request.data["type"] == "follow":
            for obj in serializers.deserialize("json", request.data["profile"]):
                profile = obj.object
            data = NotificationData.objects.create(
                type="follow",
                user=user,
                profile=profile
            )
            Notification.objects.create(
                user=profile.user,
                data=data
            )
        elif request.data["type"] == "unfollow":
            for obj in serializers.deserialize("json", request.data["profile"]):
                profile = obj.object
            data = NotificationData.objects.create(
                type="unfollow",
                user=user,
                profile=profile
            )
            Notification.objects.create(
                user=profile.user,
                data=data
            )
        elif request.data["type"] == "join":
            data = NotificationData.objects.create(
                type="join",
                user=user,
            )
            for friend in Contact.objects.get(email=user.email).users.all():
                Notification.objects.create(
                    user=friend,
                    data=data
                )
        return True


def push_to_queue(type, user, post=None, profile=None):
    if type == "like" or type == "dislike" or type == "comment" or type == "post":
        Redis.lpush("notifications",
                    json.dumps({"type": type, "user": serializers.serialize('json', [user]),
                                "post": serializers.serialize('json', [post])}))
    if type == "follow" or type == "unfollow":
        Redis.lpush("notifications",
                    json.dumps({"type": type, "user": serializers.serialize('json', [user]),
                                "post": serializers.serialize('json', [post])}))
    if type == "join":
        Redis.lpush("notifications",
                    json.dumps({"type": type, "user": serializers.serialize('json', [user])}))
