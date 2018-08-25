import os

from django.db import models
from users.models import User


# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def get_user_image_path(instance, filename):
    return os.path.join('user_photos', str(instance.user.id), filename)


class Post(models.Model):
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(upload_to=get_user_image_path, blank=True, null=True)
    des = models.TextField()
    location = models.CharField(max_length=255, default="RahnemaCollege")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.des
