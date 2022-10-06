def invalidate_followings_cache(sender, instance, **kwargs):
    # Cannot import at the first line of file, because it will cause the loop error
    from friendships.services import FriendshipService

    FriendshipService.invalidate_following_cache(instance.from_user_id)
