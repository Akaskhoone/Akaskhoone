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
