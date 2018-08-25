from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from api import views

app_name = 'api'

urlpatterns = [
    path('api/v0/', include(([
        path('profile/', views.GetProfile.as_view(), name='profile'),
        path('change_pass/', views.UpdatePassword.as_view(), name='change_password'),
        path('login/', obtain_jwt_token, name='login'),
        path('signup/', views.Signup.as_view(), name='signup'),
        path('refresh/', refresh_jwt_token, name='refresh'),
        path('verify/', verify_jwt_token, name='verify'),
        path('edit_profile/', views.EditProfile.as_view(), name="edit_profile"),
        path('allTags/', views.GetAllTags.as_view(), name="getAllTags"),
        path('tags/', views.Tags.as_view(), name="tags"),
        path('createPost/', views.CreatePost.as_view(), name="createPost"),
        path('posts/', views.GetUserPosts.as_view(), name="getUserPosts"),
    ], 'v0'))),
]
