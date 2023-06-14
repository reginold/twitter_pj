from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from comments.listeners import increase_comments_count, decrease_comments_count
from django.db.models.signals import post_save, pre_delete

from likes.models import Like
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper


class Comment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = [
            ("tweet", "created_at"),
        ]

    def __str__(self) -> str:
        return "{} - {} says {} at tweet {}".format(
            self.created_at, self.user, self.content, self.tweet_id
        )

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=self.id,
        ).order_by("-created_at")

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)

post_save.connect(increase_comments_count, sender=Comment)
pre_delete.connect(decrease_comments_count, sender=Comment)