from notifications.models import Notification
from testing.testcases import TestCase

COMMENT_URL = "/api/comments/"
LIKE_URL = "/api/likes/"


class NotificationTests(TestCase):
    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client(
            "user1", "user1@sample.com"
        )
        self.user2, self.user2_client = self.create_user_and_client(
            "user2", "user2@sample.com"
        )
        self.user2_tweet = self.create_tweet(self.user2)

    def test_comment_create_api_trigger_notification(self):
        """test the user1 comment the user2 tweet, creat the notification."""
        self.assertEqual(Notification.objects.count(), 0)
        self.user1_client.post(
            COMMENT_URL,
            {
                "tweet_id": self.user2_tweet.id,
                "content": "test this one.",
            },
        )
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_trigger_notification(self):
        """test the user1 like user2 tweet, create the notification."""
        self.assertEqual(Notification.objects.count(), 0)
        self.user1_client.post(
            LIKE_URL,
            {"content_type": "tweet", "object_id": self.user2_tweet.id},
        )
        self.assertEqual(Notification.objects.count(), 1)
