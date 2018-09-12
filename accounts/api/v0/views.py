from accounts.api.v0.serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from accounts.api.utils import get_user, get_password_errors
from django.contrib.auth.password_validation import validate_password
from accounts.forms import SignUpForm, ProfileEditForm
from rest_framework_simplejwt.views import TokenObtainPairView as TOPW, TokenRefreshView as TRV, TokenVerifyView as TVW
from akaskhoone.exceptions import error_data, success_data
from accounts.api.utils import *
from accounts.models import *
from django.db.models import Q
import json


class TokenObtainPairView(TOPW):
    def post(self, request, *args, **kwargs):
        try:
            return super(TokenObtainPairView, self).post(request)
        except Exception as e:
            errors = error_data()
            for i in e.args[0]:
                if i == 'non_field_errors':
                    errors = error_data(__data__=errors, RequestError="WrongCredentials")
                elif i == 'email':
                    errors = error_data(__data__=errors, email="Required")
                elif i == 'password':
                    errors = error_data(__data__=errors, password="Required")

            print("status: 400", errors)
            return JsonResponse(errors, status=400)


class TokenRefreshView(TRV):
    def post(self, request, *args, **kwargs):
        try:
            return super(TokenRefreshView, self).post(request)
        except Exception as e:
            errors = error_data()
            for i in e.args[0]:
                if i == 'refresh':
                    errors = error_data(refresh="Required")

            print("status: 400", errors)
            return JsonResponse(errors, status=400)


class TokenVerifyView(TVW):
    def post(self, request, *args, **kwargs):
        try:
            return super(TokenVerifyView, self).post(request)
        except Exception as e:
            errors = error_data()
            for i in e.args:
                if str(i).__contains__('invalid'):
                    errors = error_data(access="Expired")
                elif str(i).__contains__('required'):
                    errors = error_data(token="Required")

            print("status: 400", errors)
            return JsonResponse(errors, status=400)


class ProfileAPIView(APIView):
    def get(self, request):
        if request.query_params == {}:
            try:
                profile = ProfileSerializer(request.user.profile)
                return JsonResponse(profile.data, status=200)
            except Exception as e:
                return JsonResponse(error_data(profile="NotExist"), status=400)

        username = request.query_params.get("username")
        if username:
            try:
                target_user = User.objects.get(username=username)
                profile = ProfileSerializer(target_user.profile, requester=request.user.profile)
                return JsonResponse(profile.data, status=200)
            except Exception as e:
                return JsonResponse(error_data(profile="NotExist"), status=400)

        email = request.query_params.get("email")
        if email:
            try:
                target_user = User.objects.get(email=email)
                profile = ProfileSerializer(target_user.profile, requester=request.user.profile)
                return JsonResponse(profile.data, status=200)
            except Exception as e:
                print(e)
                return JsonResponse(error_data(profile="NotExist"), status=400)

        search = request.query_params.get("search")
        if search:
            try:
                filtered_profiles = Profile.objects.filter(
                    Q(user__username__contains=search) | Q(name__contains=search)).exclude(user=request.user)
                profiles = []
                for profile in filtered_profiles:
                    profiles.append(ProfileSerializer(profile, requester=request.user.profile,
                                                      fields=(
                                                          "username", "name", "image", "private", "isFollowed")).data)
                return JsonResponse({"data": profiles}, status=200)
            except Exception as e:
                return JsonResponse({"data": []}, status=200)

        return JsonResponse(error_data(request="Invalid"), status=400)

    def put(self, request):
        user = request.userrequester
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if old_password and new_password:
            if user.check_password(old_password):
                try:
                    validate_password(new_password, user=user, password_validators=None)
                    user.set_password(new_password)
                    user.save()
                    print("status: 200", success_data("PasswordChanged"))
                    return JsonResponse(success_data("PasswordChanged"), status=200)
                except Exception as e:
                    print("status: 400", error_data(new_password=get_password_errors(e)))
                    return JsonResponse(error_data(new_password=get_password_errors(e)), status=400)
            else:
                print("status: 400", error_data(old_password="NotMatch"))
                return JsonResponse(error_data(old_password="NotMatch"), status=400)

        elif request.POST.get('name'):
            profile_edit_form = ProfileEditForm(data=request.POST, files=request.FILES)
            if profile_edit_form.is_valid():
                profile_edit_form.save(user=request.user)
                profile = ProfileSerializer(request.user.profile)
                print("status: 200", profile.data)
                return JsonResponse(profile.data, status=200)
            else:
                print("status: 400", error_data(image="Size"))
                return JsonResponse(error_data(image="Size"), status=400)

        else:
            errors = error_data()
            if not old_password:
                errors = error_data(old_password="Required")
            if not new_password:
                errors = error_data(new_password="Required")
            print("status: 400", errors)
            return JsonResponse(errors, status=400)


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
                errors = error_data()
                try:
                    User.objects.get(email=email)
                    errors = error_data(email="Exist")
                except Exception as e:
                    pass
                if password:
                    try:
                        validate_password(password)
                    except Exception as e:
                        errors = error_data(password=get_password_errors(e))
                if errors:
                    print("status: 400", errors)
                    return JsonResponse(errors, status=400)
                else:
                    print("status: 200", success_data("CanBeCreated"))
                    return JsonResponse(success_data("CanBeCreated"), status=200)
            else:
                print("status: 400", error_data(email="Required"))
                return JsonResponse(error_data(email="Required"), status=400)

        signup_form = SignUpForm(data=request.POST, files=request.FILES)
        if signup_form.is_valid():
            signup_form.save()
            print("status: 200", success_data("UserCreated"))
            return JsonResponse(success_data("UserCreated"), status=200)
        else:
            errors = {}
            # fixme removing json, signup_form.errors is Dict type
            errors_as_json = json.loads(signup_form.errors.as_json())
            for error_type in ["email", "username", "password", "name"]:
                all_erros_of_the_type = self.get_errors(errors_as_json, error_type)
                if all_erros_of_the_type:
                    errors[error_type] = all_erros_of_the_type

            print("status: 400", {"error": errors})
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
        if not get_user(request):
            print("status: 400", error_data(profile="NotExist"))
            return JsonResponse(error_data(profile="NotExist"), status=400)
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
        if not get_user(request):
            print("status: 400", error_data(profile="NotExist"))
            return JsonResponse(error_data(profile="NotExist"), status=400)
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
                    print("status: 400", error_data(profile="NotExist"))
                    return JsonResponse(error_data(profile="NotExist"), status=400)
                try:
                    requester.profile.followings.get(user.profile)
                    print("status: 200", success_data("FollowedSuccessfully"))
                    return JsonResponse(success_data("FollowedSuccessfully"), status=200)
                except Exception as e:
                    if user.profile.private:
                        user.profile.requests.add(requester.profile)
                        print("status: 200", success_data("RequestedSuccessfully"))
                        return JsonResponse(success_data("RequestedSuccessfully"), status=200)
                    requester.profile.followings.add(user.profile)
                    print("status: 200", success_data("FollowedSuccessfully"))
                    return JsonResponse(success_data("FollowedSuccessfully"), status=200)
            except Exception as e:
                print("status: 400", error_data(profile="NotExist"))
                return JsonResponse(error_data(profile="NotExist"), status=400)

        username = request.data.get('unfollow')
        if username:
            try:
                user = User.objects.get(username=username)
                requester = request.user
                if user == requester:
                    print("status: 400", error_data(profile="NotExist"))
                    return JsonResponse(error_data(profile="NotExist"), status=400)
                try:
                    requester.profile.followings.remove(user.profile.id)
                    print("status: 200", success_data("UnFollowedSuccessfully"))
                    return JsonResponse(success_data("UnFollowedSuccessfully"), status=200)
                except Exception as e:
                    print("status: 200", success_data("UnFollowedSuccessfully"))
                    return JsonResponse(success_data("UnFollowedSuccessfully"), status=200)
            except Exception as e:
                print("status: 400", error_data(profile="NotExist"))
                return JsonResponse(error_data(profile="NotExist"), status=400)

        username = request.data.get('accept')
        if username:
            try:
                user = User.objects.get(username=username)
                requester = request.user
                if user == requester:
                    print("status: 400", error_data(profile="NotExist"))
                    return JsonResponse(error_data(profile="NotExist"), status=400)
                if user.profile in requester.profile.requests.all():
                    user.profile.followings.add(requester.profile)
                    requester.profile.requests.remove(user.profile)
                    print("status: 200", success_data("AcceptedSuccessfully"))
                    return JsonResponse(success_data("AcceptedSuccessfully"), status=200)
                else:
                    print("status: 400", error_data(profile="RequestNotExist"))
                    return JsonResponse(error_data(profile="RequestNotExist"), status=400)

            except Exception as e:
                print("status: 400", error_data(profile="NotExist"))
                return JsonResponse(error_data(profile="NotExist"), status=400)

        print("status: 400", error_data(request="WrongData"))
        return JsonResponse(error_data(request="WrongData"), status=400)


