from datetime import timedelta

from django.contrib.auth.models import User
from testing.testcases import TestCase
from utils.time_helpers import utc_now

from tweets.models import Tweet


class TweetTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user("user1", "user1@gmail.com")
        self.tweet = self.create_tweet(self.user1, content="user1 tweet content...")

    def test_hours_to_now(self):
        peter = User.objects.create_user(username="peter")
        tweet = Tweet.objects.create(user=peter, content="peter test the func")
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        user2 = self.create_user("user2", "user2@gmail.com")
        self.create_like(user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)
