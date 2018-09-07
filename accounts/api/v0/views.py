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

            print("status: 400")
            print({"error": errors})
            return JsonResponse({"error": errors}, status=400)


class TokenRefreshView(TRV):
    def post(self, request, *args, **kwargs):
        try:
            return super(TokenRefreshView, self).post(request)
        except Exception as e:
            errors = {}
            for i in e.args[0]:
                if i == 'refresh':
                    errors.update({"Refresh": ["Required"]})

            print("status: 400")
            print({"error": errors})
            return JsonResponse({"error": errors}, status=400)


class TokenVerifyView(TVW):
    def post(self, request, *args, **kwargs):
        try:
            return super(TokenVerifyView, self).post(request)
        except Exception as e:
            errors = {}
            for i in e.args:
                if str(i).__contains__('invalid'):
                    errors.update({"access": ["Expired"]})
                elif str(i).__contains__('required'):
                    errors.update({"token": ["Required"]})

            print("status: 400")
            print({"error": errors})
            return JsonResponse({"error": errors}, status=400)


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
                "image": str(user.profile.image) if user.profile.image else "profile_photos/default.jpg"
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

        elif request.POST.get('name'):
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

    def get_errors(self, errors_as_json, key):
        errors = errors_as_json.get(key)
        errors_set = set()
        temp = []
        if errors:
            temp[:] = []
            for error in errors:
                errors_set.add(error["code"])
            if "invalid" in errors_set:
                temp.append("NotValid")
            if "Exist" in errors_set:
                temp.append("Exist")
            if 'required' in errors_set:
                temp.append("required")
            if "Length" in errors_set:
                temp.append("Length")
            if "Numeric" in errors_set:
                temp.append("Numeric")
            if "Common" in errors_set:
                temp.append("Common")
            if "Similar" in errors_set:
                temp.append("similar")
        return temp

    def post(self, request):
        check_exist = False
        try:
            check_exist = request.META.get('CONTENT_TYPE').__contains__('form-data')
        except Exception as e:
            pass
        if not check_exist:
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
            # fixme removing json, signup_form.errors is Dict type
            errors_as_json = json.loads(signup_form.errors.as_json())
            for error_type in ["email", "username", "password", "name"]:
                all_erros_of_the_type = self.get_errors(errors_as_json, error_type)
                if all_erros_of_the_type:
                    errors[error_type] = all_erros_of_the_type

            print("status: 400")
            print({"error": errors})
            return JsonResponse({"error": errors}, status=400)


class FollowersAPIView(APIView):
    """
    This class return a list of JSONs that contain a string, name (as 'name'), and a boolean, followed (as 'followed)
    that determines whether the requester followed the USER or not.

    Target (if it gives a username or email , user is the User object that having the given email or the given username,
    else it returns the requester`s own User object)
    USERs are chosen from the Target Following List in DateBase

    """

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
    """
    This class got two parts, first one is gonna return Followings list to GET requests and second one serves follow
    and Unfollow requests that comes as a POST request.
    """

    def get(self, request):
        """
        This def return a list of JSONs that contain a string, name (as 'name'), and a boolean, followed (as 'followed)
        that determines whether the requester followed the USER or not.

        USERs are chosen from the Requester Following List in DateBase
        """
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
        """
        This def handles two functions, first is Follow Request and Second is Unfollow request
        and both returns a message and a key that shows weather the request served successfully or not
        """
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