class InvitationAPIView(APIView):
    def post(self, request):
        ret = {}
        requester = request.user
        for email in request.data.get("contacts"):
            try:
                user = User.objects.get(email=email)
                try:
                    requester.profile.followings.get(user=user)
                    ret.update({'email': email, 'username': user.username, 'followed': True})
                except Exception as e:
                    ret.update({'email': email, 'username': user.username, 'followed': False})

            except Exception as e:
                contact = Contact.objects.get_or_create(email=email)[0]
                invitation = Invitation.objects.get_or_create(contact=contact, user=requester)[0]
                if invitation.invited:
                    ret.update({'email': email, 'invited': True})
                else:
                    ret.update({'email': email, 'invited': False})
        return JsonResponse(ret, status=200)

    def put(self, request):
        requester = request.user
        email = request.data.get('email')
        if not email:
            return JsonResponse({"error": {"email": ["required"]}}, status=400)
        try:
            contact = Contact.objects.get(email=email)
            try:
                invitation = requester.invitations.get(contact=contact)
                sending_mail(email, "Akaskhoone Invitation",
                             "Hi there,\n{} invited you to join us at Akaskhooneh".format(requester.username))
                invitation.invited = True
                return JsonResponse(success_data("ContactInvited"), status=200)
            except Exception as e:
                print("status: 400", error_data(request="InvitationError"))
                return JsonResponse(error_data(request="InvitationError"), status=400)
        except Exception as e:
            print("status: 400", error_data(contact="NotExist"))
            return JsonResponse(error_data(contact="NotExist"), status=400)


class ResetPasswordAPIView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data.get('email')
            user1 = User.objects.get(email=email)
            try:
                username = request.data.get('username')
                user2 = User.objects.get(username=username)
                if user1 == user2:
                    password = User.objects.make_random_password()
                    sending_mail(email, "Reset Password",
                                 "Hi {}\nYour new password is: {}".format(user1.profile.name, password))
                    user1.set_password(password)
                    user1.save()
                    return JsonResponse({"message": "success"}, status=200)
                else:
                    return JsonResponse({"message": "success"}, status=200)
            except Exception as e:
                return JsonResponse({"message": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"message": "success"}, status=200)
