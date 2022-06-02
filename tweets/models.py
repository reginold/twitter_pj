from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from likes.models import Like
from utils.time_helpers import utc_now

from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus


class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="define the author of the tweet",
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # POINT:create the compound together, campare the first key, second key...
    #  e.g.
    #  [
    #    ("user1", "created_at1", "id1"),
    #    ("user1", "created_at2", "id2"),
    # .  ("user2", "created_at3", "id3"),
    #  ]
    class Meta:
        index_together = (("user", "created_at"),)
        ordering = ("user", "-created_at")

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # Print the timestamp and content of tweet: print(tweet instance)
        return f"{self.created_at} {self.user}: {self.content}"

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by("-created_at")


class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    # distinguish the images and in the future if the user upload the illegal images
    # so that you can track the user quickly, regardless of tweet.user
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # image file
    file = models.FileField()
    order = models.IntegerField(default=0)

    # image status, used by audit
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete, will deleted after the xx time
    has_deleted = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ("user", "created_at"),
            ("has_deleted", "created_at"),
            ("status", "created_at"),
            ("tweet", "order"),
        )

    def __str__(self) -> str:
        return f"{self.tweet_id}: {self.file}"
