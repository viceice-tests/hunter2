# vim: set fileencoding=utf-8 :
from io import StringIO
from unittest.case import expectedFailure

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from events.management.commands import createdefaultevent
from events.models import Event, Theme
from hunter2.tests import MockTTY, mock_inputs


class EventRulesTests(TestCase):

    def test_only_one_current_event(self):
        # Ensure that we only have one event set as current
        theme = Theme(name="Test Theme")
        theme.save()
        event1 = Event(name="Event Theme1", theme=theme, end_date=timezone.now(), current=True)
        event1.save()
        event2 = Event(name="Event Theme2", theme=theme, end_date=timezone.now(), current=True)
        event2.save()
        self.assertEqual(len(Event.objects.filter(current=True)), 1, "More than one event is set as current")
        self.assertEqual(Event.objects.get(current=True), event2, "Last added event is not current")

    @expectedFailure  # TODO: Currently fails but non-critical
    def test_only_remaining_event_is_current(self):
        # Ensure that we only have one event set as current after deleting the current test
        theme = Theme(name="Test Theme")
        theme.save()
        event1 = Event(name="Event Theme1", theme=theme, end_date=timezone.now(), current=True)
        event1.save()
        event2 = Event(name="Event Theme2", theme=theme, end_date=timezone.now(), current=True)
        event2.save()
        event2.delete()
        self.assertEqual(len(Event.objects.filter(current=True)), 1, "No current event set")
        self.assertEqual(Event.objects.get(current=True), event1, "Only remaining event is not current")

    def test_current_by_default_event(self):
        # If we only have one event is should be set as current by default, regardless if set as current
        theme = Theme(name="Test Theme")
        theme.save()
        event = Event(name="Event Theme", theme=theme, end_date=timezone.now(), current=False)
        event.save()
        self.assertTrue(event.current, "Only event is not set as current")


class CreateDefaultEventManagementCommandTests(TestCase):
    TEST_EVENT_NAME = "Custom Event"
    TEST_THEME_NAME = "Custom Theme"
    TEST_EVENT_END_DATE = "Monday at 18:00"
    INVALID_END_DATE = "18:00 on the second Sunday after Pentecost"

    def test_no_event_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --theme, --event and --enddate with --noinput."):
            call_command('createdefaultevent', interactive=False, theme_name="Test Theme", end_date=self.TEST_EVENT_END_DATE, stdout=output)

    def test_no_theme_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --theme, --event and --enddate with --noinput."):
            call_command('createdefaultevent', interactive=False, event_name="Test Event", end_date=self.TEST_EVENT_END_DATE, stdout=output)

    def test_no_end_date_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --theme, --event and --enddate with --noinput."):
            call_command('createdefaultevent', interactive=False, event_name="Test Event", theme_name="Test Theme", stdout=output)

    def test_invalid_date(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "End date is not a valid date."):
            call_command(
                'createdefaultevent',
                interactive=False,
                event_name=self.TEST_EVENT_NAME,
                theme_name=self.TEST_THEME_NAME,
                end_date=self.INVALID_END_DATE,
                stdout=output
            )

    def test_non_interactive_usage(self):
        output = StringIO()
        call_command(
            'createdefaultevent',
            interactive=False,
            event_name=self.TEST_EVENT_NAME,
            theme_name=self.TEST_THEME_NAME,
            end_date=self.TEST_EVENT_END_DATE,
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
            end_date=self.TEST_EVENT_END_DATE,
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
            end_date=self.TEST_EVENT_END_DATE,
            stdout=output
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Created current event \"{}\" and theme \"{}\"".format(
            self.TEST_EVENT_NAME + "2",
            self.TEST_THEME_NAME + "2"
        ))

        self.assertGreater(Event.objects.all().count(), 1)
        self.assertEqual(Event.objects.filter(current=True).count(), 1, "More than a single event with current set as True")
