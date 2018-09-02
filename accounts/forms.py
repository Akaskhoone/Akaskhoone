from django.contrib.auth.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
import os
from django import forms
from .validators import UnicodeNameValidator, UnicodeUsernameValidator
from .models import User, Profile


class ProfileEditForm(forms.Form):
    name_validator = UnicodeNameValidator()
    name = forms.CharField(max_length=100, validators=[name_validator])
    bio = forms.CharField()
    image = forms.ImageField(required=False)

    def save(self, user):
        user.profile.name = self.cleaned_data["name"]
        user.profile.bio = self.cleaned_data["bio"]
        user.profile.image = self.cleaned_data["image"]
        user.profile.save()
        user.save()

    def is_valid(self):
        is_valid = super(ProfileEditForm, self).is_valid()
        return is_valid
