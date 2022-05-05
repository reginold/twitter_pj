from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_URL = "/api/comments/"


class CommentApiTests(TestCase):
    def setUp(self):
        self.linghu = self.create_user("linghu", email="test1@gmail.com")
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)
        self.dongxie = self.create_user("dongxie", email="test2@gmail.com")
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        self.tweet = self.create_tweet(self.linghu)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 啥参数都没带不行
        response = self.linghu_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id 不行
        response = self.linghu_client.post(COMMENT_URL, {"tweet_id": self.tweet.id})
        self.assertEqual(response.status_code, 400)

        # 只带 content 不行
        response = self.linghu_client.post(COMMENT_URL, {"content": "1"})
        self.assertEqual(response.status_code, 400)

        # content 太长不行
        response = self.linghu_client.post(
            COMMENT_URL,
            {
                "tweet_id": self.tweet.id,
                "content": "1" * 141,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual("content" in response.data["errors"], True)

        # tweet_id 和 content 都带才行
        response = self.linghu_client.post(
            COMMENT_URL,
            {
                "tweet_id": self.tweet.id,
                "content": "1",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["id"], self.linghu.id)
        self.assertEqual(response.data["tweet_id"], self.tweet.id)
        self.assertEqual(response.data["content"], "1")

    def test_destroy(self):
        comment = self.create_comment(self.linghu, self.tweet)
        url = "{}{}/".format(COMMENT_URL, comment.id)

        # 匿名不可以删除
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 非本人不能删除
        response = self.dongxie_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 本人可以删除
        count = Comment.objects.count()
        response = self.linghu_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.linghu, self.tweet, "original")
        another_tweet = self.create_tweet(self.dongxie)
        url = "{}{}/".format(COMMENT_URL, comment.id)

        # 使用 put 的情况下
        # 匿名不可以更新
        response = self.anonymous_client.put(url, {"content": "new"})
        self.assertEqual(response.status_code, 403)
        # 非本人不能更新
        response = self.dongxie_client.put(url, {"content": "new"})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, "new")
        # 不能更新除 content 外的内容，静默处理，只更新内容
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.linghu_client.put(
            url,
            {
                "content": "new",
                "user_id": self.dongxie.id,
                "tweet_id": another_tweet.id,
                "created_at": now,
            },
        )
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, "new")
        self.assertEqual(comment.user, self.linghu)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_list(self):
        # tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # no comment by tweet_id
        response = self.anonymous_client.get(
            COMMENT_URL,
            {
                "tweet_id": self.tweet.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["comments"]), 0)

        # comments filterd by date
        self.create_comment(self.linghu, self.tweet, "1")
        self.create_comment(self.dongxie, self.tweet, "2")
        self.create_comment(self.dongxie, self.create_tweet(self.dongxie), "3")  # type: ignore
        response = self.anonymous_client.get(
            COMMENT_URL,
            {
                "tweet_id": self.tweet.id,
            },
        )
        self.assertEqual(len(response.data["comments"]), 2)
        self.assertEqual(response.data["comments"][0]["content"], "1")
        self.assertEqual(response.data["comments"][1]["content"], "2")

        # if user_id and tweet_id were both filterd, only tweet_id can be filterd
        response = self.anonymous_client.get(
            COMMENT_URL,
            {
                "tweet_id": self.tweet.id,
                "user_id": self.linghu.id,
            },
        )
        self.assertEqual(len(response.data["comments"]), 2)