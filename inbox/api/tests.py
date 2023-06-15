from notifications.models import Notification

from testing.testcases import TestCase

COMMENT_URL = "/api/comments/"
LIKE_URL = "/api/likes/"
NOTIFICATIONS_URL = "/api/notifications/"


class NotificationTests(TestCase):
    def setUp(self):
        self.clear_cache()
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


class NotificationApiTests(TestCase):
    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client(
            "user1", "user1@sample.com"
        )
        self.user2, self.user2_client = self.create_user_and_client(
            "user2", "user1@sample.com"
        )
        self.user1_tweet = self.create_tweet(self.user1)

    def test_unread_count(self):
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "tweet",
                "object_id": self.user1_tweet.id,
            },
        )

        url = "/api/notifications/unread-count/"
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["unread_count"], 1)

        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "comment",
                "object_id": comment.id,
            },
        )

        response = self.user1_client.get(url)
        self.assertEqual(response.data["unread_count"], 2)
        response = self.user2_client.get(url)
        self.assertEqual(response.data["unread_count"], 0)

    def test_mark_all_as_read(self):
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "tweet",
                "object_id": self.user1_tweet.id,
            },
        )

        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "comment",
                "object_id": comment.id,
            },
        )

        unread_url = "/api/notifications/unread-count/"
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data["unread_count"], 2)

        mark_url = "/api/notifications/mark-all-as-read/"
        response = self.user1_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.user1_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["marked_count"], 2)
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data["unread_count"], 0)

    def test_list(self):
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "tweet",
                "object_id": self.user1_tweet.id,
            },
        )

        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "comment",
                "object_id": comment.id,
            },
        )

        # anonymous error
        response = self.anonymous_client.get(NOTIFICATIONS_URL)
        self.assertEqual(response.status_code, 403)

        # user2 cannot see the notifications
        response = self.user2_client.get(NOTIFICATIONS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        # user1 can see two notifications
        response = self.user1_client.get(NOTIFICATIONS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

        # mark one notification then you can just see one
        notification = self.user1.notifications.first()
        notification.unread = False
        notification.save()
        response = self.user1_client.get(NOTIFICATIONS_URL)
        self.assertEqual(response.data["count"], 2)
        response = self.user1_client.get(NOTIFICATIONS_URL, {"unread": True})
        self.assertEqual(response.data["count"], 1)
        response = self.user1_client.get(NOTIFICATIONS_URL, {"unread": False})
        self.assertEqual(response.data["count"], 1)

    def test_update(self):
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "tweet",
                "object_id": self.user1_tweet.id,
            },
        )
        comment = self.create_comment(self.user1, self.user1_tweet)
        self.user2_client.post(
            LIKE_URL,
            {
                "content_type": "comment",
                "object_id": comment.id,
            },
        )
        notification = self.user1.notifications.first()

        url = f"/api/notifications/{notification.id}/"

        # post error
        response = self.user2_client.post(url, {"unread": False})
        self.assertEqual(response.status_code, 405)

        # cannot update by the anonymous
        response = self.anonymous_client.put(url, {"unread": False})
        self.assertEqual(response.status_code, 403)

        # queryset ordered by login users, return 404
        response = self.user2_client.put(url, {"unread": False})
        self.assertEqual(response.status_code, 404)

        # marked as read
        response = self.user1_client.put(url, {"unread": False})
        self.assertEqual(response.status_code, 200)
        unread_url = "/api/notifications/unread-count/"
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data["unread_count"], 1)

        # marked again
        response = self.user1_client.put(url, {"unread": True})
        response = self.user1_client.get(unread_url)
        self.assertEqual(response.data["unread_count"], 2)

        # need unread
        response = self.user1_client.put(url, {"verb": "test"})
        self.assertEqual(response.status_code, 400)

        # cannot modify the info
        response = self.user1_client.put(url, {"verb": "test", "unread": False})
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertNotEqual(notification.verb, "test")
