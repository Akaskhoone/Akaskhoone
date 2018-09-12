from rest_framework import serializers
from accounts.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
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
    isFollowed = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("username", "name", "bio", "image", "followings", "followers", "private", "isFollowed")

    def get_username(self, obj):
        return obj.user.username

    def get_image(self, obj):
        return str(obj.image)

    def get_followings(self, obj):
        return obj.followings.count()

    def get_followers(self, obj):
        return obj.followers.count()

    def get_isFollowed(self, obj):
        requester = self.context.get("requester")
        if requester:
            return obj in requester.followings.all()
        return False
