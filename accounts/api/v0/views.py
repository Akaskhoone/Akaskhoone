from accounts.api.v0.serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from accounts.api.utils import get_user, get_password_errors
from django.contrib.auth.password_validation import validate_password
from accounts.forms import SignUpForm, ProfileEditForm
from rest_framework_simplejwt.views import TokenObtainPairView as TOPW, TokenRefreshView as TRV, TokenVerifyView as TVW
import json


class TokenObtainPairView(TOPW):
    def post(self, request, *args, **kwargs):
        try:
            return super(TokenObtainPairView, self).post(request)
        except Exception as e:
            errors = {}
            for i in e.args[0]:
                if i == 'non_field_errors':
                    errors.update({"RequestError": ["WrongCredentials"]})
                elif i == 'email':
                    errors.update({"email": ["Required"]})
                elif i == 'password':
                    errors.update({"password": ["Required"]})
            return JsonResponse({"error": errors}, status=400)


class TokenRefreshView(TRV):
    pass


class TokenVerifyView(TVW):
    pass


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
            print("status: 200")
            print(data)
            return JsonResponse(data, status=200)
        except Exception as e:
            print("status: 400")
            print({"error": {"Profile": ["NotExist"]}})
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
                    print("status: 200")
                    print({"message": "user password changed"})
                    return JsonResponse({"message": "user password changed"}, status=200)
                except Exception as e:
                    print("status: 400")
                    print({"error": {"new_password": get_password_errors(e)}})
                    return JsonResponse({"error": {"new_password": get_password_errors(e)}}, status=400)
            else:
                print("status: 400")
                print({"error": {"old_password": ["NotMatch"]}})
                return JsonResponse({"error": {"old_password": ["NotMatch"]}}, status=400)

        elif request.POST['name']:
            profile_edit_form = ProfileEditForm(data=request.POST, files=request.FILES)
            if profile_edit_form.is_valid():
                profile_edit_form.save(user=request.user)
                user = request.user
                data = {
                    "username": user.username,
                    "email": user.email,
                    "name": user.profile.name,
                    "bio": user.profile.bio,
                    "followers": user.profile.followers.count(),
                    "followings": user.profile.followings.count(),
                    "image": user.profile.image.url if user.profile.image else "/media/profile_photos/default.jpg"
                }
                print("status: 200")
                print(data)
                return JsonResponse(data, status=200)
            else:
                print("status: 400")
                print({"error": {"image": ["Size"]}})
                return JsonResponse({"error": {"image": ["Size"]}}, status=400)

        else:
            errors = {}
            if not old_password:
                errors.update({"old_password": ["Required"]})
            if not new_password:
                errors.update({"new_password": ["Required"]})

            print("status: 400")
            print({"error": errors})
            return JsonResponse({"error": errors}, status=400)


class Signup(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        if not request.POST:
            email = request.data.get('email')
            password = request.data.get('password')
            if email:
                errors = {}
                try:
                    User.objects.get(email=email)
                    errors.update({"email": ["Exist"]})
                except Exception as e:
                    pass
                if password:
                    try:
                        validate_password(password)
                    except Exception as e:
                        errors.update({"password": get_password_errors(e)})
                if errors:
                    print("status: 400")
                    print({"error": errors})
                    return JsonResponse({"error": errors}, status=400)
                else:
                    print("status: 200")
                    print({"message": "user can be created"})
                    return JsonResponse({"message": "user can be created"}, status=200)
            else:
                print("status: 400")
                print({"error": {"email": ["Required"]}})
                return JsonResponse({"error": {"email": ["Required"]}}, status=400)

        signup_form = SignUpForm(data=request.POST, files=request.FILES)
        if signup_form.is_valid():
            signup_form.save()
            print("status: 200")
            print({"message": "user created successfully"})
            return JsonResponse({"message": "user created successfully"}, status=200)
        else:
            errors = {}
            errors_as_json = json.loads(signup_form.errors.as_json())

            email_errors = errors_as_json.get("email")
            email_errors_set = set()
            if email_errors:
                temp = []
                for email_error in email_errors:
                    email_errors_set.add(email_error["code"])
                if "invalid" in email_errors_set:
                    temp.append("NotValid")
                if "Exists" in email_errors_set:
                    temp.append("Exists")
                errors["email"] = temp

            username_errors = errors_as_json.get("username")
            if username_errors:
                temp = []
                for username_error in username_errors:
                    temp.append(username_error["code"])
                errors["username"] = temp

            name_errors = errors_as_json.get("name")
            if name_errors:
                temp = []
                for name_error in name_errors:
                    temp.append(name_error["code"])
                errors["name"] = temp

            password_errors = errors_as_json.get("password")
            password_errors_set = set()
            if password_errors:
                temp = []
                for password_error in password_errors:
                    password_errors_set.add(password_error["code"])
                if "password_too_short" in password_errors_set:
                    temp.append("Length")
                if "password_too_common" in password_errors_set:
                    temp.append("Common")
                if "password_entirely_numeric" in password_errors_set:
                    temp.append("Numeric")
                errors["password"] = temp

            print("status: 400")
            print({"error": errors})
            return JsonResponse({"error": errors}, status=400)


class FollowersAPIView(APIView):
    def get(self, request):
        if get_user(request):
            print("status: 400")
            print({"error": {"Profile": ["NotExist"]}})
            return JsonResponse({"error": {"Profile": ["NotExist"]}}, status=400)
        user = get_user(request)
        requester = request.user
        ret = {}
        for item in user.profile.followers.all():
            try:
                requester.profile.followings.get(pk=item.pk)
                ret.update({item.user.username: {'name': item.name, 'followed': True}})
            except Exception as e:
                ret.update({item.user.username: {'name': item.name, 'followed': False}})
        return JsonResponse(ret)


class FollowingsAPIView(APIView):
    def get(self, request):
        if get_user(request):
            return JsonResponse({"error": {"Profile": ["NotExist"]}}, status=400)
        user = get_user(request)
        requester = request.user
        ret = {}
        for item in user.profile.followings.all():
            try:
                requester.profile.followings.get(pk=item.pk)
                ret.update({item.user.username: {'name': item.name, 'followed': True}})
            except Exception as e:
                ret.update({item.user.username: {'name': item.name, 'followed': False}})
        return JsonResponse(ret)

    def post(self, request):
        username = request.data.get('follow')
        if username:
            try:
                user = User.objects.get(username=username)
                requester = request.user
                if user == requester:
                    return JsonResponse({"error": {"Profile": ["NotExist"]}}, status=400)
                try:
                    requester.profile.followings.get(username=user)
                    return JsonResponse({"success": {"message": ["followed successfully"]}}, status=200)
                except Exception as e:
                    requester.profile.followings.add(user)
                    return JsonResponse({"success": {"message": ["followed successfully"]}}, status=200)
            except Exception as e:
                return JsonResponse({"error": {"user": ["NotExist"]}}, status=400)

        username = request.data.get('unfollow')
        try:
            user = User.objects.get(username=username)
            requester = request.user
            if user == requester:
                return JsonResponse({"error": {"Profile": ["NotExist"]}}, status=400)
            try:
                requester.profile.followings.remove(user.profile.id)
                return JsonResponse({"success": {"message": ["unfollowed successfully"]}}, status=200)
            except Exception as e:
                return JsonResponse({"success": {"message": ["unfollowed successfully"]}}, status=200)
        except Exception as e:
            return JsonResponse({"error": {"user": ["NotExist"]}}, status=400)
