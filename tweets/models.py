from django.contrib.auth.models import User
from django.db import models
from utils.time_helpers import utc_now


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
