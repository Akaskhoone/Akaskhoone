from accounts.api.utils import APIJWTTestCase
from social.models import Tag, Post
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

User = get_user_model()


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
        response = self.client.get(reverse("api:v0:tags"), {"name": "b"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["matched_tags"], ['bahar', 'baharan'])
        response = self.client.get(reverse("api:v0:tags"), {"name": "kavi"})
        self.assertEqual(json.loads(response.content)["matched_tags"], ['kavir', 'kavian'])
        response = self.client.get(reverse("api:v0:tags"), {"name": "r"})
        self.assertEqual(json.loads(response.content)["matched_tags"], [])

    def test_all_tags(self):
        response = self.client.get(reverse("api:v0:getAllTags"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["tags"],
                         ['bahar', 'baharan', "tabestoon", "paeez", "parviz", "kaveh", "kavir", "kavian"])