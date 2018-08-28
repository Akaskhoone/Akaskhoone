import os
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.name


def get_post_image_path(instance, filename):
    return os.path.join('posts', str(instance.user.id), filename)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='creator')
    image = models.ImageField(upload_to=get_post_image_path, blank=True, null=True, verbose_name='post image')
    des = models.TextField(verbose_name='description')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='location')
    tags = models.ManyToManyField(Tag, related_name='Posts', verbose_name='tags')
    date = models.DateTimeField(auto_now_add=True, verbose_name='creation date')

    def __str__(self):
        return F"[{self.user}] {self.des}"