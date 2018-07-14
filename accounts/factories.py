import unicodedata

import factory
import pytz
from django.contrib.auth.models import User


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.UserProfile'

    # We pass in profile=None to prevent UserFactory from creating another profile
    # (this disables the RelatedFactory)
    user = factory.SubFactory('accounts.factories.UserFactory', profile=None)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGeneration(lambda user, create, extracted: user.set_password(extracted or factory.Faker('password').generate({})))

    # Fixed values, can be overridden manually on creation.
    is_active = True
    is_staff = False
    is_superuser = False

    # Joined in the last month but more recent last_login.
    date_joined = factory.Faker('date_time_this_month', tzinfo=pytz.utc)
    last_login = factory.LazyAttribute(lambda o: factory.Faker('date_time_between_dates', datetime_start=o.date_joined, tzinfo=pytz.utc).generate({}))

    # We pass in 'user' to link the generated Profile to our just-generated User
    # This will call UserProfileFactory(user=our_new_user), thus skipping the SubFactory.
    profile = factory.RelatedFactory(UserProfileFactory, 'user')

    @factory.lazy_attribute_sequence
    def username(self, n):
        if self.first_name and self.last_name:
            first_letter = (unicodedata.normalize('NFKD', self.first_name).encode('ascii', 'ignore').decode('utf8'))[:1]
            last_name = (unicodedata.normalize('NFKD', self.last_name).encode('ascii', 'ignore').decode('utf8'))[:9]
            return '{0}{1}{2}'.format(first_letter, last_name, n)
        else:
            return factory.Faker('user_name')

    @factory.lazy_attribute_sequence
    def email(self, n):
        if self.first_name and self.last_name:
            first_letter = (unicodedata.normalize('NFKD', self.first_name).encode('ascii', 'ignore').decode('utf8'))[:1]
            last_name = (unicodedata.normalize('NFKD', self.last_name).encode('ascii', 'ignore').decode('utf8'))[:9]
            return '{0}.{1}{2}@'.format(first_letter, last_name, n, factory.Faker('free_email_domain'))
        else:
            return factory.Faker('ascii_safe_email')
