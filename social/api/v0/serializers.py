from rest_framework import serializers
from social.models import Post, Tag, Comment, Board


class PostSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(PostSerializer, self).__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    postId = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    commentsCount = serializers.SerializerMethodField()
    likesCount = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('postId', 'creator', 'image', 'location', 'des', 'tags', 'commentsCount', 'likesCount', 'date')

    def get_postId(self, obj):
        return obj.pk

    def get_creator(self, obj):
        return {"username": obj.user.username, "name": obj.user.profile.name, "image": str(obj.user.profile.image)}

    def get_image(self, obj):
        return F"{obj.image}"

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data

    def get_commentsCount(self, obj):
        return obj.comments.count()

    def get_likesCount(self, obj):
        return obj.likes.count()

    def get_date(self, obj):
        return F"{obj.date}"


class BoardSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(BoardSerializer, self).__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    boardId = serializers.SerializerMethodField()
    postsCount = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('boardId', 'name', 'postsCount', 'posts')

    def get_boardId(self, obj):
        return obj.pk

    def get_postsCount(self, obj):
        return obj.posts.count()

    def get_posts(self, obj):
        return PostSerializer(obj.posts.all(), many=True, fields=('postId', 'image')).data


class CommentSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(CommentSerializer, self).__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    commentId = serializers.SerializerMethodField()
    postId = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('commentId', 'postId', 'creator', 'text', 'date')

    def get_commentId(self, obj):
        return obj.pk

    def get_postId(self, obj):
        return obj.post.id

    def get_creator(self, obj):
        return {"username": obj.user.username, "name": obj.user.profile.name, "image": str(obj.user.profile.image)}

    def get_date(self, obj):
        return F"{obj.date}"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)
