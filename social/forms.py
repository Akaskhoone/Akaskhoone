from django import forms
from .models import Post


class CreatePostFrom(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['date']
