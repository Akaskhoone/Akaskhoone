import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from django.http import JsonResponse
from social.forms import CreatePostFrom
from accounts.utils import get_user
from social.models import Post, Tag, Board
from social.api.v0.serializers import (PostSerializer, CommentSerializer, TagSerializer, BoardSerializer,
                                       NotificationSerializer)
from akaskhoone.utils import get_paginated_data, error_data, success_data
from akaskhoone.notifications import notify
from django.db.models import Count
from django.contrib.auth import get_user_model
from accounts.utils import has_permission

User = get_user_model()


class TagsAPIView(APIView):
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
                data=TagSerializer(
                    Tag.objects.filter(name__contains=search).annotate(posts_count=Count('posts')).order_by(
                        '-posts_count').exclude(posts__isnull=True), many=True).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/tags/?search={search}"
            )
        else:
            data = get_paginated_data(
                data=TagSerializer(
                    Tag.objects.all().annotate(posts_count=Count('posts')).order_by('-posts_count').exclude(
                        posts__isnull=True),
                    many=True).data,
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
            if not has_permission(request.user, user):
                print("status: 400", error_data(profile="Private"))
                return JsonResponse(error_data(profile="Private"), status=400)

            data = get_paginated_data(
                data=BoardSerializer(user.boards.all().order_by('-id'), requester=request.user, many=True).data,
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
                return JsonResponse(BoardSerializer(board, requester=request.user).data)
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
            if not has_permission(request.user, Board.objects.get(pk=board_id).user):
                print("status: 400", error_data(profile="Private"))
                return JsonResponse(error_data(profile="Private"), status=400)

            board = BoardSerializer(Board.objects.get(pk=board_id), requester=request.user).data
            data = get_paginated_data(
                data=board['posts'],
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/boards/{board_id}/?"
            )
            data.update({
                "id": board['id'],
                "name": board['name'],
                "posts_count": len(data['data']),
            })
            return JsonResponse(data)
        except Exception as e:
            print("status: 400", error_data(board="NotExist"))
            return JsonResponse(error_data(board="NotExist"), status=400)

    def put(self, request, board_id):
        try:
            board = Board.objects.get(pk=board_id, user=request.user)
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
            board = BoardSerializer(board, requester=request.user).data
            data = get_paginated_data(
                data=board['posts'],
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/boards/{board_id}/?"
            )
            data.update({
                "id": board['id'],
                "name": board['name'],
                "posts_count": len(data['data']),
            })
            return JsonResponse(data)

        except Exception as e:
            print("status: 400", error_data(board="NotExist"))
            return JsonResponse(error_data(board="NotExist"), status=400)

    def delete(self, request, board_id):
        try:
            board = Board.objects.get(pk=board_id, user=request.user)
            board.delete()
            return JsonResponse(success_data("BoardDeleted"))

        except Exception as e:
            print("status: 400", error_data(board="NotExist"))
            return JsonResponse(error_data(board="NotExist"), status=400)


class PostDetailAPIView(APIView):
    """
    This class handles requests sent to /api/v0/social/posts/<int: post_id>.
    Get method returns a post in json form if a post with given post_id is available,
    and an error if there is no post with that post_is.
    Put method updates a post with given post_id if available, and an error if not.
    Delete method deletes a post with given post_id if available, and an error if not.
    """

    def get(self, request, post_id):
        try:
            if not has_permission(request.user, Post.objects.get(pk=post_id).user):
                print("status: 400", error_data(profile="Private"))
                return JsonResponse(error_data(profile="Private"), status=400)

            return JsonResponse(PostSerializer(Post.objects.get(pk=post_id), requester=request.user).data)
        except ObjectDoesNotExist as e:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id, user=request.user)
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
            return JsonResponse(PostSerializer(Post.objects.get(pk=post_id), requester=request.user).data)

        except ObjectDoesNotExist:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

    def delete(self, request, post_id):
        try:
            Post.objects.get(pk=post_id, user=request.user).delete()
            print("status: 200", success_data("PostDeletedSuccessfully"))
            return JsonResponse(success_data("PostDeletedSuccessfully"))
        except ObjectDoesNotExist as e:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)


class PostsAPIView(APIView):
    """
    This class handles requests sent to /api/v0/social/posts.
    In post method it handles creation of a new post and in
    get method it returns posts associated with the query part.
    """

    def get(self, request):
        tag = request.query_params.get("tag")
        if tag:
            users = list(Post.objects.all().filter(user__profile__is_private=False).values_list('user', flat=True))
            users += list(request.user.profile.followings.all().values_list('user', flat=True))
            users.append(request.user.pk)
            data = get_paginated_data(
                data=PostSerializer(Post.objects.filter(tags__name=tag, user_id__in=set(users)).order_by('-date'),
                                    many=True, requester=request.user).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/posts/?tag={tag}"
            )
            return JsonResponse(data)

        user = get_user(request)
        if user:
            if not has_permission(request.user, user):
                print("status: 400", error_data(profile="Private"))
                return JsonResponse(error_data(profile="Private"), status=400)

            data = get_paginated_data(
                data=PostSerializer(Post.objects.filter(user_id=user.pk).order_by('-date'), many=True,
                                    requester=request.user).data,
                page=request.query_params.get('page'),
                limit=request.query_params.get('limit'),
                url=F"/social/posts/?username={user.username}"
            )
            return JsonResponse(data)
        else:
            print("status: 400", error_data(profile="NotExist"))
            return JsonResponse(error_data(profile="NotExist"), status=400)

    def post(self, request):
        post_form = CreatePostFrom(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(request.user)
            return JsonResponse(PostSerializer(post, requester=request.user).data)
        else:
            errors = {}
            errors_as_json = json.loads(post_form.errors.as_json())
            image_error = errors_as_json.get("image")
            if image_error.get("image") == "required":
                errors["image"] = ["Required"]
            return JsonResponse({"error": errors}, status=400)


class PostLikesAPIView(APIView):
    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            if request.data.get('method'):
                method = request.data.get('method')
                if method == "like":
                    post.likes.add(request.user)
                    return JsonResponse(PostSerializer(post, requester=request.user).data)
                elif method == "dislike":
                    post.likes.remove(request.user)
                    return JsonResponse(PostSerializer(post, requester=request.user).data)
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


class NotificationsAPIView(APIView):
    def get(self, request):
        notifications = request.user.notifications.all().order_by('-date')
        data = get_paginated_data(
            data=NotificationSerializer(notifications, many=True).data,
            page=request.query_params.get('page'),
            limit=request.query_params.get('limit'),
            url="/social/notifications/?"
        )
        return JsonResponse(data)
