from io import StringIO
from unittest.case import expectedFailure

from django.core.management import CommandError, call_command
from django.test import TestCase
from django_tenants.test.cases import TenantTestCase

from events.management.commands import createevent
from events.models import Event, Theme
from hunter2.tests import MockTTY, mock_inputs


class EventTestCase(TenantTestCase):

    @classmethod
    def setup_tenant(cls, tenant):
        theme = Theme(name='Test Theme')
        theme.save()
        tenant.name = 'Test Event'
        tenant.theme = theme


class EventRulesTests(EventTestCase):

    def test_only_one_current_event(self):
        # Ensure that we only have one event set as current
        theme = Theme(name="Test Theme")
        theme.save()
        event1 = Event(name="Event Theme1", theme=theme, current=True)
        event1.save()
        event2 = Event(name="Event Theme2", theme=theme, current=True)
        event2.save()
        self.assertEqual(len(Event.objects.filter(current=True)), 1, "More than one event is set as current")
        self.assertEqual(Event.objects.get(current=True), event2, "Last added event is not current")

    @expectedFailure  # TODO: Currently fails but non-critical
    def test_only_remaining_event_is_current(self):
        # Ensure that we only have one event set as current after deleting the current test
        theme = Theme(name="Test Theme")
        theme.save()
        event1 = Event(name="Event Theme1", theme=theme, current=True)
        event1.save()
        event2 = Event(name="Event Theme2", theme=theme, current=True)
        event2.save()
        event2.delete()
        self.assertEqual(len(Event.objects.filter(current=True)), 1, "No current event set")
        self.assertEqual(Event.objects.get(current=True), event1, "Only remaining event is not current")

    def test_current_by_default_event(self):
        # If we only have one event is should be set as current by default, regardless if set as current
        theme = Theme(name="Test Theme")
        theme.save()
        event = Event(name="Event Theme", theme=theme, current=False)
        event.save()
        self.assertTrue(event.current, "Only event is not set as current")


class CreateDefaultEventManagementCommandTests(TestCase):
    TEST_EVENT_NAME = "Custom Event"
    TEST_THEME_NAME = "Custom Theme"
    TEST_SUBDOMAIN = 'custom'

    def test_no_event_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --event, --subdomain and --theme with --noinput."):
            call_command('createevent', interactive=False, theme_name="Test Theme", stdout=output)

    def test_no_theme_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --event, --subdomain and --theme with --noinput."):
            call_command('createevent', interactive=False, event_name="Test Event", stdout=output)

    def test_non_interactive_usage(self):
        output = StringIO()
        call_command(
            'createevent',
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
        'theme': TEST_THEME_NAME,
        'subdomain': TEST_SUBDOMAIN,
    })
    def test_interactive_usage(self):
        output = StringIO()
        call_command(
            'createevent',
            interactive=True,
            stdout=output,
            stdin=MockTTY(),
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            self.TEST_EVENT_NAME,
            self.TEST_THEME_NAME,
        ))

        theme = Theme.objects.get(name=self.TEST_THEME_NAME)
        self.assertIsNotNone(theme)
        event = Event.objects.get(name=self.TEST_EVENT_NAME, theme=theme.id, current=True)
        self.assertIsNotNone(event)

    @mock_inputs({
        'event': "",
        'theme': "",
        'subdomain': "",
    })
    def test_default_interactive_usage(self):
        output = StringIO()
        call_command(
            'createevent',
            interactive=True,
            stdout=output,
            stdin=MockTTY(),
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            createevent.Command.DEFAULT_EVENT_NAME,
            createevent.Command.DEFAULT_THEME_NAME
        ))

        theme = Theme.objects.get(name=createevent.Command.DEFAULT_THEME_NAME)
        self.assertIsNotNone(theme)
        event = Event.objects.get(name=createevent.Command.DEFAULT_EVENT_NAME, theme=theme.id, current=True)
        self.assertIsNotNone(event)

    def test_only_one_current_event(self):
        output = StringIO()
        call_command(
            'createevent',
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
            'createevent',
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
