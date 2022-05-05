from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet

# need "/", if not, will cause the 301 redirect error
TWEET_LIST_API = "/api/tweets/"
TWEET_CREATE_API = "/api/tweets/"
TWEET_RETRIEVE_API = "/api/tweets/{}/"


class TweetApiTests(TestCase):
    def setUp(self):

        self.user1 = self.create_user("user1", "user1@gmail.com")
        self.tweets1 = [self.create_tweet(self.user1) for i in range(3)]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user("user2", "user2@gmail.com")
        self.tweets2 = [self.create_tweet(self.user2) for i in range(2)]

    def test_list_api(self):
        # need user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # success request
        response = self.anonymous_client.get(TWEET_LIST_API, {"user_id": self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["tweets"]), 3)

        response = self.anonymous_client.get(TWEET_LIST_API, {"user_id": self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["tweets"]), 2)

        # verify the tweet order
        self.assertEqual(response.data["tweets"][0]["id"], self.tweets2[1].id)
        self.assertEqual(response.data["tweets"][1]["id"], self.tweets2[0].id)

    def test_create_api(self):
        # fail case : not login user
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # fail case: need tweet content
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)

        # fail case : the content length be not too short
        response = self.user1_client.post(TWEET_CREATE_API, {"content": "1"})
        self.assertEqual(response.status_code, 400)

        # fail case : the content length should not be too long
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {"content": "h" * 141},
        )
        self.assertEqual(response.status_code, 400)

        # success case
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(
            TWEET_CREATE_API, {"content": "Hello world, Tweet post"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["id"], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # tweet with id=-1 doesnot exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # when get the tweet, which company with comments
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["comments"]), 0)

        self.create_comment(self.user2, tweet, "second comment")
        self.create_comment(self.user1, tweet, "first comment")
        self.create_comment(self.user1, self.create_tweet(self.user2), "third comment")
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data["comments"]), 2)
