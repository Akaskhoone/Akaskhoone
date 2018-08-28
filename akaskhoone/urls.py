from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('social.urls')),
    # path('', include('posts.urls')),
    # path('', include('api.urls'))
]
