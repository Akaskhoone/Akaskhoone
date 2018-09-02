from accounts.api.v0.serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse

from django.contrib.auth.password_validation import validate_password
from accounts.validators import UnicodeNameValidator, UnicodeUsernameValidator


def get_user(request):
    username = request.query_params.get('username')
    if username:
        try:
            return User.objects.get(username=username)
        except:
            return None
    email = request.query_params.get('email')
    if email:
        try:
            return User.objects.get(email=email)
        except:
            return None
    return request.user


def get_password_errors(e):
    errors = []
    for i in e.args[0]:
        if str(list(i)[0]).__contains__('similar'):
            errors.append("Similar")
        elif str(list(i)[0]).__contains__('short'):
            errors.append("Length")
        elif str(list(i)[0]).__contains__('numeric'):
            errors.append("Numeric")
        elif str(list(i)[0]).__contains__('common'):
            errors.append("Common")
    return errors


class ProfileAPIView(APIView):
    def get(self, request):
        user = get_user(request)
        try:
            data = {
                "username": user.username,
                "email": user.email,
                "name": user.profile.name,
                "bio": user.profile.bio,
                "followers": user.profile.followers.count(),
                "followings": user.profile.followings.count(),
                "image": user.profile.image.url if user.profile.image else "/media/profile_photos/default.jpg"
            }
            return JsonResponse(data, status=200)
        except Exception as e:
            return JsonResponse({"error": {"Profile": ["NotExist"]}}, status=400)

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if old_password and new_password:
            if user.check_password(old_password):
                try:
                    validate_password(new_password, user=user, password_validators=None)
                    user.set_password(new_password)
                    user.save()
                    return JsonResponse({"message": "user password changed"}, status=200)
                except Exception as e:
                    errors = []
                    for i in e.args[0]:
                        if str(list(i)[0]).__contains__('similar'):
                            errors.append("Similar")
                        elif str(list(i)[0]).__contains__('short'):
                            errors.append("Length")
                        elif str(list(i)[0]).__contains__('numeric'):
                            errors.append("Numeric")
                        elif str(list(i)[0]).__contains__('common'):
                            errors.append("Common")
                    return JsonResponse({"error": {"new_password": errors}}, status=400)
            else:
                return JsonResponse({"error": {"old_password": ["NotMatch"]}}, status=400)
        else:
            errors = {}
            if not old_password:
                errors.update({"old_password": ["Required"]})
            if not new_password:
                errors.update({"new_password": ["Required"]})
            return JsonResponse({"error": errors}, status=400)


class Signup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if not request.FILES:
            email = request.data.get('email')
            password = request.data.get('password')
            if email and password:
                pass
            else:
                errors = {}
                if not email:
                    errors.update({"email": ["Required"]})
                if not password:
                    errors.update({"password": ["Required"]})
                return JsonResponse({"error": errors}, status=400)


# class EditProfile(APIView):
#     def post(self, request):
#         p = Profile.objects.get(user=request.user)
#         p.bio = request.data["bio"]
#         UnicodeNameValidator()(request.data["name"])
#         p.name = request.data["first_name"]
#         p.save()
#         return JsonResponse({"status": "profile updated"})


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
