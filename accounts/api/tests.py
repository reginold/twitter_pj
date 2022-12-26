from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from accounts.models import UserProfile
from testing.testcases import TestCase

LOGIN_URL = "/api/accounts/login/"
LOGOUT_URL = "/api/accounts/logout/"
SIGNUP_URL = "/api/accounts/signup/"
LOGIN_STATUS_URL = "/api/accounts/login_status/"
USER_PROFILE_DETAIL_URL = "/api/profiles/{}/"


class AccountApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        self.client = APIClient()
        self.user = self.create_user(
            username="someone",
            email="admin@twitter.com",
            password="correct password",
        )

    def test_login(self):
        # use the get instead of post, return 405
        response = self.client.get(
            LOGIN_URL,
            {
                "username": self.user.username,
                "password": "correct password",
            },
        )

        self.assertEqual(response.status_code, 405)

        # use the post but get the wrong password
        response = self.client.post(
            LOGIN_URL,
            {
                "username": self.user.username,
                "password": "wrong password",
            },
        )

        self.assertEqual(response.status_code, 400)

        # use the wrong password return False
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], False)

        # user the right password return true
        response = self.client.post(
            LOGIN_URL,
            {
                "username": self.user.username,
                "password": "correct password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data["user"], None)
        self.assertEqual(response.data["user"]["id"], self.user.id)

        # verify the has_logged_in return code
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True)

    def test_logout(self):
        # Log in first
        self.client.post(
            LOGIN_URL,
            {
                "username": self.user.username,
                "password": "correct password",
            },
        )

        # verify the has_logged_in return code
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True)

        # return false when use get
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # return true when use post
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # verify the log out successful
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], False)

    def test_signup(self):
        data = {
            "username": "someone123",
            "email": "someone@twitter.com",
            "password": "someone",
        }

        # verify the get method , return false
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # verify the wrong mail address
        response = self.client.post(
            SIGNUP_URL,
            {
                "username": "someone",
                "email": "not a correct email",
                "password": "someone",
            },
        )

        self.assertEqual(response.status_code, 400)

        # verify the length of password is too short
        response = self.client.post(
            SIGNUP_URL,
            {
                "username": "someone",
                "email": "someone@twitter.com",
                "password": "123",
            },
        )

        self.assertEqual(response.status_code, 400)

        # verify the length of username is too long
        response = self.client.post(
            SIGNUP_URL,
            {
                "username": "username is toooooooooooo longggggggg",
                "email": "someone@twitter.com",
                "password": "any password",
            },
        )

        self.assertEqual(response.status_code, 400)

        # verfiy the successful sign up
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["username"], "someone123")
        # verify user profile was created
        created_user_id = response.data["user"]["id"]
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data["has_logged_in"], True)


class UserProfileAPITest(TestCase):
    def test_update(self):
        """test the profile can only be updated by himself"""
        user1, user1_client = self.create_user_and_client("user1", "user1@sample.com")
        profile = user1.profile
        profile.nickname = "old nickname"
        profile.save()
        url = USER_PROFILE_DETAIL_URL.format(profile.id)

        # anonymous user cannot update the avatar
        response = self.anonymous_client.put(
            url,
            {
                "nickname": "a new nickname",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )

        _, user2_client = self.create_user_and_client("user2", "user2@sample.com")
        response = user2_client.put(
            url,
            {
                "nickname": "a new nickname",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "You dont have permission to access this object"
        )
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, "old nickname")

        # after updated nickname
        response = user1_client.put(
            url,
            {
                "nickname": "a new nickname",
            },
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, "a new nickname")

        # after updated avatar
        response = user1_client.put(
            url,
            {
                "avatar": SimpleUploadedFile(
                    name="my-avatar.jpg",
                    content=str.encode("a fake image"),
                    content_type="image/jpeg",
                ),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual("my-avatar" in response.data["avatar"], True)
        profile.refresh_from_db()
        self.assertIsNotNone(profile.avatar)
