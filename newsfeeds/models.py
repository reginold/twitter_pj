from django.contrib.auth.models import User
from django.db import models

from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


class NewsFeed(models.Model):
    # The users can see the tweet feed.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = [
            ("user", "created_at"),
        ]
        unique_together = [
            ("user", "tweet"),
        ]
        ordering = [
            "-created_at",
        ]

    def __str__(self) -> str:
        return f"{self.created_at} inbox of {self.user}: {self.tweet}"

    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)
