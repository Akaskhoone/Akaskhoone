from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(label="Email address", required=True,
                             help_text="Required. Provide a real email address")

    class Meta:
        model = User
        fields = ('email', 'username')

