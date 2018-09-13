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

    creator = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'creator', 'image', 'location', 'des', 'tags', 'comments_count', 'likes_count', 'date')

    def get_creator(self, obj):
        return {"username": obj.user.username, "name": obj.user.profile.name, "image": str(obj.user.profile.image)}

    def get_image(self, obj):
        return F"{obj.image}"

    def get_tags(self, obj):
        return TagSerializer(obj.tags.all(), many=True).data

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
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

    posts_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ('id', 'name', 'posts_count', 'posts')

    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_posts(self, obj):
        return PostSerializer(obj.posts.all(), many=True, fields=('post_id', 'image')).data


class CommentSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(CommentSerializer, self).__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    post_id = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'post_id', 'creator', 'text', 'date')

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
