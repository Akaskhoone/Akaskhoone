from django.http import JsonResponse
# from
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from users.serializers import *
from rest_framework.views import APIView


class Users(APIView):

    def get(self, request, format=None):
        content = {
            'user': "user user",
            'auth': "auth auth",
        }
        return JsonResponse(content)


class Signup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        newUserData = {
            "email": request.data["email"],
            "username": request.data["username"],
            "first_name": request.data["first_name"],
            "password": request.data["password"]
        }
        userSerializer = UserSerializer(data=dict(newUserData))
        if userSerializer.is_valid():
            print("validated")
            user = userSerializer.save()
            newProfileData = {
                "user": user.id,
                "bio": request.data["bio"],
                # "image": request.data["image"],
            }
            profileSerializer = ProfileSerializer(data=newProfileData)
            if profileSerializer.is_valid():
                profileSerializer.save()
                return JsonResponse({"status": "user created"})
            else:
                return JsonResponse({"status": "error profile exists"})
        else:
            return JsonResponse({"status": "error user exists"})
