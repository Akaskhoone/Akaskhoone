from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from users.models import Profile

followings = []


@receiver(m2m_changed, sender=Profile.followings.through)
def follow_unfollow(sender, instance, action, **kwargs):
    global followings
    if action == "pre_add" or action == "pre_remove":
        followings = list(instance.followings.all())
    if action == "post_add":
        newly_added = [profile for profile in instance.followings.all() if profile not in followings]
        for followed in newly_added:
            followed.followers.add(instance)
    if action == "post_remove":
        newly_removed = [profile for profile in followings if profile not in instance.followings.all()]
        # print(newly_removed)
        for unfollowed in newly_removed:
            unfollowed.followers.remove(instance)
