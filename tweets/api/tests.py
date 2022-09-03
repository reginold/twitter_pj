from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from utils.paginations import EndlessPagination

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
        self.assertEqual(len(response.data["results"]), 3)

        response = self.anonymous_client.get(TWEET_LIST_API, {"user_id": self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

        # verify the tweet order
        self.assertEqual(response.data["results"][0]["id"], self.tweets2[1].id)
        self.assertEqual(response.data["results"][1]["id"], self.tweets2[0].id)

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

    def test_create_with_files(self):
        """test the uploading files to tweet"""
        # test uploading ZERO image and content only successfully
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {
                "content": "uploading the zero image...",
                "files": [],
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # test uploading ONE image successfully
        file = SimpleUploadedFile(
            name="1.jpg",
            content=str.encode("a fake image"),
            content_type="image/jpeg",
        )
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {
                "content": "uploading the one image...",
                "files": [file],
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 1)

        # test uploading the MULTI images successfully
        file_1 = SimpleUploadedFile(
            name="1.jpg",
            content=str.encode("a fake image1"),
            content_type="image/jpeg",
        )
        file_2 = SimpleUploadedFile(
            name="2.jpg",
            content=str.encode("a fake image2"),
            content_type="image/jpeg",
        )
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {
                "content": "uploading the two pieces of images...",
                "files": [file_1, file_2],
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TweetPhoto.objects.count(), 3)
        retrieve_url = TWEET_RETRIEVE_API.format(response.data["id"])
        response = self.user1_client.get(retrieve_url)
        self.assertEqual(len(response.data["photo_urls"]), 2)
        self.assertEqual("1" in response.data["photo_urls"][0], True)
        self.assertEqual("2" in response.data["photo_urls"][1], True)

        # test uploading the TEN images failed
        files = [
            SimpleUploadedFile(
                name=f"selfie{i}.jpg",
                content=str.encode(f"selfie{i}"),
                content_type="image/jpeg",
            )
            for i in range(10)
        ]
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {
                "content": "failed due to number of photos exceeded limit",
                "files": files,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TweetPhoto.objects.count(), 3)

    def test_pagination(self):
        page_size = EndlessPagination.page_size

        # create page_size * 2 tweets
        # we have created self.tweets1 in setUp
        for i in range(page_size * 2 - len(self.tweets1)):
            self.tweets1.append(self.create_tweet(self.user1, "tweet{}".format(i)))

        tweets = self.tweets1[::-1]

        # pull the first page
        response = self.user1_client.get(TWEET_LIST_API, {"user_id": self.user1.id})
        self.assertEqual(response.data["has_next_page"], True)
        self.assertEqual(len(response.date["results"]), page_size)
        self.assertEqual(response.data["results"][0]["id"], tweets[0].id)
        self.assertEqual(response.data["results"][1]["id"], tweets[1].id)
        self.assertEqual(
            response.data["results"][page_size - 1]["id"], tweets[page_size - 1].id
        )

        # pull the second page
        response = self.user1_client.get(
            TWEET_LIST_API,
            {
                "create_at__lt": tweets[page_size - 1].create_at,
                "user_id": self.user1.id,
            },
        )
        self.assertEqual(response.data["has_next_page"], False)
        self.assertEqual(len(response.date["results"]), page_size)
        self.assertEqual(response.data["results"][0]["id"], tweets[page_size].id)
        self.assertEqual(response.data["results"][1]["id"], tweets[page_size + 1].id)
        self.assertEqual(
            response.data["results"][page_size - 1]["id"], tweets[2 * page_size - 1].id
        )

        # pull latest newsfeeds
        response = self.user1_client.get(
            TWEET_LIST_API,
            {
                "create_at__gt": tweets[0].created_at,
                "user_id": self.user1.id,
            },
        )
        self.assertEqual(response.data["has_next_page"], False)
        self.assertEqual(len(response.date["results"]), 0)

        new_tweet = self.create_tweet(self.user1, "a new tweet comes in...")

        response = self.user1_client.get(
            TWEET_LIST_API,
            {
                {
                    "create_at__gt": tweets[0].created_at,
                    "user_id": self.user1.id,
                },
            },
        )
        self.assertEqual(response.data["has_next_page"], False)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["result"][0]["id"], new_tweet.id)
