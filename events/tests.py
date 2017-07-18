# vim: set fileencoding=utf-8 :
from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

from events.management.commands import createdefaultevent
from events.models import Event, Theme
from hunter2.tests import MockTTY, mock_inputs


class CreateDefaultEventManagementCommandTests(TestCase):
    TEST_EVENT_NAME = "Custom Event"
    TEST_THEME_NAME = "Custom Theme"

    def test_no_event_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --theme and --event with --noinput."):
            call_command('createdefaultevent', interactive=False, theme_name="Test Theme", stdout=output)

    def test_no_theme_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --theme and --event with --noinput."):
            call_command('createdefaultevent', interactive=False, event_name="Test Event", stdout=output)

    def test_non_interactive_usage(self):
        output = StringIO()
        call_command(
            'createdefaultevent',
            interactive=False,
            event_name=self.TEST_EVENT_NAME,
            theme_name=self.TEST_THEME_NAME,
            stdout=output
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            self.TEST_EVENT_NAME,
            self.TEST_THEME_NAME
        ))

        theme = Theme.objects.get(name=self.TEST_THEME_NAME)
        self.assertIsNotNone(theme)
        event = Event.objects.get(name=self.TEST_EVENT_NAME, theme=theme, current=True)
        self.assertIsNotNone(event)

    @mock_inputs({
        'event': TEST_EVENT_NAME,
        'theme': TEST_THEME_NAME
    })
    def test_interactive_usage(self):
        output = StringIO()
        call_command(
            'createdefaultevent',
            interactive=True,
            stdout=output,
            stdin=MockTTY(),
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            self.TEST_EVENT_NAME,
            self.TEST_THEME_NAME
        ))

        theme = Theme.objects.get(name=self.TEST_THEME_NAME)
        self.assertIsNotNone(theme)
        event = Event.objects.get(name=self.TEST_EVENT_NAME, theme=theme.id, current=True)
        self.assertIsNotNone(event)

    @mock_inputs({
        'event': "",
        'theme': ""
    })
    def test_default_interactive_usage(self):
        output = StringIO()
        call_command(
            'createdefaultevent',
            interactive=True,
            stdout=output,
            stdin=MockTTY(),
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            createdefaultevent.Command.DEFAULT_EVENT_NAME,
            createdefaultevent.Command.DEFAULT_THEME_NAME
        ))

        theme = Theme.objects.get(name=createdefaultevent.Command.DEFAULT_THEME_NAME)
        self.assertIsNotNone(theme)
        event = Event.objects.get(name=createdefaultevent.Command.DEFAULT_EVENT_NAME, theme=theme.id, current=True)
        self.assertIsNotNone(event)

    def test_only_one_current_event(self):
        output = StringIO()
        call_command(
            'createdefaultevent',
            interactive=False,
            event_name=self.TEST_EVENT_NAME + "1",
            theme_name=self.TEST_THEME_NAME + "1",
            stdout=output
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            self.TEST_EVENT_NAME + "1",
            self.TEST_THEME_NAME + "1"
        ))

        output = StringIO()
        call_command(
            'createdefaultevent',
            interactive=False,
            event_name=self.TEST_EVENT_NAME + "2",
            theme_name=self.TEST_THEME_NAME + "2",
            stdout=output
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            self.TEST_EVENT_NAME + "2",
            self.TEST_THEME_NAME + "2"
        ))

        self.assertGreater(Event.objects.all().count(), 1)
        self.assertEqual(Event.objects.filter(current=True).count(), 1, "More than a single event with current set as True")
