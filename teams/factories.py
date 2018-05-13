import collections

import factory

from events import factories


class TeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'teams.Team'

    name = factory.Faker('color_name')
    at_event = factory.SubFactory(factories.EventFactory)
    is_admin = False

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in (extracted if isinstance(extracted, collections.Iterable) else (extracted,)):
                self.members.add(member)
