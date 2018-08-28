from django.urls import path
from social.api.v0.views import *

app_name = 'api.v0.social'

urlpatterns = [
    path('all_tags/', GetAllTags.as_view(), name="all_tags"),
    path('tags/', Tags.as_view(), name="tags"),
    path('create_post/', CreatePost.as_view(), name="create_post"),
    path('posts/', GetUserPosts.as_view(), name="posts"),
]
