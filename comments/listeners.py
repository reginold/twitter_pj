from utils.listeners import invalidate_object_cache
from utils.redis_helper import RedisHelper


def increase_comments_count(sender, instance, created, **kwargs):
    from django.db.models import F

    from tweets.models import Tweet

    if not created:
        return

    # handle new comment
    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F("comments_count") + 1
    )
    RedisHelper.increase_count(instance.tweet, "comments_count")


def decrease_comments_count(sender, instance, **kwargs):
    from django.db.models import F

    from tweets.models import Tweet

    Tweet.objects.filter(id=instance.tweet_id).update(
        comments_count=F("comments_count") - 1
    )
    RedisHelper.decrease_count(instance.tweet, "comments_count")
