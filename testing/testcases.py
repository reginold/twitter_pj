from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient
from tweets.models import Tweet


class TestCase(DjangoTestCase):
    @property
    def anonymous_client(self):
        if hasattr(self, "_anonymous_client"):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email, password=None):
        if password is None:
            password = "generic password"
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = "default tweet content"
        return Tweet.objects.create(user=user, content=content)
