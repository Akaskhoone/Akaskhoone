from accounts.api.utils import APIJWTTestCase
from accounts.api.v0.serializers import *
from django.urls import reverse
from django.core.exceptions import *
from accounts.api.utils import sending_mail
import requests

from django.test.client import encode_multipart

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
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'mammamad'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'rezareza'})
        self.assertEqual(response.status_code, 200)

    def test_valid_password(self):
        User.objects.create_user(username='reza', email='reza@admin.com', password='passreza')
        self.client.login(email='reza@admin.com', password='passreza')

        # common_pass
        self.client.put(reverse("api.v0.accounts:profile"), {'old_password': 'passreza', 'new_password': '12345678'})

        response = self.client.post(reverse("api.v0.accounts:login"),
                                    {'email': 'reza@admin.com', 'password': '12345678'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"),
                                    {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)

        # min_lenght
        self.client.put(reverse("api.v0.accounts:profile"), {'old_password': 'passreza', 'new_password': 'j43n54'})

        response = self.client.post(reverse("api.v0.accounts:login"), {'email': 'reza@admin.com', 'password': 'j43n54'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"),
                                    {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)

        # Numerical_pass
        self.client.put(reverse("api.v0.accounts:profile"), {'old_password': 'passreza', 'new_password': '1231423223453'})

        response = self.client.post(reverse("api.v0.accounts:login"),
                                    {'email': 'reza@admin.com', 'password': '1231423223453'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api.v0.accounts:login"),
                                    {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 200)


class APIFollowingTest(APIJWTTestCase):
    def test_follow(self):
        User.objects.create_user(email='reza@admin.com', username='reza', password='passreza')
        u = User.objects.get(username='reza')
        Profile.objects.create(user=u, name='reza', bio='reza bio')
        User.objects.create_user(email='sohrab@admin.com', username='sohrab', password='passsohrab')
        u2 = User.objects.get(username='sohrab')
        Profile.objects.create(user=u2, name='sohrab', bio='sohrab bio')
        self.client.login(email='reza@admin.com', password='passreza')

        # test follow
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'sohrab'})
        self.assertEqual(response.status_code, 200)
        try:
            sohrab_profile = u.profile.followings.get(user=u2)
            print("Followed successfully")
        except Exception as e:
            print("shit follow FAIL")
            print(e)

        # test follow a followed user
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'sohrab'})
        self.assertEqual(response.status_code, 200)
        try:
            sohrab_profile = u.profile.followings.get(user=u2)
            print("Followed successfully")
        except Exception as e:
            print("shit follow FAIL")
            print(e)

        # test follow itself
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'reza'})
        self.assertEqual(response.status_code, 400)

        # test follow a not registered user
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'mamadreza'})
        self.assertEqual(response.status_code, 400)

        # test unfollow
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'sohrab'})
        self.assertEqual(response.status_code, 200)
        try:
            sohrab = u.profile.followings.get(profile=u2.profile)
            print("UNFOLLOW EEEEERRRRRRRRRROOOOOOORRRRRR")
        except Exception as e:
            print("unfollowed successfully")

        # test unfollow a unfolowed user
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'sohrab'})
        self.assertEqual(response.status_code, 200)
        try:
            sohrab = u.profile.followings.get(profile=u2.profile)
            print("UNFOLLOW EEEEERRRRRRRRRROOOOOOORRRRRR")
        except Exception as e:
            print("unfollowed successfully")

        # test unfollow a not registered user
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'mamadreza'})
        self.assertEqual(response.status_code, 400)

        # test unfollow itself
        response = self.client.post(reverse("api.v0.accounts:followings"), {'follow': 'reza'})
        self.assertEqual(response.status_code, 400)

    def test_followers_list(self):
        u = User.objects.create_user(email='reza@admin.com', username='reza', password='passreza')
        Profile.objects.create(user=u, name='reza', bio='reza bio')
        u2 = User.objects.create_user(email='sohrab@admin.com', username='sohrab', password='passsohrab')
        Profile.objects.create(user=u2, name='sohrab', bio='sohrab bio')
        u3 = User.objects.create_user(email='eddi@admin.com', username='eddi', password='passeddi')
        Profile.objects.create(user=u3, name='eddi', bio='eddi bio')
        u4 = User.objects.create_user(email='fatemeh@admin.com', username='fatemeh', password='passfathemeh')
        Profile.objects.create(user=u4, name='fatemeh', bio='fatemeh bio')
        u5 = User.objects.create_user(email='aasmpro@admin.com', username='aasmpro', password='passaasmpro')
        Profile.objects.create(user=u5, name='aasmpro', bio='aasmpro bio')

        u.profile.followings.add(u4.profile)
        u4.profile.followings.add(u.profile)

        u3.profile.followings.add(u5.profile)
        u5.profile.followings.add(u3.profile)

        self.client.login(email='reza@admin.com', password='passreza')

        response = self.client.get(path='/api/v0/accounts/profile/followers/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'fatemeh': {'name': 'fatemeh', 'followed': True}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?username=reza')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'fatemeh': {'name': 'fatemeh', 'followed': True}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?email=reza@admin.com')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'fatemeh': {'name': 'fatemeh', 'followed': True}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?username=eddi')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'aasmpro': {'name': 'aasmpro', 'followed': False}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?email=eddi@admin.com')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'aasmpro': {'name': 'aasmpro', 'followed': False}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?email=mamad@shit.com')
        self.assertEqual(response.status_code, 400)
        response = self.client.get(path='/api/v0/accounts/profile/followers/?username=mamadreza')
        self.assertEqual(response.status_code, 400)

    def test_followings_list(self):
        u = User.objects.create_user(email='reza@admin.com', username='reza', password='passreza')
        Profile.objects.create(user=u, name='reza', bio='reza bio')
        u2 = User.objects.create_user(email='sohrab@admin.com', username='sohrab', password='passsohrab')
        Profile.objects.create(user=u2, name='sohrab', bio='sohrab bio')
        u3 = User.objects.create_user(email='eddi@admin.com', username='eddi', password='passeddi')
        Profile.objects.create(user=u3, name='eddi', bio='eddi bio')
        u4 = User.objects.create_user(email='fatemeh@admin.com', username='fatemeh', password='passfathemeh')
        Profile.objects.create(user=u4, name='fatemeh', bio='fatemeh bio')
        u5 = User.objects.create_user(email='aasmpro@admin.com', username='aasmpro', password='passaasmpro')
        Profile.objects.create(user=u5, name='aasmpro', bio='aasmpro bio')

        u.profile.followings.add(u4.profile)
        u4.profile.followings.add(u.profile)

        u3.profile.followings.add(u5.profile)
        u5.profile.followings.add(u3.profile)

        self.client.login(email='reza@admin.com', password='passreza')

        response = self.client.get(path='/api/v0/accounts/profile/followers/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'fatemeh': {'name': 'fatemeh', 'followed': True}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?username=reza')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'fatemeh': {'name': 'fatemeh', 'followed': True}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?email=reza@admin.com')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'fatemeh': {'name': 'fatemeh', 'followed': True}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?username=eddi')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'aasmpro': {'name': 'aasmpro', 'followed': False}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?email=eddi@admin.com')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'aasmpro': {'name': 'aasmpro', 'followed': False}})

        response = self.client.get(path='/api/v0/accounts/profile/followers/?email=mamad@shit.com')
        self.assertEqual(response.status_code, 400)
        response = self.client.get(path='/api/v0/accounts/profile/followers/?username=mamadreza')
        self.assertEqual(response.status_code, 400)


