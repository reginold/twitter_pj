from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.constants import FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from utils.time_constants import ONE_HOUR


@shared_task(routing_key="newsfeeds", time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    from newsfeeds.services import NewsFeedServices

    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id) for follower_id in follower_ids
    ]

    # use bulk_create to change insert to one line
    NewsFeed.objects.bulk_create(newsfeeds)
    # since post_save signal func would not trigger the bulk create, need push into cache
    for newsfeed in newsfeeds:
        NewsFeedServices.push_newsfeed_to_cache(newsfeed)

    return f"{len(newsfeeds)} newsfeeds created."


@shared_task(routing_key="default", time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    # Fanout the tweet to all followers' timeline
    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    index = 0
    while index < len(follower_ids):
        batch_ids = follower_ids[index : index + FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, batch_ids)
        index += FANOUT_BATCH_SIZE

    return "{} newsfeeds going to be fanout, {} batch created.".format(
        len(follower_ids),
        (len(follower_ids) - 1) // FANOUT_BATCH_SIZE + 1,
    )
