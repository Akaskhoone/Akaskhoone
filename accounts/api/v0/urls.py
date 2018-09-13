from django.urls import path
from accounts.api.v0.views import *

app_name = 'api.v0.accounts'

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('refresh/', RefreshTokenAPIView.as_view(), name='refresh'),
    path('verify/', VerifyTokenAPIView.as_view(), name='verify'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('profile/followers/', FollowersAPIView.as_view(), name='followers'),
    path('profile/followings/', FollowingsAPIView.as_view(), name='followings'),
    path('profile/invitation/', InvitationAPIView.as_view(), name='invitation'),
    path('reset_password/', ResetPasswordAPIView.as_view(), name='reset_password')
]
