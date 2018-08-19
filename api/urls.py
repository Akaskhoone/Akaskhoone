from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from api import views


urlpatterns = [
    path('api/v0/', include(([
        path('users/', views.Users.as_view()),
        path('login/', obtain_jwt_token),
        path('refresh/', refresh_jwt_token),
        path('verify/', verify_jwt_token),
    ], 'api'), namespace='api')),
]
