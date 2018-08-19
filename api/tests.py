from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_jwt.settings import api_settings

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
        response = self.client.get(reverse("api:v0:users"))
        self.assertEqual(response.status_code, 401)
        User.objects.create_user('aasmpro', 'aasmpro@admin.com', 'passaasmpro')
        self.client.login(email='aasmpro@admin.com', password='passaasmpro')
        # response = self.client.post(reverse("api:v0:login"), {'email': 'aasmpro@admin.com', 'password': 'passaasmpro'})
        # authorization = F"{api_settings.JWT_AUTH_HEADER_PREFIX} {response.data['token']}"
        # self.client.credentials(HTTP_AUTHORIZATION=authorization)
        response = self.client.get(reverse("api:v0:users"))
        self.assertEqual(response.status_code, 200)
