import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


def get_profile_image_path(instance, filename):
    return os.path.join('profile_photos', str(instance.user.id), filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField('biography', null=True, blank=True)
    image = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True)
    followers = models.ManyToManyField('Profile', related_name='user_followers', blank=True)
    followings = models.ManyToManyField('Profile', related_name='user_followings', blank=True)

    def __str__(self):
        return str(self.user)
