from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile
from .forms import UserCreationForm


@register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    list_display = ['email', 'username', 'is_superuser', 'is_staff']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    # -- snippet --
    # this way you can have different add and change forms if using admin.ModelAdmin
    #
    # def get_form(self, request, obj=None, change=False, **kwargs):
    #     defaults = {}
    #     if obj is None:
    #         defaults['form'] = UserCreationForm
    #     else:
    #         defaults['form'] = UserChangeForm
    #     defaults.update(kwargs)
    #     return super(UserAdmin, self).get_form(request, obj, **defaults)
    # ------------


@register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

