from django.urls import path
from accounts.api.v0.views import *

app_name = 'api.v0.accounts'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('verify/', TokenVerifyView.as_view(), name='verify'),
    path('signup/', Signup.as_view(), name='signup'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('profile/followers/', FollowersAPIView.as_view(), name='followers'),
    path('profile/followings/', FollowingsAPIView.as_view(), name='followings'),
]
