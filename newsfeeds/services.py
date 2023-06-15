from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedServices:
    @classmethod
    def fanout_to_followers(cls, tweet):
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        # use bulk_create to change insert to one line
        NewsFeed.objects.bulk_create(newsfeeds)
        # since post_save signal func would not trigger the bulk create, need push into cache
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        # Queryset is lazy loading
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by("-created_at")
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        # Queryset is lazy loading
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by(
            "-created_at"
        )
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)
