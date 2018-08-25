from rest_framework import serializers
from .models import Post


class postSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('tags', 'image', 'des', 'location', 'user')
