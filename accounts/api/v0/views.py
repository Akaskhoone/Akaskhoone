from accounts.api.v0.serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse

from django.contrib.auth.password_validation import validate_password
from accounts.validators import UnicodeNameValidator, UnicodeUsernameValidator


class ProfileAPIView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                data = {
                    "username": username,
                    "email": user.email,
                    "name": user.profile.name,
                    "bio": user.profile.bio,
                    "followers": user.profile.followers.count(),
                    "followings": user.profile.followings.count(),
                    "image": user.profile.image.url
                }
                return JsonResponse(data)
            except Exception as e:
                return JsonResponse({"error": {"Profile":["NotExist"]}})

        email = request.query_params.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                data = {
                    "username": user.username,
                    "email": email,
                    "name": user.profile.name,
                    "bio": user.profile.bio,
                    "followers": user.profile.followers.count(),
                    "followings": user.profile.followings.count(),
                    "image": user.profile.image.url
                }
                return JsonResponse(data)
            except Exception as e:
                return JsonResponse({"error": {"Profile": ["NotExist"]}})

        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "name": user.profile.name,
            "bio": user.profile.bio,
            "followers": user.profile.followers.count(),
            "followings": user.profile.followings.count(),
            "image": user.profile.image.url
        }
        return JsonResponse(data)

    # def put(self, request):
    #     user = request.user
    #     if user.check_password(request.data['old_password']):
    #         try:
    #             validate_password(request.data['new_password'], user=user, password_validators=None)
    #         except Exception as e:
    #             return JsonResponse({"error": {"new_password": ["Common, Length, Numeric, NotUnicode"]}})
    #         user.set_password(request.data['new_password'])
    #         user.save()
    #         return JsonResponse({"success": {"message": ["user password changed"]}})
    #     else:
    #         return JsonResponse({"error": {"old_password": ["NotMatch"]}})

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
            return JsonResponse({"error": "you have already followed user with user_id: {}".format(user_id)},
                                status=403)

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
