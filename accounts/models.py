from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    # use one2one field to create the unique index, so that the point the diff userprofile
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # user the filefield , not imagefield
    avater = models.FileField(null=True)

    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} {self.nickname}"


def get_profile(user):
    if hasattr(user, "_cached_user_profile"):
        return getattr(user, "_cached_user_profile")
    profile, _ = UserProfile.objects.get_or_create(user=user)
    setattr(user, "_cached_user_profile", profile)
    return profile


User.profile = property(get_profile)
