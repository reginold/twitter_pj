from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedServices
from newsfeeds.tasks import fanout_newsfeeds_main_task
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


class NewsFeedTaskTests(TestCase):
    def setUp(self):
        NewsFeed.objects.all().delete()
        self.clear_cache()
        self.user1 = self.create_user("user1", "user1@example.com")
        self.user2 = self.create_user("user2", "user2@example.com")

    def test_fanout_newsfeeds_main_task(self):
        tweet = self.create_tweet(self.user1, "tweet1")
        self.create_friendship(self.user2, self.user1)
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, "1 newsfeeds going to be fanout, 1 batch created.")
        self.assertEqual(1 + 1, NewsFeed.objects.count())

        cached_list = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 1)

        # create another tweet
        for i in range(2):
            user = self.create_user(f"user{i}test", f"user{i}test@example.com")
            self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, "tweet2")
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, "3 newsfeeds going to be fanout, 1 batch created.")
        self.assertEqual(4 + 2, NewsFeed.objects.count())

        cached_list = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 2)

        user = self.create_user("another_user", "another_user@example.com")
        self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, "tweet3")
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, "4 newsfeeds going to be fanout, 2 batch created.")
        self.assertEqual(8 + 3, NewsFeed.objects.count())
        cached_list = NewsFeedServices.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsFeedServices.get_cached_newsfeeds(self.user2.id)
        self.assertEqual(len(cached_list), 3)
