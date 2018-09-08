import os

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, send_mail

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager
from .validators import UnicodeUsernameValidator, UnicodeNameValidator


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return str(self.email)


def get_profile_image_path(instance, filename):
    return os.path.join('profile_photos', str(instance.user.id), filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name_validator = UnicodeNameValidator()
    name = models.CharField(_('name'), max_length=100, blank=False, validators=[name_validator])
    bio = models.TextField(_('biography'), null=True, blank=True)
    image = models.ImageField(_('image'), upload_to=get_profile_image_path, blank=True, null=True,
                              default='profile_photos/default.jpg')
    followings = models.ManyToManyField('Profile', related_name='followers', blank=True, verbose_name=_('followings'),
                                        symmetrical=False)
    private = models.BooleanField(_('private'), default=True)

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
