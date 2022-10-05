from testing.testcases import TestCase

from friendships.models import Friendship
from friendships.services import FriendshipService


class FriendshipServiceTests(TestCase):
    def setUp(self) -> None:
        self.clear_cache()
        self.user1 = self.create_user("user1_name", email="user1@example.com")
        self.user2 = self.create_user("user2_name", email="user2@exmple.com")

    def test_get_following(self):
        follow_user1 = self.create_user("follow_user1", email="follow_user1@exmple.com")
        follow_user2 = self.create_user("follow_user2", email="follow_user2@exmple.com")

        for to_user in [follow_user1, follow_user2, self.user2]:
            Friendship.objects.create(from_user=self.user1, to_user=to_user)

        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertSetEqual(
            user_id_set, {follow_user1.id, follow_user2.id, self.user2.id}
        )

        Friendship.objects.filter(from_user=self.user1, to_user=self.user2).delete()
        user_id_set = FriendshipService.get_following_user_id_set(self.user1.id)
        self.assertSetEqual(user_id_set, {follow_user1.id, follow_user2.id})
