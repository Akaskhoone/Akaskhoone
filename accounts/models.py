import os

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from .managers import UserManager
from .validators import UnicodeUsernameValidator, UnicodeNameValidator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    is_staff = models.BooleanField(
        verbose_name='staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_active = models.BooleanField(
        verbose_name='active',
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting accounts.'
    )
    date_joined = models.DateTimeField('date joined', default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return str(self.email)


def get_profile_image_path(instance, filename):
    return os.path.join('profile_photos', str(instance.user.id), filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False)
    bio = models.TextField(verbose_name='biography', null=True, blank=True)
    image = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True,
                              default='profile_photos/default.jpg')
    followings = models.ManyToManyField('Profile', related_name='followers', blank=True, symmetrical=False)
    requests = models.ManyToManyField('Profile', related_name='requests_sent', blank=True, symmetrical=False)
    is_private = models.BooleanField(verbose_name="private", default=True)

    def clean(self):
        super().clean()
        if not self.image:
            self.image = 'profile_photos/default.jpg'

    def __str__(self):
        return str(self.user)


class Contact(models.Model):
    email = models.EmailField(primary_key=True)
    users = models.ManyToManyField(User, related_name='contacts', through='Invitation')

    def __str__(self):
        return self.email


class Invitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='invited_by')
    invited = models.BooleanField(default=False)

    def __str__(self):
        return F"{self.user.email} {'invited' if self.invited else 'not invited'} {self.contact.email}"

    class Meta:
        unique_together = ('user', 'contact')
