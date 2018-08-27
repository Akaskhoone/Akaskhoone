from accounts.api.v0.serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse

from django.contrib.auth.password_validation import validate_password
from accounts.validators import UnicodeNameValidator, UnicodeUsernameValidator


class GetProfile(APIView):
    def get(self, request):
        p = Profile.objects.get(user=request.user)
        ps = ProfileSerializer(p)
        return JsonResponse(ps.data)


class UpdatePassword(APIView):
    def post(self, request):
        user = request.user
        if user.check_password(request.data['old_password']):
            validate_password(request.data['new_password'], user=user, password_validators=None)
            user.set_password(request.data['new_password'])
            user.save()
            return JsonResponse({"status": "Password changed successfully"})
        else:
            return JsonResponse({"status": "The given old password is not true"})


class Signup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        new_user_data = {
            "email": request.data["email"],
            "username": request.data["username"],
            "password": request.data["password"]
        }
        UnicodeUsernameValidator()(request.data["username"])
        user_serializer = UserSerializer(data=dict(new_user_data))
        if user_serializer.is_valid():
            UnicodeNameValidator()(request.data["name"])
            user = user_serializer.save()
            new_profile_data = {
                "user": user.id,
                "name": request.data["name"],
                "bio": request.data["bio"],
                # "image": request.data["image"],
            }
            profile_serializer = ProfileSerializer(data=new_profile_data)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return JsonResponse({"status": "User created successfully"})
            else:
                return JsonResponse({"status": "Can not to create a profile with given data"}, status=400)
        else:
            return JsonResponse({"status": "Can not to create a user with given data"}, status=400)


class EditProfile(APIView):
    def post(self, request):
        p = Profile.objects.get(user=request.user)
        p.bio = request.data["bio"]
        UnicodeNameValidator()(request.data["name"])
        p.name = request.data["first_name"]
        p.save()
        return JsonResponse({"status": "profile updated"})
