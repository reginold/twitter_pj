from django.conf import settings
from django.core.cache import caches

from accounts.models import UserProfile
from twitter.cache import USER_PROFILE_PATTERN

cache = caches["testing"] if settings.TESTING_MODE else caches["default"]


class UserService:
    @classmethod
    def get_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)

        # Read from cache
        profile = cache.get(key)

        # Cache hit return
        if profile is not None:
            return profile

        # Cache miss, read from db
        profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, profile)
        return profile

    @classmethod
    def invalidate_profile(cls, user_id):
        # When user change the password, then delete the user,key
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)
