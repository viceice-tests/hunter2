# vim: set fileencoding=utf-8 :
import sys

from django.core.management import BaseCommand, CommandError

from events.models import Event, Theme


# Based on createsuperuser:
# https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
class Command(BaseCommand):
    help = 'Creates a default development event and associated theme'

    DEFAULT_EVENT_NAME = "Development Event"
    DEFAULT_THEME_NAME = "Development Theme"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            '--theme',
            dest='theme_name',
            type=str,
            help="Name for the theme",
            default=None,
        )
        parser.add_argument(
            '--event',
            dest='event_name',
            type=str,
            help="Name for the event",
            default=None,
        )
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help=(
                "Tells Django to NOT prompt the user for input of any kind. "
                "You must use --theme and --event with --noinput."
            ),
        )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        theme_name = options['theme_name']
        event_name = options['event_name']

        if not options['interactive']:
            if not theme_name or not event_name:
                raise CommandError("You must use --theme and --event with --noinput.")

        while theme_name is None:
            theme_name = self.get_input_data("Theme name", default=self.DEFAULT_THEME_NAME)

        while event_name is None:
            event_name = self.get_input_data("Event name", default=self.DEFAULT_EVENT_NAME)

        theme = Theme(name=theme_name)
        theme.save()
        event = Event(name=event_name, theme=theme, current=True)
        event.save()

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
