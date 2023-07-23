from django.conf import settings
from django.core.cache import caches

from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches["testing"] if settings.TESTING_MODE else caches["default"]


# userA following list, the loggedin user can see the following list
# To userB [followed]
# To userC [Not followed]
class FriendshipService:
    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related("from_user")
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def get_follower_ids(cls, user_id):
        friendships = Friendship.objects.filter(
            to_user_id=user_id,
        )
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        # fetch the cache
        # LRU will be used by release the memory
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        # If the data was not stored in cache, we can search from the DB, maybe litte slow.
        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = {fs.to_user_id for fs in friendships}
        cache.set(key, user_id_set)
        return user_id_set

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)
