from social.api.v0.serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from social.forms import CreatePostFrom

User = get_user_model()


class GetAllTags(APIView):
    def get(self, request):
        return JsonResponse({
            "tags": [str(t) for t in Tag.objects.all()]
        })


class Tags(APIView):

    def get(self, request, formant=None):
        query = request.query_params['name']
        matched_tags = [str(t) for t in Tag.objects.filter(name__startswith=query)]
        return JsonResponse({
            "matched_tags": matched_tags
        })


def handle_uploaded_file(f, filename):
    with open('posts/images/{}'.format(filename), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


class CreatePost(APIView):
    def post(self, request):
        form = CreatePostFrom(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            handle_uploaded_file(request.FILES['file'], request.user.post_set.count())
            return JsonResponse({"status": "Successful!"})
        else:
            return JsonResponse({"status": "Failed!"})


class GetUserPosts(APIView):
    def get(self, request, format=None):
        user = User.objects.get(id=request.query_params["user_id"])
        return JsonResponse({
            "posts": [post for post in Post.objects.filter(user=user)]
        })
