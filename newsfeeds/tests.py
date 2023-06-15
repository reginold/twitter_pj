from newsfeeds.services import NewsFeedServices
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient


class NewsFeedServiceTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user("user1", "user1@sample.com")
        self.user2 = self.create_user("user2", "user2@sample.com")

    def test_get_user_newsfeed(self):
        newsfeed_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.user2)
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeed_ids.append(newsfeed.id)
        newsfeed_ids = newsfeed_ids[::-1]

        # cache miss
        newsfeeds = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

        # cache hit
        newsfeeds = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

        # cahce updated
        tweet = self.create_tweet(self.user1)
        new_newsfeed = self.create_newsfeed(self.user1, tweet)
        newsfeeds = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        newsfeed_ids.insert(0, new_newsfeed.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

    def test_create_new_newsfeed_before_get_cached_newsfeeds(self):
        feed1 = self.create_newsfeed(self.user1, self.create_tweet(self.user1))

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key), False)
        feed2 = self.create_newsfeed(self.user1, self.create_tweet(self.user1))
        self.assertEqual(conn.exists(key), True)

        feeds = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.id for f in feeds], [feed2.id, feed1.id])
