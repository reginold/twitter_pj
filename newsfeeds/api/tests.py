from django.conf import settings
from rest_framework.test import APIClient

from friendships.models import Friendship
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedServices
from testing.testcases import TestCase
from utils.paginations import EndlessPagination

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
            follower = self.create_user(f"user2_follower{i}", "user2@gmail.com")
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user(f"user2_following{i}", "user2@gmail.com")
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
        self.assertEqual(len(response.data["results"]), 0)
        # newsfeed shows yourself tweet
        self.user1_client.post(POST_TWEETS_URL, {"content": "Hello World"})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data["results"]), 1)
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
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["tweet"]["id"], posted_tweet_id)

    def test_user_cache(self):
        # Relation: Newsfeed --> Tweet ---> User ---> Profile
        # Test case: test the modification with profile and newsfeed will not be affected
        #            when add the cache feature
        profile = self.user2.profile
        profile.nickname = "user2_nicky"
        profile.save

        self.assertEqual(self.user1.username, "user1")
        self.create_newsfeed(self.user2, self.create_tweet(self.user1))
        self.create_newsfeed(self.user2, self.create_tweet(self.user2))

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["user"]["username"], "user2")
        # self.assertEqual(results[0]["tweet"]["user"]["nickname"], "user2_nicky")
        self.assertEqual(results[1]["tweet"]["user"]["username"], "user1")

        self.user1.username = "user1-for-test"
        self.user1.save()
        profile.nickname = "user2-for-test"
        profile.save()

        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["user"]["username"], "user2")
        # self.assertEqual(results[0]["tweet"]["user"]["nickname"], "user2-for-test")
        self.assertEqual(results[1]["tweet"]["user"]["username"], "user1-for-test")

    def test_tweet_cache(self):
        tweet = self.create_tweet(self.user1, "content1")
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["user"]["username"], "user1")
        self.assertEqual(results[0]["tweet"]["content"], "content1")

        # update username
        self.user1.username = "user1chong"
        self.user1.save()
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["user"]["username"], "user1chong")

        # update content
        tweet.content = "content2"
        tweet.save()
        response = self.user2_client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["tweet"]["content"], "content2")

    def _paginate_to_get_newsfeeds(self, client):
        # paginate until the end
        response = client.get(NEWSFEEDS_URL)
        results = response.data["results"]
        while response.data["has_next_page"]:
            created_at__lt = response.data["results"][-1]["created_at"]
            response = client.get(NEWSFEEDS_URL, {"created_at__lt": created_at__lt})
            results.extend(response.data["results"])
        return results

    def test_redis_list_limit(self):
        list_limit = settings.REDIS_LIST_LENGTH_LIMIT
        page_size = EndlessPagination.page_size
        users = [
            self.create_user(f"user{i}test", email="user@example.com") for i in range(5)
        ]
        newsfeeds = []
        for i in range(list_limit + page_size):
            tweet = self.create_tweet(user=users[i % 5], content=f"feed{i}")
            feed = self.create_newsfeed(self.user1, tweet)
            newsfeeds.append(feed)
        newsfeeds = newsfeeds[::-1]

        # only cached list_limit objects
        cached_newsfeeds = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_newsfeeds), list_limit)
        queryset = NewsFeed.objects.filter(user=self.user1)
        self.assertEqual(queryset.count(), list_limit + page_size)

        results = self._paginate_to_get_newsfeeds(self.user1_client)
        self.assertEqual(len(results), list_limit + page_size)
        for i in range(list_limit + page_size):
            self.assertEqual(newsfeeds[i].id, results[i]["id"])

        # a followed user create a new tweet
        self.create_friendship(self.user1, self.user2)
        new_tweet = self.create_tweet(self.user2, "a new tweet")
        NewsFeedServices.fanout_to_followers(new_tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._paginate_to_get_newsfeeds(self.user1_client)
            self.assertEqual(len(results), list_limit + page_size + 1)
            self.assertEqual(results[0]["tweet"]["id"], new_tweet.id)
            for i in range(list_limit + page_size):
                self.assertEqual(newsfeeds[i].id, results[i + 1]["id"])

        _test_newsfeeds_after_new_feed_pushed()

        # cache expired
        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()
