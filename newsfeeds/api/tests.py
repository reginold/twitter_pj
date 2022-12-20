from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase

NEWSFEEDS_URL = "/api/newsfeeds/"
POST_TWEETS_URL = "/api/tweets/"
FOLLOW_URL = "/api/friendships/{}/follow/"


class NewsFeedApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user("user1", "user1@gmail.com")
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user("user2", "user2@gmail.com")
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # create followings and followers for user2
        for i in range(2):
            follower = self.create_user(
                "user2_follower{}".format(i), "user2@gmail.com"
            )
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user(
                "user2_following{}".format(i), "user2@gmail.com"
            )
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_list(self):
        # login
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # post failing
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # base zero
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["newsfeeds"]), 0)
        # newsfeed shows yourself tweet
        self.user1_client.post(POST_TWEETS_URL, {"content": "Hello World"})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data["newsfeeds"]), 1)
        # when follow the user, can see the following feed
        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(
            POST_TWEETS_URL,
            {
                "content": "Hello Twitter",
            },
        )
        posted_tweet_id = response.data["id"]
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data["newsfeeds"]), 2)
        self.assertEqual(response.data["newsfeeds"][0]["tweet"]["id"], posted_tweet_id)

    def test_user_cache(self):
        # Relation: Newsfeed --> Tweet ---> User ---> Profile
        # Test case: test the modification with profile and newsfeed will not be affected
        #            when add the cache feature
        profile = self.user2.profile  # type: ignore
        profile.nickname = "user2_nicky"
        profile.save()

        self.assertEqual(self.user1.username, "user1")
        self.create_newsfeed(self.user2, self.create_tweet(self.user1))
        self.create_newsfeed(self.user1, self.create_tweet(self.user2))

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["user"]["username"], "user2")
        self.assertEqual(results[0]["tweet"]["user"]["nickname"], "user1")
        self.assertEqual(results[1]["tweet"]["user"]["username"], "user1")

        self.user1.username = "user1-for-test"
        self.user1.save()
        profile.nickname = "user2-for-test"
        profile.save()

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["user"]["username"], "user2")
        self.assertEqual(results[0]["tweet"]["user"]["nickname"], "user2-for-test")
        self.assertEqual(results[1]["tweet"]["user"]["username"], "user1-for-test")

