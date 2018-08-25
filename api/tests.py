from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_jwt.settings import api_settings
import json

from posts.models import Tag
from users.serializers import *


class APIJWTClient(APIClient):
    def login(self, **credentials):
        response = self.post(reverse("api:v0:login"), credentials, format='json')
        if response.status_code == status.HTTP_200_OK:
            self.credentials(
                HTTP_AUTHORIZATION="{0} {1}".format(api_settings.JWT_AUTH_HEADER_PREFIX, response.data['token']))
            return True, response
        else:
            return False, response


class APIJWTTestCase(APITestCase):
    client_class = APIJWTClient


class APILoginTest(APIJWTTestCase):
    def test_login_with_real_user(self):
        print('>>> test login with real user')
        User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        response = self.client.post(reverse("api:v0:login"), {'email': 'aasmpro@admin.com', 'password': 'passaasmpro'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'token')

    def test_login_with_fake_user(self):
        print('>>> test login with fake user')
        response = self.client.post(reverse("api:v0:login"), {'email': 'aasmpro@admin.com', 'password': 'passaasmpro'})
        self.assertEqual(response.status_code, 400)


class APIAuthorizationTest(APIJWTTestCase):
    def test_api_authorization_needed_endpoint(self):
        print('>>> test api authorization needed endpoint')
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 401)
        u = User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        Profile.objects.create(user_id=u.id, bio='testing profile')
        # response = self.client.post(reverse("api:v0:login"), {'email': 'aasmpro@admin.com', 'password': 'passaasmpro'})
        # authorization = F"{api_settings.JWT_AUTH_HEADER_PREFIX} {response.data['token']}"
        # self.client.credentials(HTTP_AUTHORIZATION=authorization)
        response = self.client.get(reverse("api:v0:profile"))
        self.assertEqual(response.status_code, 200)


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
    def test_change_password(self):
        User.objects.create_user('reza', 'reza@admin.com', 'passreza')
        self.client.login(email='reza@admin.com', password='passreza')
        self.client.post(reverse("api:v0:change_password"), {'old_password': 'passreza', 'new_password': 'rezareza'})
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'passreza'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'mamadmamad'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse("api:v0:login"), {'email': 'reza@admin.com', 'password': 'rezareza'})
        self.assertEqual(response.status_code, 200)
