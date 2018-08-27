from accounts.api.utils import APIJWTTestCase
from .serializers import *
from django.urls import reverse
from django.core.exceptions import *


class APILoginTest(APIJWTTestCase):
    def test_login_with_real_user(self):
        print('>>> test login with real user')
        User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        result, response = self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'access')

    def test_login_with_fake_user(self):
        print('>>> test login with fake user')
        response = self.client.post(reverse("api:v0:login"), {'email': 'aasmpro@admin.com', 'password': 'passaasmpro'})
        self.assertEqual(response.status_code, 400)


class APIAuthorizationTest(APIJWTTestCase):
    def test_authorization_needed(self):
        print('>>> test authorization needed')
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 401)
        u = User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        Profile.objects.create(user_id=u.id, bio='testing profile')
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)


class APIUsersTest(APIJWTTestCase):
    def test_getting_user_profile(self):
        print('>>> test getting user profile')
        u = User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        Profile.objects.create(user_id=u.id, bio='testing profile')
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,
                             '{"id": 1, "bio": "testing profile", "image": null, "user": 1, "followers": [], "followings": []}')


class APIChangePasswordTest(APIJWTTestCase):
    def test_login_after_change(self):
        User.objects.create_user('reza', 'reza@admin.com', 'passreza')
        self.client.login(email='reza@admin.com', password='passreza')
        self.client.post(reverse("api:v0:change_password"), {'old_password': 'passreza', 'new_password': 'rezareza'})
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'mamadmamad'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'rezareza'})
        self.assertEqual(response.status_code, 200)

    def test_valid_password(self):
        User.objects.create_user('reza', 'reza@admin.com', 'passreza')
        self.client.login(email='reza@admin.com', password='passreza')

        # common_pass
        try:
            self.client.post(reverse("api:v0:change_password"),
                             {'old_password': 'passreza', 'new_password': '12345678'})
        except ValidationError as e:
            # print(E.messages)
            self.assertListEqual(e.messages, ['This password is too common.', 'This password is entirely numeric.'])
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)

        # min_lenght
        try:
            self.client.post(reverse("api:v0:change_password"), {'old_password': 'passreza', 'new_password': 'j43n54'})
        except ValidationError:
            pass
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'j43n54'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)

        # Numerical_pass
        try:
            self.client.post(reverse("api:v0:change_password"),
                             {'old_password': 'passreza', 'new_password': '1231423223453'})
        except ValidationError:
            pass
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': '1231423223453'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)


class APISignUpTest(APIJWTTestCase):
    def test_create(self):
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

    def test_requaired_fields(self):
        # username
        try:
            self.client.post(reverse("api:v0:signup"),
                             {'username': '', 'first_name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza',
                              'bio': 'salam'})
        except ValidationError:
            pass

        # firs_name
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'mamad', 'first_name': '', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'khubi'})
        self.assertEqual(response.status_code, 200)

        # email
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': '',
                                     'password': 'passfatemeh', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # password
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'sina', 'first_name': 'sina', 'email': 'sina@admin.com',
                                     'password': '', 'bio': 'reza'})
        self.assertEqual(response.status_code, 400)

        # bio
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'ali', 'first_name': 'ali', 'email': 'ali@admin.com',
                                     'password': 'passaliali', 'bio': ''})
        self.assertEqual(response.status_code, 200)

    def test_uique_fields(self):
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

        # username
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'reza', 'first_name': 'mamad', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'khubi'})
        self.assertEqual(response.status_code, 400)

        # first_name
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'ali', 'first_name': 'reza', 'email': 'ali@admin.com',
                                     'password': 'passaliali', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 200)

        # email
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'reza@admin.com',
                                     'password': 'passfatemeh', 'bio': 'reza'})
        self.assertEqual(response.status_code, 400)

        # password
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'sina', 'first_name': 'sina', 'email': 'sina@admin.com',
                                     'password': 'passreza', 'bio': 'are'})
        self.assertEqual(response.status_code, 200)

        # bio
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'sohrab', 'first_name': 'sohrab', 'email': 'sohrab@admin.com',
                                     'password': 'passsohrab', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

    def test_bad_input_fields(self):
        # username
        try:
            self.client.post(reverse("api:v0:signup"),
                             {'username': 'mam mad', 'first_name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
        except ValidationError:
            pass

        # username
        try:
            self.client.post(reverse("api:v0:signup"),
                             {'username': 'mamad!!!!??', 'first_name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
        except ValidationError:
            pass

        # username
        try:
            self.client.post(reverse("api:v0:signup"),
                             {'username': 'mamad---+++', 'first_name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
        except ValidationError:
            pass

        # username
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'mamad...___', 'first_name': 'mamad', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 200)

        # first_name
        try:
            self.client.post(reverse("api:v0:signup"),
                             {'username': 'ali', 'first_name': 'ali121', 'email': 'ali@admin.com',
                              'password': 'passaliali', 'bio': 'ali'})
        except ValidationError:
            pass

        # first_name
        try:
            self.client.post(reverse("api:v0:signup"),
                             {'username': 'ali', 'first_name': 'ali???!!!', 'email': 'ali@admin.com',
                              'password': 'passaliali', 'bio': 'ali'})
        except ValidationError:
            pass

        # first_name
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'ali', 'first_name': 'ali reza', 'email': 'ali@admin.com',
                                     'password': 'passaliali', 'bio': 'ali'})
        self.assertEqual(response.status_code, 200)

        # email
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh @admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh@ admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh@admin. com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email -------> without .com
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh@admin',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email ------> without @
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email -------> without domain
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh@.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email -------> without name
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': '@admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

    def test_uniqe_signup(self):
        # user
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # profile
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'fatemeh', 'first_name': 'fatemeh', 'email': 'fatemeh@admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'sina', 'first_name': 'sina', 'email': 'sina@admin.com',
                                     'password': 'passsina', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 200)
