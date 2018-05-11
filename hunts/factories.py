from datetime import timedelta

import pytz

from .runtimes.registry import RuntimesRegistry as rr

import factory


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
