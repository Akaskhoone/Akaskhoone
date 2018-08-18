import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


def get_profile_image_path(instance, filename):
    return os.path.join('profile_photos', str(instance.id), filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField('biography')
    image = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True)
    followers = models.ManyToManyField('Profile', related_name='user_followers')
    followings = models.ManyToManyField('Profile', related_name='user_followings')


