import collections

import factory
from faker import Faker

from accounts.factories import UserProfileFactory
from events import factories


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'teams.Team'

    name = factory.Sequence(lambda n: f'{n}{Faker().color_name()}')
    at_event = factory.SubFactory(factories.EventFactory)
    is_admin = False

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in (extracted if isinstance(extracted, collections.Iterable) else (extracted,)):
                self.members.add(member)

class TeamMemberFactory(UserProfileFactory):
    class Meta:
        exclude = ('team',)

    team = factory.RelatedFactory(TeamFactory, 'members')
