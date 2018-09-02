from django.contrib.auth.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
import os
from django import forms
from .validators import UnicodeNameValidator, UnicodeUsernameValidator
from .models import User, Profile


class SignUpForm(forms.Form):

    email = forms.EmailField()
    username_validator = UnicodeUsernameValidator()
    username = forms.CharField(
        max_length=150,
        validators=[username_validator],
    )
    password = forms.CharField(max_length=128)
    name_validator = UnicodeNameValidator()
    name = forms.CharField(max_length=100, validators=[name_validator])
    bio = forms.TextInput()
    image = forms.ImageField()

    def save(self):
        user = User.objects.create_user(email=self.cleaned_data["email"], username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        Profile.objects.create(user=user, name=self.cleaned_data["name"], bio=self.cleaned_data["name"], image=self.cleaned_data["image"])

    def is_valid(self):
        is_valid = super(SignUpForm, self).is_valid()
        if not is_valid:
            return is_valid
        try:
            User.objects.get(email=self.fields["email"])
            return False
        except User.DoesNotExist:
            pass
        try:
            User.objects.get(username=self.fields["username"])
            return False
        except User.DoesNotExist:
            pass

        return is_valid
