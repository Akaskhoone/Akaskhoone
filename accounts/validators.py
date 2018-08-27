import re
from django.core import validators
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class UnicodeNameValidator(validators.RegexValidator):
    regex = r'([a-zA-Z\s])+$|^$'
    message = (
        'Enter a valid name. This value may contain only English letters '
    )
    flags = 0
