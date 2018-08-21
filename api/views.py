from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from users.serializers import *
from rest_framework.views import APIView


class GetProfile(APIView):
    def get(self, request, format=None):
        p = Profile.objects.get(user=request.user)
        ps = ProfileSerializer(p)
        return JsonResponse(ps.data)


class Signup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        new_user_data = {
            "email": request.data["email"],
            "username": request.data["username"],
            "first_name": request.data["first_name"],
            "password": request.data["password"]
        }
        user_serializer = UserSerializer(data=dict(new_user_data))
        if user_serializer.is_valid():
            print("validated")
            user = user_serializer.save()
            new_profile_data = {
                "user": user.id,
                "bio": request.data["bio"],
                # "image": request.data["image"],
            }
            profile_serializer = ProfileSerializer(data=new_profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return JsonResponse({"status": "user created"})
            else:
                return JsonResponse({"status": "error profile exists"})
        else:
            return JsonResponse({"status": "error user exists"})


class EditProfile(APIView):

    def post(self, request, format=None):
        p = Profile.objects.get(user=request.user)
        p.bio = request.data["bio"]
        p.user.firstname = request.data["first_name"]
        p.save()
        return JsonResponse({"status": "profile updated!"})