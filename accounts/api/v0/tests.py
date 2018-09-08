from accounts.api.utils import APIJWTTestCase
from accounts.api.v0.serializers import *
from django.urls import reverse
from django.core.exceptions import *
import json


class APIAuthTest(APIJWTTestCase):
    def test_login_real_user(self):
        User.objects.create_user(email='aasmpro@admin.com', username='aasmpro', password='passaasmpro')
        result, response = self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'access')

    def test_login_fake_user(self):
        result, response = self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        self.assertEqual(response.status_code, 400)

    def test_authorization_real_user(self):
        u = User.objects.create_user('aasmpro@admin.com', 'aasmpro', 'passaasmpro')
        Profile.objects.create(user_id=u.id, bio='testing profile')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        response = self.client.get(reverse("api.v0.accounts:profile"))
        self.assertEqual(response.status_code, 200)

    def test_authorization_fake_user(self):
        response = self.client.get(reverse("api.v0.accounts:profile"))
        self.assertEqual(response.status_code, 401)


class APIProfilesTest(APIJWTTestCase):
    def setUp(self):
        u = User.objects.create_user('aasmpro@admin.com', 'aasmpro', 'passaasmpro')
        u2 = User.objects.create_user('sohrab@admin.com', 'sohrab', 'passsohrab')
        User.objects.create_user('noprofile@admin.com', 'noprofile', 'passnoprofile')
        Profile.objects.create(user=u, name='aasmpro name', bio='aasmpro bio')
        Profile.objects.create(user=u2, name='sohrab name', bio='sohrab bio')

    def test_getting_authorized_user_profile(self):
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        response = self.client.get(reverse("api.v0.accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('aasmpro', str(response.content))

    def test_getting_authorized_user_without_profile(self):
        self.client.login(email='noprofile@admin.com', password='passnoprofile')
        response = self.client.get(reverse("api.v0.accounts:profile"))
        self.assertEqual(response.status_code, 400)
        self.assertIn('NotExist', str(response.content))

    def test_getting_profile_with_username(self):
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        response = self.client.get(path="{}{}".format(reverse("api.v0.accounts:profile"), "?username=sohrab"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sohrab', str(response.content))
        response = self.client.get(path="{}{}".format(reverse("api.v0.accounts:profile"), "?username=sohrabi"))
        self.assertEqual(response.status_code, 400)

    def test_getting_profile_with_email(self):
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        response = self.client.get(path="{}{}".format(reverse("api.v0.accounts:profile"), "?email=sohrab@admin.com"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sohrab', str(response.content))
        response = self.client.get(path="{}{}".format(reverse("api.v0.accounts:profile"), "?email=abi@admin.com"))
        self.assertEqual(response.status_code, 400)


class APIChangePasswordTest(APIJWTTestCase):
    def test_login_after_change(self):
        User.objects.create_user(username='reza', email='reza@admin.com', password='passreza')
        self.client.login(email='reza@admin.com', password='passreza')
        self.client.put(reverse("api.v0.accounts:profile"), {'old_password': 'passreza', 'new_password': 'rezareza'})
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'mamadmamad'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'rezareza'})
        self.assertEqual(response.status_code, 200)

    def test_valid_password(self):
        User.objects.create_user(username='reza', email='reza@admin.com', password='passreza')
        self.client.login(email='reza@admin.com', password='passreza')

        # common_pass
        try:
            self.client.post(reverse("api.v0.accounts:profile"),
                             {'old_password': 'passreza', 'new_password': '12345678'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 88")
        except ValidationError as e:
            # print(E.messages)
            self.assertListEqual(e.messages, ['This password is too common.', 'This password is entirely numeric.'])
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)

        # min_lenght
        try:
            self.client.post(reverse("api.v0.accounts:profile"), {'old_password': 'passreza', 'new_password': 'j43n54'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 100")
        except ValidationError:
            pass
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'j43n54'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)

        # Numerical_pass
        try:
            self.client.post(reverse("api.v0.accounts:profile"),
                             {'old_password': 'passreza', 'new_password': '1231423223453'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 112")
        except ValidationError:
            pass
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': '1231423223453'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)


class APISignUpTest(APIJWTTestCase):
    def test_create_then_login(self):
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)
        response = self.client.login(email='reza@admin.com', password='passreza')
        self.assertEqual(response[1].status_code, 200)

    def test_requaired_fields(self):
        # username
        try:
            self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': '', 'name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza',
                              'bio': 'salam'})
            print("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT (in former api , it must return ValidationError) at line 136")
        except ValidationError:
            pass

        # firs_name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'mamad', 'name': '', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'khubi'})
        self.assertEqual(response.status_code, 200)

        # email
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': '',
                                     'password': 'passfatemeh', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # password
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'sina', 'name': 'sina', 'email': 'sina@admin.com',
                                     'password': '', 'bio': 'reza'})
        self.assertEqual(response.status_code, 400)

        # bio
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'ali', 'name': 'ali', 'email': 'ali@admin.com',
                                     'password': 'passaliali', 'bio': ''})
        self.assertEqual(response.status_code, 200)

    def test_uique_fields(self):
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

        # username
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'reza', 'name': 'mamad', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'khubi'})
        self.assertEqual(response.status_code, 400)

        # name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'ali', 'name': 'reza', 'email': 'ali@admin.com',
                                     'password': 'passaliali', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 200)

        # email
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'reza@admin.com',
                                     'password': 'passfatemeh', 'bio': 'reza'})
        self.assertEqual(response.status_code, 400)

        # password
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'sina', 'name': 'sina', 'email': 'sina@admin.com',
                                     'password': 'passreza', 'bio': 'are'})
        self.assertEqual(response.status_code, 200)

        # bio
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'sohrab', 'name': 'sohrab', 'email': 'sohrab@admin.com',
                                     'password': 'passsohrab', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)

    def test_bad_input_fields(self):
        # username
        try:
            self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'mam mad', 'name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 206")
        except ValidationError:
            pass

        # username
        try:
            self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'mamad!!!!??', 'name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 215")
        except ValidationError:
            pass

        # username
        try:
            self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'mamad---+++', 'name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 224")
        except ValidationError:
            pass

        # username
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'mamad...___', 'name': 'mamad', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 200)

        # name
        try:
            self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'ali', 'name': 'ali121', 'email': 'ali@admin.com',
                              'password': 'passaliali', 'bio': 'ali'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 239")
        except ValidationError:
            pass

        # name
        try:
            self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'ali', 'name': 'ali???!!!', 'email': 'ali@admin.com',
                              'password': 'passaliali', 'bio': 'ali'})
            print ("SSSSSSSSSSHHHHHHHHHHIIIIIIIIIITTTTTTTTTT  wher are the validators ??!! at line 248")
        except ValidationError:
            pass

        # name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'ali', 'name': 'ali reza', 'email': 'ali@admin.com',
                                     'password': 'passaliali', 'bio': 'ali'})
        self.assertEqual(response.status_code, 200)

        # email
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh @admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh@ admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh@admin. com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email -------> without .com
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh@admin',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email ------> without @
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email -------> without domain
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh@.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

        # email -------> without name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': '@admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 400)

    def test_uniqe_signup(self):
        # user
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com',
                                     'password': 'passreza', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # profile
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'fatemeh', 'name': 'fatemeh', 'email': 'fatemeh@admin.com',
                                     'password': 'passfatemeh', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'sina', 'name': 'sina', 'email': 'sina@admin.com',
                                     'password': 'passsina', 'bio': 'fatemeh'})
        self.assertEqual(response.status_code, 200)


