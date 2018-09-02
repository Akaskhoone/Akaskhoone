from django.urls import path
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh, token_verify
from accounts.api.v0.views import *

app_name = 'api.v0.accounts'

urlpatterns = [
    path('login/', token_obtain_pair, name='login'),
    path('refresh/', token_refresh, name='refresh'),
    path('verify/', token_verify, name='verify'),
    path('signup/', Signup.as_view(), name='signup'),

    path('profile/', ProfileAPIView.as_view(), name='profile'),

    path('users/<int:user_id>/follow', FollowUser.as_view(), name="FollowUser"),
    path('users/<int:user_id>/unfollow', UnFollow.as_view(), name="UnFollowUser"),
]
