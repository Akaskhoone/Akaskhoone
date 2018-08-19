from django.http import JsonResponse
from users.serializers import *
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class Users(APIView):
    # authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, format=None):
        content = {
            'user': "user user",
            'auth': "auth auth",
        }
        return JsonResponse(content)
