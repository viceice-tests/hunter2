import collections
import json
from datetime import timedelta
from random import choice

import factory
import pytz
from faker import Faker

from accounts.factories import UserProfileFactory
from events.factories import EventFactory
from teams.factories import TeamFactory
from .models import AnnouncementType
from .runtimes.registry import RuntimesRegistry as rr


class PuzzleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Puzzle'

    title = factory.Faker('sentence')
    flavour = factory.Faker('text')

    runtime = rr.STATIC
    content = factory.Faker('text')

    cb_runtime = rr.STATIC
    cb_content = ""

    start_date = factory.Faker('date_time_this_month', tzinfo=pytz.utc)
    headstart_granted = factory.Faker('time_delta', end_datetime=timedelta(minutes=60))

    # This puzzle needs to be part of an episode
    episode_set = factory.RelatedFactory('hunts.factories.EpisodeFactory', 'puzzles')


class PuzzleFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.PuzzleFile'
        django_get_or_create = ('puzzle', 'slug')

    puzzle = factory.SubFactory(PuzzleFactory)
    slug = factory.Faker('slug')
    file = factory.django.FileField(
        filename=factory.Faker('file_name'),
        data=factory.Faker('binary')
    )


class HintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Hint'

    puzzle = factory.SubFactory(PuzzleFactory)
    text = factory.Faker('sentence')
    time = factory.Faker('time_delta', end_datetime=timedelta(minutes=60))


class UnlockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Unlock'

    puzzle = factory.SubFactory(PuzzleFactory)
    text = factory.Faker('sentence')


class UnlockAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.UnlockAnswer'

    unlock = factory.SubFactory(UnlockFactory)
    runtime = rr.STATIC
    guess = factory.Faker('word')


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Answer'

    for_puzzle = factory.SubFactory(PuzzleFactory)
    runtime = rr.STATIC
    answer = factory.Faker('word')


class GuessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Guess'
        exclude = ('update_team',)

    by = factory.SubFactory(UserProfileFactory)
    by_team = factory.SubFactory(TeamFactory)
    for_puzzle = factory.SubFactory(PuzzleFactory)
    guess = factory.Faker('sentence')
    given = factory.Faker('date_time_this_month', tzinfo=pytz.utc)

    # by_team, correct_for and correct_current are all handled internally.

    @factory.post_generation
    def update_team(obj, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        # A Guess can only be made by a User who is on a Team at an Event.
        # We need to ensure that there is this consistency:
        # UserProfile(by) <-> Team <-> Event <-> Episode <-> Puzzle(for_puzzle)
        # TODO: This is a hack as it creates an orphan team from the original declaration.
        obj.by_team = TeamFactory(at_event=obj.for_puzzle.episode_set.get().event, members=obj.by)


class DataFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    data = factory.LazyFunction(lambda: json.dumps(Faker().pydict(
        10,
        True,
        'str', 'str', 'str', 'str', 'float', 'int', 'int',
    )))


class TeamDataFactory(DataFactory):
    class Meta:
        model = 'hunts.TeamData'

    team = factory.SubFactory(TeamFactory)


class UserDataFactory(DataFactory):
    class Meta:
        model = 'hunts.UserData'
        django_get_or_create = ('event', 'user')

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserProfileFactory)


class TeamPuzzleDataFactory(DataFactory):
    class Meta:
        model = 'hunts.TeamPuzzleData'
        django_get_or_create = ('puzzle', 'team')

    puzzle = factory.SubFactory(PuzzleFactory)
    team = factory.SubFactory(TeamFactory)
    start_time = factory.Faker('date_time_this_month', tzinfo=pytz.utc)


class UserPuzzleDataFactory(DataFactory):
    class Meta:
        model = 'hunts.UserPuzzleData'
        django_get_or_create = ('puzzle', 'user')

    puzzle = factory.SubFactory(PuzzleFactory)
    user = factory.SubFactory(UserProfileFactory)
    token = factory.Faker('uuid4')


class EpisodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Episode'

    name = factory.Faker('sentence')
    flavour = factory.Faker('text')
    start_date = factory.Faker('date_time_this_month', tzinfo=pytz.utc)
    event = factory.SubFactory(EventFactory)
    parallel = factory.Faker('boolean')

    @factory.post_generation
    def puzzles(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of puzzles were passed in, use them
            for puzzle in (extracted if isinstance(extracted, collections.Iterable) else (extracted,)):
                self.puzzles.add(puzzle)

    @factory.post_generation
    def prequels(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of prequels were passed in, use them
            for prequel in (extracted if isinstance(extracted, collections.Iterable) else (extracted,)):
                self.prequels.add(prequel)

    @factory.post_generation
    def headstart_from(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of  puzzles were passed in, use them
            for puzzle in (extracted if isinstance(extracted, collections.Iterable) else (extracted,)):
                self.headstart_from.add(puzzle)


class AnnouncementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'hunts.Announcement'

    event = factory.SubFactory(EventFactory)
    puzzle = factory.SubFactory(PuzzleFactory)  # TODO: Generate without puzzle as well.
    title = factory.Faker('sentence')
    posted = factory.Faker('date_time_this_month', tzinfo=pytz.utc)
    message = factory.Faker('text')
    type = factory.LazyFunction(lambda: choice(list(AnnouncementType)))
