import re
from django.core import validators
from django.core.exceptions import ValidationError


class NameValidator(validators.RegexValidator):
    regex = r'([a-zA-Z\s])+$|^$'
    message = (
        'Enter a valid name. This value may contain only English letters and spaces '
    )
    flags = re.ASCII

    def __call__(self, value):
        regex_matches = self.regex.match(str(value))
        invalid_input = regex_matches if self.inverse_match else not regex_matches
        if invalid_input:
            raise ValidationError(self.message, code=self.code)


class UsernameValidator(validators.RegexValidator):
    regex = r'([a-zA-Z0-9._])+$'
    message = (
        'Enter a valid username. This value may contain only English letters '
    )
    flags = re.ASCII

    def __call__(self, value):
        regex_matches = self.regex.match(str(value))
        invalid_input = regex_matches if self.inverse_match else not regex_matches
        if invalid_input:
            raise ValidationError(self.message, code=self.code)