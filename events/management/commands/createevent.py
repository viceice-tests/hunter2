# vim: set fileencoding=utf-8 :
import sys

from django.core.management import BaseCommand, CommandError
from django.contrib.sites.models import Site

from ...models import Domain, Event, Theme


# Based on createsuperuser:
# https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
class Command(BaseCommand):
    help = 'Creates an event and associated theme, tenant and domain'

    DEFAULT_EVENT_NAME = "Development Event"
    DEFAULT_THEME_NAME = "Development Theme"
    DEFAULT_SUBDOMAIN = "dev"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            '--event',
            dest='event_name',
            type=str,
            help="Name for the event",
            default=None,
        )
        parser.add_argument(
            '--theme',
            dest='theme_name',
            type=str,
            help="Name for the theme",
            default=None,
        )
        parser.add_argument(
            '--subdomain',
            dest='subdomain',
            type=str,
            help="Subdomain for the event",
            default=None,
        )
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help=(
                "Tells Django to NOT prompt the user for input of any kind. "
                "You must use --event, --subdomain and --theme with --noinput."
            ),
        )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        event_name = options['event_name']
        theme_name = options['theme_name']
        subdomain = options['subdomain']

        if not options['interactive']:
            if not theme_name or not event_name:
                raise CommandError("You must use --event, --subdomain and --theme with --noinput.")

        while event_name is None:
            event_name = self.get_input_data("Event name", default=self.DEFAULT_EVENT_NAME)

        while theme_name is None:
            theme_name = self.get_input_data("Theme name", default=self.DEFAULT_THEME_NAME)

        while subdomain is None:
            subdomain = self.get_input_data("Subdomain", default=self.DEFAULT_SUBDOMAIN)

        site_domain = Site.objects.get().domain
        theme = Theme(name=theme_name)
        theme.save()
        event = Event(name=event_name, schema_name=subdomain, theme=theme, current=True)
        event.save()
        domain = Domain(domain='.'.join([subdomain, site_domain]), tenant=event)
        domain.save()

        self.stdout.write("Created current event \"{}\" and theme \"{}\"".format(event_name, theme_name))

    @staticmethod
    def get_input_data(field, default=None):
        if default:
            message = "{} (leave blank to use \'{}\'): ".format(field, default)
        else:
            message = "{}:".format(field)
        value = input(message)
        if default and value == '':
            value = default
        return value
