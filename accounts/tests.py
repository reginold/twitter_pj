from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):
    def setUp(self):
        self.clear_cache()

    def test_profile_property(self):
        user1 = self.create_user("user1", "user1@sampl.com")
        self.assertEqual(UserProfile.objects.count(), 3)
        profile = user1.profile
        self.assertEqual(isinstance(profile, UserProfile), True)
