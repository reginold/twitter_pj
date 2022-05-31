from testing.testcases import TestCase

from accounts.models import UserProfile


class UserProfileTests(TestCase):
    def test_profile_property(self):
        user1 = self.create_user("user1", "user1@sampl.com")
        self.assertEqual(UserProfile.objects.count(), 0)
        profile = user1.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
