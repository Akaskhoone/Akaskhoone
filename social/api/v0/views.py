from django.core.exceptions import ObjectDoesNotExist

from social.api.v0.serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from social.forms import CreatePostFrom
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils.datastructures import MultiValueDictKeyError
from social.models import Post, Tag

User = get_user_model()


class Tags(APIView):
    """
    This view handles request related to tags.
    It returns all the previously stored tags if the query part is empty,
    or tags starting with the string specified in the name field at the query part.
    It returns error with message 'invalid' if the query part contains other fields.
    """

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


class PostWithID(APIView):
    """
    This class handles requests sent to /api/v0/social/posts/<int: post_id>.
    Get method returns a post in json form if a post with given post_id is available,
    and an error if there is no post with that post_is.
    Put method updates a post with given post_id if available, and an error if not.
    Delete method deletes a post with given post_id if available, and an error if not.
    """
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            return JsonResponse({
                "creator": post.user.username,
                "image": str(post.image),
                "des": post.des,
                "location": post.location,
                "date": str(post.date),
                "tags": [tag.name for tag in post.tags.all()]
            })
        except ObjectDoesNotExist as e:
            return JsonResponse({"post": ["NotExist"]}, status=400)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            post.des = request.data.get("des")
            post.location = request.data.get("location")
            post.tags = request.data.get("tags")
            post.save()
            post = Post.objects.get(pk=post_id)
            return JsonResponse({
                "creator": post.user.username,
                "image": str(post.image),
                "des": post.des,
                "location": post.location,
                "date": str(post.date),
                "tags": [tag.name for tag in post.tags.all()]
            })
        except ObjectDoesNotExist as e:
            return JsonResponse({"post": ["NotExist"]}, status=400)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            post.delete()
            return JsonResponse({"message": "Deleted!"})
        except ObjectDoesNotExist as e:
            return JsonResponse({"post": ["NotExist"]}, status=400)

    def post(self, request, *args, **kwargs):
        image_serializer = PostSerializer(data=request.data)
        if str(request.user.pk) != str(request.data["user"]):
            raise serializers.ValidationError("the author is not validated!")
        if image_serializer.is_valid():
            image_serializer.save()
            return JsonResponse({"status": "Successfully created!"})
        else:
            return JsonResponse({"status": "Post creation failed!"})


class Posts(APIView):
    def get(self, request, format=None):
        user = User.objects.get(id=request.query_params["user_id"])
        return JsonResponse({
            "posts": serializers.serialize("json", Post.objects.filter(user=user))
        })
