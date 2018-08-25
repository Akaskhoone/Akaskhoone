from django.forms import *
from .models import Post


class UploadImageForm(ModelForm):
    class Meta:
        model = Post
        fields = ["tags", "image", "des", "location", "user"]
