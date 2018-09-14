from rest_framework import serializers
from accounts.models import Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(TokenSerializer, cls).get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        return token


class ProfileSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        self.requester = kwargs.pop('requester', None)
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    username = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    boards_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "username", "name", "bio", "image", "followings", "followers", "is_private", "is_followed", "posts_count",
            "boards_count")

    def get_username(self, obj):
        return obj.user.username

    def get_image(self, obj):
        return str(obj.image)

    def get_followings(self, obj):
        return obj.followings.count()

    def get_followers(self, obj):
        return obj.followers.count()

    def get_is_followed(self, obj):
        if self.requester:
            return obj in self.requester.followings.all()
        return False

    def get_posts_count(self, obj):
        return obj.user.posts.count()

    def get_boards_count(self, obj):
        return obj.user.boards.count()
