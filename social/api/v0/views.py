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
                return JsonResponse(error_data(request="Invalid"), status=400)

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
            boards = user.boards.all()
            boards_list = []
            for board in boards:
                posts = []
                for post in board.posts.all():
                    posts.append({
                        "post_id": post.id,
                        "image": str(post.image)
                    })
                boards_list.append({
                    "board_id": board.id,
                    "name": board.name,
                    "count": board.posts.count(),
                    "posts": posts
                })
            data = {
                "count": len(boards),
                "boards": boards_list
            }
            print("status: 200 >> board objects returned for user {}".format(user))
            return JsonResponse(data, status=200, safe=False)
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
            board = Board.objects.get(pk=board_id)
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
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

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
            print("status: 400", error_data(request="Invalid"))
            return JsonResponse(error_data(request="Invalid"), status=400)
        return JsonResponse({"posts": posts_list})

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


# todo pagination is not implemented, but needed!

class PostLikesAPIView(APIView):
    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            users = []
            for user in post.likes.all():
                users.append({
                    "username": user.username,
                    "name": user.profile.name,
                    "image": str(user.profile.image)
                })
            return JsonResponse(data=users, safe=False)
        except ObjectDoesNotExist:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

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
            comments = []
            for comment in post.comments.all():
                comments.append({
                    "comment_id": comment.id,
                    "username": comment.user.username,
                    "name": comment.user.profile.name,
                    "image": str(comment.user.profile.image),
                    "text": comment.text
                })
            return JsonResponse(data=comments, safe=False)
        except ObjectDoesNotExist:
            print("status: 400", error_data(post="NotExist"))
            return JsonResponse(error_data(post="NotExist"), status=400)

    def post(self, request, post_id):
        text = request.data.get('text')
        if text:
            try:
                post = Post.objects.get(pk=post_id)
                comment = post.comments.create(user=request.user, text=text)
                comment = {
                    "comment_id": comment.id,
                    "username": comment.user.username,
                    "name": comment.user.profile.name,
                    "image": str(comment.user.profile.image),
                    "text": comment.text
                }
                return JsonResponse(data=comment, safe=False)
            except ObjectDoesNotExist:
                print("status: 400", error_data(post="NotExist"))
                return JsonResponse(error_data(post="NotExist"), status=400)
        else:
            print("status: 400", error_data(text="Required"))
            return JsonResponse(error_data(text="Required"), status=400)
