import os
from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.name


def get_post_image_path(instance, filename):
    return os.path.join('posts', str(instance.user.id), filename)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='creator', related_name='posts')
    image = models.ImageField(upload_to=get_post_image_path, blank=True, null=True, verbose_name='post image')
    des = models.TextField(verbose_name='description', null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='location')
    tags = models.ManyToManyField(Tag, related_name='posts', verbose_name='tags', blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='creation date')
    likes = models.ManyToManyField(User, related_name='posts_liked', blank=True)

    def __str__(self):
        return F"[{self.id}] [{self.user}] {self.des}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='creator', related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True, verbose_name='creation date')

    def __str__(self):
        return F"[{self.user}] on post {self.post.id}"


class Board(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='creator', related_name='boards')
    name = models.CharField(max_length=200, verbose_name='name')
    posts = models.ManyToManyField(Post, related_name='boards', verbose_name='posts', blank=False)

    def __str__(self):
        return F"[{self.user}] {self.name}"


class NotificationData(models.Model):
    type = models.CharField(
        choices=[("unfollow", "unfollow"), ("dislike", "dislike"), ("like", "like"), ("follow", "follow"),
                 ("comment", "comment"), ("post", "post"), ("join", "join")], max_length=8)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_data")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name="notifications_data")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True,
                                related_name="notifications_data")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return F"{self.user} {self.type}ed"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="owner", related_name="notifications")
    data = models.ForeignKey(NotificationData, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
