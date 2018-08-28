from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.settings import api_settings
import json
from django.core.exceptions import *
from posts.models import Tag, Post
from users.serializers import *


class APIJWTClient(APIClient):
    def login(self, **credentials):
        response = self.post(reverse("api:v0:login"), credentials, format='json')
        if response.status_code == status.HTTP_200_OK:
            self.credentials(
                HTTP_AUTHORIZATION="{0} {1}".format(api_settings.AUTH_HEADER_TYPES[0], response.data['access']))
            return True, response
        else:
            return False, response


class APIJWTTestCase(APITestCase):
    client_class = APIJWTClient


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
        self.assertJSONEqual(response.content, '{"id": 1, "bio": "testing profile", "image": null, "user": 1, "followers": [], "followings": []}')


class APITagTest(APIJWTTestCase):
    def setUp(self):
        User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        Tag.objects.create(name="bahar")
        Tag.objects.create(name="baharan")
        Tag.objects.create(name="tabestoon")
        Tag.objects.create(name="paeez")
        Tag.objects.create(name="parviz")
        Tag.objects.create(name="kaveh")
        Tag.objects.create(name="kavir")
        Tag.objects.create(name="kavian")

    def test_search_for_tags(self):
        print(">>> test search for tags ")
        response = self.client.get(reverse("api:v0:tags"), {"name": "b"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["matched_tags"], ['bahar', 'baharan'])
        response = self.client.get(reverse("api:v0:tags"), {"name": "kavi"})
        self.assertEqual(json.loads(response.content)["matched_tags"], ['kavir', 'kavian'])
        response = self.client.get(reverse("api:v0:tags"), {"name": "r"})
        self.assertEqual(json.loads(response.content)["matched_tags"], [])

    def test_all_tags(self):
        print(">>> test all tags ")
        response = self.client.get(reverse("api:v0:getAllTags"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["tags"],
                         ['bahar', 'baharan', "tabestoon", "paeez", "parviz", "kaveh", "kavir", "kavian"])


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
    def test_create_then_login(self):
        response = self.client.post(reverse("api:v0:signup"),
                                    {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)
        response = self.client.login(email='reza@admin.com', password='passreza')
        self.assertEqual(response[1].status_code, 200)

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


class APIGetUserPosts(APIJWTTestCase):
    def setUp(self):
        User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        Post.objects.create(image="user_photos/4/tanha.jpg", des="I'm Abolfazl", location="rahnema college",
                            user_id='1')
        Post.objects.create(image="user_photos/4/tanha.jpg", des="I'm Reza", location="rahnema college", user_id='4')

    def test_get_user_posts(self):
        print(">>> test user posts ")
        response = self.client.get(reverse("api:v0:getUserPosts"), {"user_id": "1"})
        print(json.loads(response.content))
        # for i in serializers.deserialize("json", response.content):
        #     print(i)
        self.assertEqual(response.status_code, 200)


class APIfollow(APIJWTTestCase):
    def setUp(self):
        abolfazl = User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        reza = User.objects.create_user('reza', 'reza@admin.com', 'passreza')
        fatemeh = User.objects.create_user('fatemeh', 'fatemeh@admin.com', 'passfatemeh')
        sohrab = User.objects.create_user('sohrab', 'sohrab@admin.com', 'passsohrab')
        edi = User.objects.create_user('edi', 'edi@admin.com', 'passedi')
        abolfazl_profile = Profile.objects.create(user=abolfazl)
        reza_profile = Profile.objects.create(user=reza)
        Profile.objects.create(user=fatemeh)
        Profile.objects.create(user=sohrab)
        abolfazl_profile.followings.add(reza_profile)

    def test_follow_someone(self):
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "1"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "you can not follow yourself!"})

        response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "5"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "user with user_id: 5 does not have profile!"})

        response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "2"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "you have already followed user with user_id: 2"})

        response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "3"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "Successful!"})

        self.client.login(email='edi@admin.com', password='passedi')
        response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "1"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "you don't have profile, sorry!"})

    def test_unfollow(self):
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "1"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "you don't follow user with user_id: 1"})

        response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "3"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "you don't follow user with user_id: 3"})

        response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "5"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "user with user_id: 5 does not have profile!"})

        response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "2"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"status": "Successful!"})

        self.client.login(email='edi@admin.com', password='passedi')
        response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "1"}))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content), {"error": "you don't have profile, sorry!"})


class APIEditProfileTest(APIJWTTestCase):
    def test_changing_bio(self):
        # first name is blank at all the tests below
        # signup and login
        self.client.post(reverse("api:v0:signup"),  {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza', 'bio': ''})
        self.client.login(email='reza@admin.com', password='passreza')

        # just setting the bio
        response = self.client.post(reverse("api:v0:edit_profile"), {'first_name': '', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "salam", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, '')

        # different kind of characters
        response = self.client.post(reverse("api:v0:edit_profile"), {'first_name': '', 'bio': 'aksdjan 923u48324u ???!!! --- +++ :: () {} []'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "aksdjan 923u48324u ???!!! --- +++ :: () {} []", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, '')

    def test_changing_first_name(self):
        # bio is blank at all the tests below

        # signup and login
        self.client.post(reverse("api:v0:signup"), {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza', 'bio': ''})
        self.client.login(email='reza@admin.com', password='passreza')

        # just setting the first name
        response = self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'mamadreza', 'bio': ''})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'mamadreza')

        # testing first names with spaces
        response = self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'mamad reza', 'bio': ''})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'mamad reza')

        # testing invalid first names with numbers
        try:
            self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'reza1234', 'bio': ''})
        except ValidationError:
            pass
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'mamad reza')

        # testing invalid first names with symbols
        try:
            self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'reza?!', 'bio': ''})
        except ValidationError:
            pass
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'mamad reza')

        # testing invalid first names with underline and dot
        try:
            self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'reza_reza.a', 'bio': ''})
        except ValidationError:
            pass
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'mamad reza')


    def test_changing_both(self):
        self.client.post(reverse("api:v0:signup"), {'username': 'reza', 'first_name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza', 'bio': ''})
        self.client.login(email='reza@admin.com', password='passreza')

        # blank both
        response = self.client.post(reverse("api:v0:edit_profile"), {'first_name': '', 'bio': ''})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, '')

        # both good
        response = self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'reza', 'bio': 'salam man reza hastam 18 :)'})
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "salam man reza hastam 18 :)", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'reza')

        # setting first name badly and bio good
        try:
            self.client.post(reverse("api:v0:edit_profile"), {'first_name': 'mamad reza 2000', 'bio': 'salam mamad reza'})
        except ValidationError:
            pass
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"id" :1, "bio": "salam man reza hastam 18 :)", "image": null, "user": 1, "followers": [], "followings": []}')
        self.assertEqual(User.objects.get(id=1).first_name, 'reza')
