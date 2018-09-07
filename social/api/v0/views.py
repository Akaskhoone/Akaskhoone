import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from social.api.v0.serializers import *
from rest_framework.views import APIView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from social.forms import CreatePostFrom
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils.datastructures import MultiValueDictKeyError
from social.models import Post, Tag
from social.forms import *
from accounts.api.utils import get_user

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


class HomeAPIView(APIView):
    def get(self, request):
        limit = request.query_params.get('limit') or 2
        page = request.query_params.get('page') or 1
        page = int(page)
        posts_list = []
        followings = request.user.profile.followings.all().values('user')
        posts = Post.objects.filter(user__in=followings).order_by('date').reverse()
        posts_paginated = Paginator(posts, limit)
        for post in posts_paginated.object_list:
            posts_list.append({
                "post_id": post.id,
                "creator": post.user.username,
                "image": str(post.image),
                "des": post.des,
                "location": post.location,
                "date": str(post.date),
                "tags": [tag.name for tag in post.tags.all()]
            })
        posts_paginated.object_list = posts_list
        next_page = (page + 1) if (page + 1) <= posts_paginated.num_pages else None
        try:
            posts_list = list(posts_paginated.page(page))
        except EmptyPage or InvalidPage:
            posts_list = None
        data = {
            "posts": posts_list,
            "next": F"/social/home/?page={next_page}" if next_page else None
        }
        return JsonResponse(data, status=200, safe=False)


class BoardsAPIView(APIView):
    def get(self, request):
        user = get_user(request)
        if user:
            boards = user.boards.objects.all()
            boards_list = []
            for board in boards:
                posts = []
                for post in board.posts.all():
                    posts.append({
                        "post_id": post.id,
                        "image": post.image
                    })
                boards_list.append({
                    "name": board.name,
                    "count": board.posts.count(),
                    "posts": posts
                })
            data = {
                "count": len(boards),
                "boards": boards_list
            }
            return JsonResponse(data, status=200, safe=False)
        else:
            return JsonResponse({"error": {"Profile": ["NotExist"]}}, status=400)

    def post(self, request):
        return JsonResponse({"method": "post"}, status=200, safe=False)

    def put(self, request):
        return JsonResponse({"method": "put"}, status=200, safe=False)

    def delete(self, request):
        return JsonResponse({"method": "delete"}, status=200, safe=False)


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
                "post_id": post.id,
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
                "post_id": post.id,
                "creator": post.user.username,
                "image": str(post.image),
                "des": post.des,
                "location": post.location,
                "date": str(post.date),
                "tags": [tag.name for tag in post.tags.all()]
            })
        except ObjectDoesNotExist:
            return JsonResponse({"post": ["NotExist"]}, status=400)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            post.delete()
            return JsonResponse({"message": "Deleted!"})
        except ObjectDoesNotExist as e:
            return JsonResponse({"post": ["NotExist"]}, status=400)


class Posts(APIView):
    """
    This class handles requests sent to /api/v0/social/posts.
    In post method it handles creation of a new post and in
    get method it returns posts associated with the query part.
    """

    def get_posts(self, *args, **kwargs):
        if args:
            posts = Post.objects.filter(user=args[0])
        elif kwargs.get("tag"):
            posts = Post.objects.filter(tags=kwargs.get("tag"))
        elif kwargs.get("username"):
            posts = User.objects.get(username=kwargs.get("username")).post_set.all()
        elif kwargs.get("email"):
            posts = User.objects.get(email=kwargs.get("email")).post_set.all()
        else:
            posts = []
        posts_list = []
        for post in posts:
            posts_list.append({
                "post_id": post.id,
                "creator": post.user.username,
                "image": str(post.image),
                "des": post.des,
                "location": post.location,
                "date": str(post.date),
                "tags": [tag.name for tag in post.tags.all()]
            })
        return posts_list

    def get(self, request, format=None):
        tag = request.query_params.get("tag")
        username = request.query_params.get("username")
        email = request.query_params.get("email")
        if request.query_params == {}:
            posts_list = self.get_posts(request.user)
        elif tag:
            posts_list = self.get_posts(tag=tag)
        elif username:
            posts_list = self.get_posts(username=username)
        elif email:
            posts_list = self.get_posts(email=email)
        else:
            return JsonResponse({"error": "Invalid"}, status=400)
        return JsonResponse({"posts": posts_list})

    def post(self, request):
        new_post = CreatePostFrom(request.POST, request.FILES)
        if new_post.is_valid():
            new_post.save(request.user)
            return JsonResponse({"message": "post created successfully"})
        else:
            errors = {}
            errors_as_json = json.loads(new_post.errors.as_json())
            image_error = errors_as_json.get("image")
            if image_error.get("image") == "required":
                errors["image"] = ["Required"]
            return JsonResponse({"error": errors}, status=400)

# todo pagination is not implemented, but needed!
