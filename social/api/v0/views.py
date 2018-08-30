from social.api.v0.serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from social.forms import CreatePostFrom
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils.datastructures import MultiValueDictKeyError

User = get_user_model()


class GetAllTags(APIView):
    def get(self, request):
        return JsonResponse({
            "tags": [str(t) for t in Tag.objects.all()]
        })


class Tags(APIView):

    def get(self, request, formant=None):
        try:
            query = request.query_params['name']
            matched_tags = [str(t) for t in Tag.objects.filter(name__startswith=query)]

        except MultiValueDictKeyError:
            if request.query_params == {}:
                matched_tags = [str(t) for t in Tag.objects.all()]
            else:
                return JsonResponse({"error": "invalid"}, status=400)

        return JsonResponse({
            "matched_tags": matched_tags
        })


class PostView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        image_serializer = PostSerializer(data=request.data)
        if str(request.user.pk) != str(request.data["user"]):
            raise serializers.ValidationError("the author is not validated!")
        if image_serializer.is_valid():
            image_serializer.save()
            return JsonResponse({"status": "Successfully created!"})
        else:
            return JsonResponse({"status": "Post creation failed!"})


class GetUserPosts(APIView):
    def get(self, request, format=None):
        user = User.objects.get(id=request.query_params["user_id"])
        return JsonResponse({
            "posts": serializers.serialize("json", Post.objects.filter(user=user))
        })
