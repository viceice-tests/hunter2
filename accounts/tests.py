from django.test import TestCase

from accounts.factories import UserProfileFactory


class FactoryTests(TestCase):

    def test_user_profile_factory_default_construction(self):
        UserProfileFactory.create()
