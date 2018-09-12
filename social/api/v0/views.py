import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.parsers import FormParser, MultiPartParser
from django.utils.datastructures import MultiValueDictKeyError
from social.forms import CreatePostFrom
from accounts.api.utils import get_user
from django.contrib.auth import get_user_model
from social.models import Post, Tag, Board
from akaskhoone.exceptions import error_data, success_data
from social.api.v0.serializers import PostSerializer, CommentSerializer, TagSerializer, BoardSerializer
from akaskhoone.utils import get_paginated_data
from accounts.api.v0.serializers import ProfileSerializer

User = get_user_model()


class Tags(APIView):
    """
    This view handles request related to tags.
    It returns all the previously stored tags if the query part is empty,
    or tags starting with the string specified in the name field at the query part.
    It returns error with message 'invalid' if the query part contains other fields.
    """

    def get(self, request):
        search = request.query_params.get('search')
        if search:
            data = get_paginated_data(
                data=TagSerializer(Tag.objects.filter(name__contains=search), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/tags/?search={search}"
            )
        else:
            data = get_paginated_data(
                data=TagSerializer(Tag.objects.all(), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/tags/?"
            )
        return JsonResponse(data)


class HomeAPIView(APIView):
    def get(self, request):
        followings = list(request.user.profile.followings.all().values_list('user', flat=True))
        followings.append(request.user.pk)
        posts = Post.objects.filter(user_id__in=followings).order_by('-date')
        data = get_paginated_data(
            data=PostSerializer(posts, many=True).data,
            page=request.query_params.get('page'),
            limit=request.query_params.get('limit'),
            url="/social/home/?"
        )
        return JsonResponse(data)


class BoardsAPIView(APIView):
    def get(self, request):
        user = get_user(request)
        if user:
            data = get_paginated_data(
                data=BoardSerializer(user.boards.all(), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/boards/?username={user.username}"
            )
            return JsonResponse(data)
        else:
            print("status: 400", error_data(profile="NotExist"))
            return JsonResponse(error_data(profile="NotExist"), status=400)

    def post(self, request):
        name = request.data.get('name')
        posts = request.data.get('posts')
        if name and posts:
            try:
                board = Board.objects.create(user=request.user, name=name)
                for post in posts:
                    try:
                        board.posts.add(post)
                    except Exception as e:
                        pass
                if board.posts.count() == 0:
                    board.delete()
                    print("status: 400", error_data(posts="NotValid"))
                    return JsonResponse(error_data(posts="NotValid"), status=400)
                posts = []
                for post in board.posts.all():
                    posts.append({
                        "post_id": post.id,
                        "image": str(post.image)
                    })
                data = {
                    "board_id": board.id,
                    "name": board.name,
                    "count": board.posts.count(),
                    "posts": posts
                }
                print("status: 200", data)
                return JsonResponse(data, status=200)
            except Exception as e:
                print("status: 400", error_data(request="InternalError"))
                return JsonResponse(error_data(request="InternalError"), status=400)
        else:
            errors = error_data()
            if not name:
                errors = error_data(name="Required")
            if not posts:
                errors = error_data(posts="Required")
            print("status: 400", errors)
            return JsonResponse(errors, status=400)


class BoardDetailAPIView(APIView):
    def get(self, request, board_id):
        try:
            data = BoardSerializer(Board.objects.get(pk=board_id)).data
            print("status: 200", data)
            return JsonResponse(data, status=200)

        except Exception as e:
            print("status: 400", error_data(board="NotExist"))
            return JsonResponse(error_data(board="NotExist"), status=400)

    def put(self, request, board_id):
        try:
            board = Board.objects.get(pk=board_id)
            name = request.data.get('name')
            add_posts = request.data.get('add_posts')
            remove_posts = request.data.get('remove_posts')
            if name:
                board.name = name
            if add_posts:
                for post in add_posts:
                    try:
                        board.posts.add(post)
                    except Exception as e:
                        pass
            if remove_posts:
                for post in remove_posts:
                    try:
                        board.posts.remove(post)
                    except Exception as e:
                        pass
            board.save()
            posts = []
            for post in board.posts.all():
                posts.append({
                    "post_id": post.id,
                    "image": str(post.image)
                })
            data = {
                "board_id": board.id,
                "name": board.name,
                "count": board.posts.count(),
                "posts": posts
            }
            print("status: 200", data)
            return JsonResponse(data, status=200)

        except Exception as e:
            print("status: 400", error_data(board="NotExist"))
            return JsonResponse(error_data(board="NotExist"), status=400)

    def delete(self, request, board_id):
        try:
            board = Board.objects.get(pk=board_id)
            board.delete()
            print("status: 200", success_data("BoardDeleted"))
            return JsonResponse(success_data("BoardDeleted"), status=200)

        except Exception as e:
            print("status: 400", error_data(board="NotExist"))
            return JsonResponse(error_data(board="NotExist"), status=400)


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
            data = PostSerializer(Post.objects.get(pk=post_id))
            return JsonResponse(data)
        except ObjectDoesNotExist as e:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            if request.data.get("des"):
                post.des = request.data.get("des")
            if request.data.get("location"):
                post.location = request.data.get("location")
            if request.data.get("tags"):
                tags = request.data.get("tags").split()
                for tag in tags:
                    try:
                        Tag.objects.create(name=tag)
                    except Exception as e:
                        pass
                post.tags.clear()
                post.tags.add(*tags)
            post.save()
            data = PostSerializer(Post.objects.get(pk=post_id))
            return JsonResponse(data)

        except ObjectDoesNotExist:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            post.delete()
            print("status: 200", success_data("PostDeletedSuccessfully"))
            return JsonResponse(success_data("PostDeletedSuccessfully"))
        except ObjectDoesNotExist as e:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)


class Posts(APIView):
    """
    This class handles requests sent to /api/v0/social/posts.
    In post method it handles creation of a new post and in
    get method it returns posts associated with the query part.
    """

    def get(self, request):
        tag = request.query_params.get("tag")
        if tag:
            data = get_paginated_data(
                data=PostSerializer(Post.objects.filter(tags__name=tag), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/posts/?tag={tag}"
            )
            return JsonResponse(data)

        user = get_user(request)
        if user:
            data = get_paginated_data(
                data=PostSerializer(Post.objects.filter(user_id=user.pk), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/posts/?username={user.username}"
            )
            return JsonResponse(data)
        else:
            print("status: 400", error_data(profile="NotExist"))
            return JsonResponse(error_data(profile="NotExist"), status=400)

    def post(self, request):
        new_post = CreatePostFrom(request.POST, request.FILES)
        if new_post.is_valid():
            new_post.save(request.user)
            print("status: 200", success_data("PostCreatedSuccessfully"))
            return JsonResponse(success_data("PostCreatedSuccessfully"))
        else:
            errors = {}
            errors_as_json = json.loads(new_post.errors.as_json())
            image_error = errors_as_json.get("image")
            if image_error.get("image") == "required":
                errors["image"] = ["Required"]
            return JsonResponse({"error": errors}, status=400)


class PostLikesAPIView(APIView):
    # extra future
    # def get(self, request, post_id):
    #     try:
    #         post = Post.objects.get(pk=post_id)
    #         data = get_paginated_data(
    #             data=ProfileSerializer(post.likes.all(), many=True, fields=(
    #                 "username", "name", "image", "private", "isFollowed")).data,
    #             page=request.query_params.get('page'),
    #             limit=request.query_params.get('limit'),
    #             url=F"/social/posts/{post_id}/likes/?"
    #         )
    #         return JsonResponse(data)
    #     except ObjectDoesNotExist:
    #         print("status: 400", error_data(post="NotExist"))
    #         return JsonResponse(error_data(post="NotExist"), status=400)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            if request.data.get('method'):
                method = request.data.get('method')
                if method == "like":
                    post.likes.add(request.user)
                    return JsonResponse(success_data("PostLiked"))
                elif method == "dislike":
                    post.likes.remove(request.user)
                    return JsonResponse(success_data("PostDisliked"))
                else:
                    print("status: 400", error_data(method="WrongData"))
                    return JsonResponse(error_data(method="WrongData"), status=400)
            else:
                print("status: 400", error_data(method="Required"))
                return JsonResponse(error_data(method="Required"), status=400)
        except ObjectDoesNotExist:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)


class PostCommentsAPIView(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            data = get_paginated_data(
                data=CommentSerializer(post.comments.all(), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/posts/{post_id}/comments/?"
            )
            return JsonResponse(data)
        except ObjectDoesNotExist:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

    def post(self, request, post_id):
        text = request.data.get('text')
        if text:
            try:
                post = Post.objects.get(pk=post_id)
                comment = post.comments.create(user=request.user, text=text)
                data = CommentSerializer(comment).data
                return JsonResponse(data)
            except ObjectDoesNotExist:
                print("status: 400", error_data(post="NotExist"))
                return JsonResponse(error_data(post="NotExist"), status=400)
        else:
            print("status: 400", error_data(text="Required"))
            return JsonResponse(error_data(text="Required"), status=400)
