from django.http import JsonResponse
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny

from api.validators import NameValidator
from users.serializers import *
from posts.serializers import PostSerializer
from rest_framework.views import APIView
from posts.models import *
<<<<<<< HEAD
from posts.forms import UploadImageForm
from django.contrib.auth.password_validation import validate_password
from api.validators import *
=======
from users.models import Profile
from django.core import serializers
>>>>>>> S1_posts

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
        NameValidator()(request.data["first_name"])
        UsernameValidator()(request.data["username"])
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
                return JsonResponse({"status": "User created successfully"})
            else:
                return JsonResponse({"status": "Can not to create a profile with given data"}, status=400)
        else:
            return JsonResponse({"status": "Can not to create a user with given data"}, status=400)


class EditProfile(APIView):
    def post(self, request):
        p = Profile.objects.get(user=request.user)
        p.bio = request.data["bio"]

        NameValidator()(request.data["first_name"])

        p.user.first_name = request.data["first_name"]
        p.user.save()
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


class PostView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        image_serializer = PostSerializer(data=request.data)
        if str(request.user.pk) != str(request.data["user"]):
            raise serializers.ValidationError("the author is not validated!")
        if image_serializer.is_valid():
            image_serializer.save()
            return JsonResponse({"status": "Successfully created!"})
        else:
            return JsonResponse({"status": "Post creation failed!"})


class GetUserPosts(APIView):
    def get(self, request, format=None):
        user = User.objects.get(id=request.query_params["user_id"])
        return JsonResponse({
            "posts": serializers.serialize("json", Post.objects.filter(user=user))
        })


class GetUser(APIView):
    def get(self, request, user_id, format=None):
        return JsonResponse({
            'user': serializers.serialize(Profile.objects.get(user_id=user_id))
        })


class FollowUser(APIView):
    def get(self, request, user_id, format=None):
        try:
            from_profile = Profile.objects.get(user_id=request.user.id)
        except:
            return JsonResponse({"error": "you don't have profile, sorry!"}, status=403)

        try:
            to_profile = Profile.objects.get(user_id=user_id)
        except:
            return JsonResponse(
                {"error": "user with user_id: {} does not have profile!".format(user_id).format(user_id)}, status=403)

        if to_profile.user_id == from_profile.user_id:
            return JsonResponse({"error": "you can not follow yourself!"}, status=403)

        if to_profile in list(from_profile.followings.all()):
            return JsonResponse({"error": "you have already followed user with user_id: {}".format(user_id)}, status=403)

        from_profile.followings.add(to_profile)
        return JsonResponse({"status": "Successful!"})


class UnFollow(APIView):
    def get(self, request, user_id, format=None):
        try:
            from_profile = Profile.objects.get(user_id=request.user.id)
        except:
            return JsonResponse({"error": "you don't have profile, sorry!"}, status=403)

        try:
            to_profile = Profile.objects.get(user_id=user_id)
        except:
            return JsonResponse(
                {"error": "user with user_id: {} does not have profile!".format(user_id).format(user_id)}, status=403)

        if to_profile not in list(from_profile.followings.all()):
            return JsonResponse({"error": "you don't follow user with user_id: {}".format(user_id)}, status=403)

        from_profile.followings.remove(to_profile)
        return JsonResponse({"status": "Successful!"})