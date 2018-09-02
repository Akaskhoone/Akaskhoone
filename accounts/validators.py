import re
from django.core import validators
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ObjectDoesNotExist

@deconstructible
class UnicodeNameValidator(validators.RegexValidator):
    regex = r'([a-zA-Z\s])+$|^$'
    message = (
        'Enter a valid name. This value may contain only English letters and Spaces'
    )
    flags = 0


@deconstructible
class UniqueEmailValidator:
    message = 'Email already exists!'
    code = 'Exists'

    def __init__(self, User):
        self.User = User

    def validate(self, value):
        try:
            self.User.objects.get(email=value)
            raise validators.ValidationError(self.message, self.code)
        except ObjectDoesNotExist as e:
            print(e)

@deconstructible
class UniqueUsernameValidator:
    message = 'User already exists!'
    code = 'Exists'

    def __init__(self, User):
        self.User = User

    def validate(self, value):
        try:
            self.User.objects.get(username=value)
            raise validators.ValidationError(self.message, self.code)
        except ObjectDoesNotExist as e:
            print(e)