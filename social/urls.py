from django.urls import path, include

urlpatterns = [
    path('api/v0/social/', include('social.api.v0.urls'), name='api.v0.social')
]