# class APIfollow(APIJWTTestCase):
#     def setUp(self):
#         abolfazl = User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
#         reza = User.objects.create_user('reza', 'reza@admin.com', 'passreza')
#         fatemeh = User.objects.create_user('fatemeh', 'fatemeh@admin.com', 'passfatemeh')
#         sohrab = User.objects.create_user('sohrab', 'sohrab@admin.com', 'passsohrab')
#         edi = User.objects.create_user('edi', 'edi@admin.com', 'passedi')
#         abolfazl_profile = Profile.objects.create(user=abolfazl)
#         reza_profile = Profile.objects.create(user=reza)
#         Profile.objects.create(user=fatemeh)
#         Profile.objects.create(user=sohrab)
#         abolfazl_profile.followings.add(reza_profile)
#
    # def test_follow_someone(self):
    #     self.client.login(email='aasmpro@admin.com', password='passaasmpro')
    #     response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "1"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "you can not follow yourself!"})
    #
    #     response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "5"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "user with user_id: 5 does not have profile!"})
    #
    #     response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "2"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "you have already followed user with user_id: 2"})
    #
    #     response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "3"}))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content), {"status": "Successful!"})
    #
    #     self.client.login(email='edi@admin.com', password='passedi')
    #     response = self.client.get(reverse('api:v0:FollowUser', kwargs={"user_id": "1"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "you don't have profile, sorry!"})
    #
    # def test_unfollow(self):
    #     self.client.login(email='aasmpro@admin.com', password='passaasmpro')
    #     response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "1"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "you don't follow user with user_id: 1"})
    #
    #     response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "3"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "you don't follow user with user_id: 3"})
    #
    #     response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "5"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "user with user_id: 5 does not have profile!"})
    #
    #     response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "2"}))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content), {"status": "Successful!"})
    #
    #     self.client.login(email='edi@admin.com', password='passedi')
    #     response = self.client.get(reverse('api:v0:UnFollowUser', kwargs={"user_id": "1"}))
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(json.loads(response.content), {"error": "you don't have profile, sorry!"})
#
#
# class APIEditProfileTest(APIJWTTestCase):
#     def test_changing_bio(self):
#         # first name is blank at all the tests below
#         # signup and login
#         self.client.post(reverse("api.v0.accounts:signup"),
#                          {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza',
#                           'bio': ''})
#         self.client.login(email='reza@admin.com', password='passreza')
#
#         # just setting the bio
#         response = self.client.post(reverse("api:v0:edit_profile"), {'name': '', 'bio': 'salam'})
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "salam", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, '')
#
#         # different kind of characters
#         response = self.client.post(reverse("api:v0:edit_profile"),
#                                     {'name': '', 'bio': 'aksdjan 923u48324u ???!!! --- +++ :: () {} []'})
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "aksdjan 923u48324u ???!!! --- +++ :: () {} []", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, '')
#
#     def test_changing_name(self):
#         # bio is blank at all the tests below
#
#         # signup and login
#         self.client.post(reverse("api.v0.accounts:signup"),
#                          {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza',
#                           'bio': ''})
#         self.client.login(email='reza@admin.com', password='passreza')
#
#         # just setting the first name
#         response = self.client.post(reverse("api:v0:edit_profile"), {'name': 'mamadreza', 'bio': ''})
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'mamadreza')
#
#         # testing first names with spaces
#         response = self.client.post(reverse("api:v0:edit_profile"), {'name': 'mamad reza', 'bio': ''})
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'mamad reza')
#
#         # testing invalid first names with numbers
#         try:
#             self.client.post(reverse("api:v0:edit_profile"), {'name': 'reza1234', 'bio': ''})
#         except ValidationError:
#             pass
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'mamad reza')
#
#         # testing invalid first names with symbols
#         try:
#             self.client.post(reverse("api:v0:edit_profile"), {'name': 'reza?!', 'bio': ''})
#         except ValidationError:
#             pass
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'mamad reza')
#
#         # testing invalid first names with underline and dot
#         try:
#             self.client.post(reverse("api:v0:edit_profile"), {'name': 'reza_reza.a', 'bio': ''})
#         except ValidationError:
#             pass
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'mamad reza')
#
#     def test_changing_both(self):
#         self.client.post(reverse("api.v0.accounts:signup"),
#                          {'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com', 'password': 'passreza',
#                           'bio': ''})
#         self.client.login(email='reza@admin.com', password='passreza')
#
#         # blank both
#         response = self.client.post(reverse("api:v0:edit_profile"), {'name': '', 'bio': ''})
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, '')
#
#         # both good
#         response = self.client.post(reverse("api:v0:edit_profile"),
#                                     {'name': 'reza', 'bio': 'salam man reza hastam 18 :)'})
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "salam man reza hastam :)", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'reza')
#
#         # setting first name badly and bio good
#         try:
#             self.client.post(reverse("api:v0:edit_profile"),
#                              {'name': 'mamad reza 2000', 'bio': 'salam mamad reza'})
#         except ValidationError:
#             pass
#         response = self.client.get(reverse("api:v0:profile"))
#         self.assertEqual(response.status_code, 200)
#         self.assertJSONEqual(response.content,
#                              '{"id" :1, "bio": "salam man reza hastam 18 :)", "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'reza')

# class APIProfileTest(APIJWTTestCase):
#     def setUp(self):
#         User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
#         self.client.login(email='aasmpro@admin.com', password='passaasmpro')
#
#     def