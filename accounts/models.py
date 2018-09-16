import os, json, requests
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from .managers import UserManager
from .validators import UnicodeUsernameValidator, UnicodeNameValidator, ASCIIUsernameValidator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username_validator = ASCIIUsernameValidator()
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

    def send_email(self, subject, body):
        data = {
            "to": self.email,
            "subject": str(subject),
            "body": str(body)
        }
        headers = {"Agent-Key": "3Q0gRe22zp", "content-type": "application/json"}
        response = requests.post(url='http://192.168.10.66:80/api/send/mail', data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return True
        return False

    def clean(self):
        super().clean()
        self.email = str(self.email).lower()
        self.username = str(self.username).lower()


def get_profile_image_path(instance, filename):
    return os.path.join('profile_photos', str(instance.user.id), filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name_validator = UnicodeNameValidator()
    name = models.CharField(max_length=100, blank=False, validators=[name_validator])
    bio = models.TextField(verbose_name='biography', null=True, blank=True)
    image = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True,
                              default='profile_photos/default.jpg')
    followings = models.ManyToManyField('Profile', related_name='followers', blank=True, symmetrical=False)
    requests = models.ManyToManyField('Profile', related_name='requests_sent', blank=True, symmetrical=False)
    is_private = models.BooleanField(verbose_name="private", default=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.clean()
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

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
