from django.http import JsonResponse
from users.serializers import *
from rest_framework.views import APIView


class Users(APIView):

    def get(self, request, format=None):
        content = {
            'user': "user user",
            'auth': "auth auth",
        }
        return JsonResponse(content)
