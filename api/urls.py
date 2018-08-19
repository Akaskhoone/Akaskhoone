from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from api import views

app_name = 'api'

urlpatterns = [
    path('api/v0/', include(([
        path('users/', views.Users.as_view(), name='users'),
        path('login/', obtain_jwt_token, name='login'),
        path('refresh/', refresh_jwt_token, name='refresh'),
        path('verify/', verify_jwt_token, name='verify'),
    ], 'v0'))),
]
