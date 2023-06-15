def increase_likes_count(sender, instance, created, **kwargs):
    from django.db.models import F

    from tweets.models import Tweet

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    # NOT Recommended
    # tweet =instance.content_object
    # tweet.likes_count += 1
    # tweet.save()
    # reason: because it will not trigger the update_at field and is not the atomic operation

    # method 1
    tweet = instance.content_object
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F("likes_count") + 1)

    # method 2
    # tweet = instance.content_object
    # tweet.likes_count = F('likes_count') + 1
    # tweet.save()


def decrease_likes_count(sender, instance, **kwargs):
    from django.db.models import F

    from tweets.models import Tweet

    model_class = instance.content_type.model_class()
    if model_class != Tweet:
        return

    tweet = instance.content_object
    Tweet.objects.filter(id=instance.object_id).update(likes_count=F("likes_count") - 1)
