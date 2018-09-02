from django.contrib.auth.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django import forms
from .validators import UnicodeNameValidator, UnicodeUsernameValidator, UniqueEmailValidator, UniqueUsernameValidator
from .models import User, Profile


class SignUpForm(forms.Form):

    email = forms.EmailField()
    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator],
    )
    password = forms.CharField(max_length=128)
    name_validator = UnicodeNameValidator()
    name = forms.CharField(max_length=100, validators=[name_validator])
    bio = forms.CharField()
    image = forms.ImageField()

    def save(self):
        user = User.objects.create_user(email=self.cleaned_data["email"], username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        Profile.objects.create(user=user, name=self.cleaned_data["name"], bio=self.cleaned_data["bio"], image=self.cleaned_data["image"])

    def is_valid(self):
        is_valid = super(SignUpForm, self).is_valid()
        if not is_valid:
            return is_valid
        # try:
        #     User.objects.get(email=self.cleaned_data["email"])
        #     return False
        # except User.DoesNotExist:
        #     pass
        # try:
        #     User.objects.get(username=self.cleaned_data["username"])
        #     return False
        # except User.DoesNotExist:
        #     pass
        try:
            unique_email_validator = UniqueEmailValidator(User=User)
            unique_email_validator.validate(self.data["email"])
        except Exception as e:
            self.add_error(field="email", error=e)
            is_valid = False

        try:
            unique_username_validator = UniqueUsernameValidator(User=User)
            unique_username_validator.validate(self.data["username"])
        except Exception as e:
            self.add_error(field="username", error=e)
            is_valid = False

        return is_valid
