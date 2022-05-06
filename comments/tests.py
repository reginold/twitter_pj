from testing.testcases import TestCase


class CommentModelTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user("user1", "user1@gmail.com")
        self.tweet = self.create_tweet(self.user1)
        self.comment = self.create_comment(self.user1, self.tweet)

    def test_comment(self):
        user = self.create_user("testUser", email="test@gmail.com")
        tweet = self.create_tweet(user)
        comment = self.create_comment(user, tweet)
        self.assertNotEqual(comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.user1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.user1, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        user2 = self.create_user("user2", "user2@gmail.com")
        self.create_like(user2, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)
