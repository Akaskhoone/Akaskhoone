from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from users.serializers import *
from rest_framework.views import APIView
from posts.models import *
from django.contrib.auth.password_validation import validate_password

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
    def post(self, request):
        p = Profile.objects.get(user=request.user)
        p.bio = request.data["bio"]
        p.user.first_name = request.data["first_name"]
        p.save()
        return JsonResponse({"status": "profile updated"})


class GetAllTags(APIView):
    def get(self, request):
        return JsonResponse({
            "tags": [str(t) for t in Tag.objects.all()]
        })


class Tags(APIView):

    def get(self, request, formant=None):
        query = request.query_params['name']
        matched_tags = [str(t) for t in Tag.objects.filter(name__startswith=query)]
        return JsonResponse({
            "matched_tags": matched_tags
        })
