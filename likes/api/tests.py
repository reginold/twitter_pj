from rest_framework.test import APIClient
from testing.testcases import TestCase

LIKE_BASE_URL = "/api/likes/"
LIKE_CANCEL_URL = "/api/likes/cancel/"
COMMENT_LIST_API = "/api/comments/"
TWEET_LIST_API = "/api/tweets/"
TWEET_DETAIL_API = "/api/tweets/{}/"
NEWSFEED_LIST_API = "/api/newsfeeds/"


class LikeApiTests(TestCase):
    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client(
            "user1", "user1@example.com"
        )
        self.user2, self.user2_client = self.create_user_and_client(
            "user2", "user2@example.com"
        )

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.user1)
        data = {"content_type": "tweet", "object_id": tweet.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get method is not allowed
        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.user1_client.post(
            LIKE_BASE_URL,
            {
                "content_type": "tweetttttt",
                "object_id": tweet.id,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("content_type" in response.data["errors"], True)

        # wrong object_id
        response = self.user1_client.post(
            LIKE_BASE_URL,
            {
                "content_type": "tweet",
                "object_id": 1.5,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("object_id" in response.data["errors"], True)

        # post method succeed
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # duplicate likes
        self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)
        data = {"content_type": "comment", "object_id": comment.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get method is not allowed
        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.user1_client.post(
            LIKE_BASE_URL,
            {
                "content_type": "coment",
                "object_id": comment.id,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("content_type" in response.data["errors"], True)

        # wrong object_id
        response = self.user1_client.post(
            LIKE_BASE_URL,
            {
                "content_type": "comment",
                "object_id": 1.5,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("object_id" in response.data["errors"], True)

        # post method succeed
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicate likes
        self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 1)
        self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):

        # set user1's comment like and user2's tweet like
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)
        like_tweet_data = {"content_type": "tweet", "object_id": tweet.id}
        like_comment_data = {"content_type": "comment", "object_id": comment.id}
        self.user1_client.post(LIKE_BASE_URL, like_comment_data)
        self.user2_client.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        # get method is not allowed
        response = self.user1_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.user1_client.post(
            LIKE_CANCEL_URL,
            {
                "content_type": "commenttttttt",
                "object_id": comment.id,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("content_type" in response.data["errors"], True)

        # wrong object_id
        response = self.user1_client.post(
            LIKE_CANCEL_URL,
            {
                "content_type": "comment",
                "object_id": 1.5,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("object_id" in response.data["errors"], True)

        # if user2 dislike the comment, the count num won't change
        response = self.user2_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 0)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # user1 dislike the comment
        response = self.user1_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 1)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # if user1 dislike the tweet, the tweet num won't change
        response = self.user1_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 0)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # user1 dislike thet tweet
        response = self.user2_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["deleted"], 1)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)

    def test_likes_in_comments_api(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)

        # test anonymous
        anonymous_client = APIClient()
        response = anonymous_client.get(COMMENT_LIST_API, {"tweet_id": tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["comments"][0]["has_liked"], False)
        self.assertEqual(response.data["comments"][0]["likes_count"], 0)

        # test comments list api
        response = self.user2_client.get(COMMENT_LIST_API, {"tweet_id": tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["comments"][0]["has_liked"], False)
        self.assertEqual(response.data["comments"][0]["likes_count"], 0)
        self.create_like(self.user2, comment)
        response = self.user2_client.get(COMMENT_LIST_API, {"tweet_id": tweet.id})
        self.assertEqual(response.data["comments"][0]["has_liked"], True)
        self.assertEqual(response.data["comments"][0]["likes_count"], 1)

        # test tweet detail api
        self.create_like(self.user1, comment)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["comments"][0]["has_liked"], True)
        self.assertEqual(response.data["comments"][0]["likes_count"], 2)

    def test_likes_in_tweets_api(self):
        tweet = self.create_tweet(self.user1)

        # test tweet detail api
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["has_liked"], False)
        self.assertEqual(response.data["likes_count"], 0)
        self.create_like(self.user2, tweet)
        response = self.user2_client.get(url)
        self.assertEqual(response.data["has_liked"], True)
        self.assertEqual(response.data["likes_count"], 1)

        # test tweets list api
        response = self.user2_client.get(TWEET_LIST_API, {"user_id": self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["tweets"][0]["has_liked"], True)
        self.assertEqual(response.data["tweets"][0]["likes_count"], 1)

        # test newsfeeds list api
        self.create_like(self.user1, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["newsfeeds"][0]["tweet"]["has_liked"], True)
        self.assertEqual(response.data["newsfeeds"][0]["tweet"]["likes_count"], 2)

        # test likes details
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(len(response.data["likes"]), 2)
        self.assertEqual(response.data["likes"][0]["user"]["id"], self.user1.id)
        self.assertEqual(response.data["likes"][1]["user"]["id"], self.user2.id)
