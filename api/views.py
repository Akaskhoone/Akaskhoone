from django.http import JsonResponse
from users.serializers import *
from rest_framework.views import APIView


class GetProfile(APIView):
    def get(self, request, format=None):
        p = Profile.objects.get(user=request.user)
        ps = ProfileSerializer(p)
        return JsonResponse(ps.data)
