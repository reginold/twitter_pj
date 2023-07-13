from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    from newsfeeds.services import NewsFeedServices

    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    # use bulk_create to change insert to one line
    NewsFeed.objects.bulk_create(newsfeeds)
    # since post_save signal func would not trigger the bulk create, need push into cache
    for newsfeed in newsfeeds:
        NewsFeedServices.push_newsfeed_to_cache(newsfeed)
