import redis, json
from rest_framework.views import APIView
from social.models import Notification
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .utils import success_data, error_data

r = redis.StrictRedis(host='localhost', port=6379, db=0)


class PrivateAPIView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            Notification.objects.create(
                type=request.data.get("notify_type"),
                user_id=request.data.get("user_id"),
                post_id=request.data.get("post_id"),
                user_notified_id=request.data.get("user_notified_id"),
            )
            return JsonResponse(success_data("NotifySent"))
        except Exception as e:
            return JsonResponse(error_data(request="WrongData"), status=400)


def notify(notify_type, user_id, post_id=None, users_notified=None):
    r.lpush("notifications",
            json.dumps(
                {"notify_type": notify_type,
                 "user_id": user_id,
                 "post_id": post_id,
                 "users_notified": users_notified
                 }))
