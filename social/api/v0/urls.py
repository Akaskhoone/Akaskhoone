from django.urls import path
from social.api.v0.views import *

app_name = 'api.v0.social'

urlpatterns = [
    path('tags/', Tags.as_view(), name="tags"),
    path('posts/', Posts.as_view(), name="posts"),
    path('home/', HomeAPIView.as_view(), name="home"),
    path('boards/', BoardsAPIView.as_view(), name="home"),
    path('posts/<int:post_id>', PostWithID.as_view(), name="posts_with_id"),
]
