from testing.testcases import TestCase

LIKE_BASE_URL = "/api/likes/"
LIKE_CANCEL_URL = "/api/likes/cancel/"


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