class APISignUpTest(APIJWTTestCase):
    def test_create_then_login(self):
        response = self.client.post(reverse("api.v0.accounts:signup"), {'email': 'reza@admin.com', 'username': 'arabporr',
                                                             'name': 'arabporr', 'password': 'passreza', 'bio': 'salam'})
        self.assertEqual(response.status_code, 200)
        response = self.client.login(email='reza@admin.com', password='passreza')
        self.assertEqual(response[1].status_code, 200)

    def test_requaired_fields(self):
        # username
        response = self.client.post(reverse("api.v0.accounts:signup"), {'username': '', 'name': 'reza', 'bio': 'salam',
                                                             'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 400)

        # firs_name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'mamad', 'name': '', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'khubi'})
        self.assertEqual(response.status_code, 400)

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
        response = self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'mam mad', 'name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # username
        response = self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'mamad!!!!??', 'name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # username
        response = self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'mamad---+++', 'name': 'mamad', 'email': 'mamad@admin.com',
                              'password': 'passmamad', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 400)

        # username
        response = self.client.post(reverse("api.v0.accounts:signup"),
                                    {'username': 'mamad...___', 'name': 'mamad', 'email': 'mamad@admin.com',
                                     'password': 'passmamad', 'bio': 'mamad'})
        self.assertEqual(response.status_code, 200)

        # name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'ali', 'name': 'ali121', 'email': 'ali@admin.com',
                              'password': 'passaliali', 'bio': 'ali'})
        self.assertEqual(response.status_code, 400)

        # name
        response = self.client.post(reverse("api.v0.accounts:signup"),
                             {'username': 'ali', 'name': 'ali???!!!', 'email': 'ali@admin.com',
                              'password': 'passaliali', 'bio': 'ali'})
        self.assertEqual(response.status_code, 400)

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
                                    data={'username': 'reza', 'name': 'reza', 'email': 'reza@admin.com',
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
#                              '{"id" :1, "bio": "salam man reza hastam :)",
#                                "image": null, "user": 1, "followers": [], "followings": []}')
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
#                              '{"id" :1, "bio": "salam man reza hastam 18 :)",
#                                "image": null, "user": 1, "followers": [], "followings": []}')
#         self.assertEqual(User.objects.get(id=1).name, 'reza')

