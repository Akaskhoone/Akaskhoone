from django.urls import path
from social.api.v0.views import *

app_name = 'api.v0.social'

urlpatterns = [
    path('tags/', TagsAPIView.as_view(), name="tags"),
    path('home/', HomeAPIView.as_view(), name="home"),
    path('boards/', BoardsAPIView.as_view(), name="boards"),
    path('boards/<int:board_id>/', BoardDetailAPIView.as_view(), name="board_detail"),
    path('posts/', PostsAPIView.as_view(), name="posts"),
    path('posts/<int:post_id>/', PostDetailAPIView.as_view(), name="post_detail"),
    path('posts/<int:post_id>/likes/', PostLikesAPIView.as_view(), name="post_likes"),
    path('posts/<int:post_id>/comments/', PostCommentsAPIView.as_view(), name="post_comments"),
]
