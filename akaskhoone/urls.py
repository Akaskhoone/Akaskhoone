from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .notifications import PrivateAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('private/', PrivateAPIView.as_view(), name="private"),
    path('', include('accounts.urls')),
    path('', include('social.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
