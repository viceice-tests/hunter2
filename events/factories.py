import factory

from faker import Faker
from faker.providers import BaseProvider


class SchemaNameProvider(BaseProvider):
    def schema_name(self,):
        name = self.generator.format('domain_word')
        name = name.replace('-', '')
        return name


factory.Faker.add_provider(SchemaNameProvider)


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'sites.Site'
        django_get_or_create = ('domain', 'name')
        exclude = ('fake', )

    fake = Faker()

    domain = fake.domain_name
    name = fake.company


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.Theme'
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'Test Theme %d' % n)


class DomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.Domain'
        django_get_or_create = ('domain', )
        exclude = ('site', 'subdomain')

    site = factory.SubFactory(SiteFactory)
    subdomain = factory.Faker('schema_name')

    domain = factory.LazyAttribute(lambda o: f'{o.subdomain}.{o.site.domain}')


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.Event'

    name = factory.Sequence(lambda n: 'Test Event %d' % n)
    schema_name = factory.Faker('schema_name')
    theme = factory.SubFactory(ThemeFactory)
    current = False
    about_text = factory.Faker('text')
    rules_text = factory.Faker('text')
    help_text = factory.Faker('text')
    examples_text = factory.Faker('text')
    max_team_size = factory.Faker('random_int', min=0, max=10)

    domain = factory.RelatedFactory(DomainFactory, 'tenant', subdomain=schema_name)


class EventFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'events.EventFile'
        django_get_or_create = ('event', 'slug')

    event = factory.SubFactory(EventFactory)
    slug = factory.Faker('slug')
    file = factory.django.FileField(
        filename=factory.Faker('file_name'),
        data=factory.Faker('binary', length=factory.Faker('random-int', min=1, max=1048576))
    )
