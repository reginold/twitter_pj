from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from utils.time_helpers import utc_now

from tweets.models import Tweet


class TweetTests(TestCase):
    def test_hours_to_now(self):
        peter = User.objects.create_user(username="peter")
        tweet = Tweet.objects.create(user=peter, content="peter test the func")
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)
