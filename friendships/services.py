from friendships.models import Friendship


# userA following list, the loggedin user can see the following list
# To userB [followed]
# To userC [Not followed]
class FriendshipService(object):
    @classmethod
    def get_followers(cls, user):
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related("from_user")
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user,
        ).exists()
