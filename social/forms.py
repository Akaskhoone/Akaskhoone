from django import forms
from .models import Tag, Post


class CreatePostFrom(forms.Form):
    image = forms.ImageField(required=True)
    des = forms.CharField(required=False, max_length=250)
    location = forms.CharField(required=False, max_length=100)
    tags = forms.CharField(required=False, max_length=250)

    def save(self, user):
        tags = self.cleaned_data["tags"].split()
        for tag in tags:
            Tag.objects.get_or_create(name=tag)
        new_post = Post.objects.create(user=user, image=self.cleaned_data["image"], des=self.cleaned_data["des"],
                                       location=self.cleaned_data["location"])
        new_post.tags.add(*tags)
