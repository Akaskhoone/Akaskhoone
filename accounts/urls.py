from django.urls import path, include

urlpatterns = [
    path('api/v0/accounts/', include('accounts.api.v0.urls'), name='api.v0.accounts')
]
