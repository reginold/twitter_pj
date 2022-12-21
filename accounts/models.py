from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete

from accounts.listeners import profile_changed, user_changed


class UserProfile(models.Model):
    # use one2one field to create the unique index, so that the point the diff userprofile
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # user the filefield , not imagefield
    avatar = models.FileField(null=True)

    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.nickname}"


def get_profile(user):
    # Void loop
    from accounts.services import UserService
    if hasattr(user, "_cached_user_profile"):
        return getattr(user, "_cached_user_profile")
    profile = UserService.get_profile_through_cache(user.id)
    setattr(user, "_cached_user_profile", profile)
    return profile


User.profile = property(get_profile)

# hook up with listeners to invalidate cache
pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)

pre_delete.connect(profile_changed, sender=UserProfile)
post_save.connect(profile_changed, sender=UserProfile)
