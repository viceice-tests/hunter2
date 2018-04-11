# vim: set fileencoding=utf-8 :
from io import StringIO
from unittest.case import expectedFailure

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.utils import timezone

from events.management.commands import createdefaultevent
from events.models import Event, Theme
from hunter2.tests import MockTTY, mock_inputs
from hunts.models import Episode, Puzzle, Answer, Guess
from teams.models import UserProfile, Team


class EventRulesTests(TestCase):

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


class EventWinningTests(TestCase):
    fixtures = ["teams_test"]

    def test_win_two_day_event(self):
        event = Event.objects.get(pk=1)
        user1 = UserProfile.objects.get(pk=1)
        user2 = UserProfile.objects.get(pk=2)
        team1 = Team.objects.get(pk=1)
        ep1 = Episode(name="Day 1", event=event, start_date=timezone.now(), winning=True)
        ep1.save()
        ep2 = Episode(name="Day 2", event=event, start_date=timezone.now(), winning=True)
        ep2.save()
        pz1_1 = Puzzle(title="Puzzle 1", episode=ep1, content="1")
        pz1_1.save()
        a1_1 = Answer(for_puzzle=pz1_1, answer="correct")
        a1_1.save()
        pz1_2 = Puzzle(title="Puzzle 2", episode=ep1, content="2")
        pz1_2.save()
        a1_2 = Answer(for_puzzle=pz1_2, answer="correct")
        a1_2.save()
        pz2_1 = Puzzle(title="Puzzle 3", episode=ep2, content="3")
        pz2_1.save()
        a2_1 = Answer(for_puzzle=pz2_1, answer="correct")
        a2_1.save()
        pz2_2 = Puzzle(title="Puzzle 4", episode=ep2, content="4")
        pz2_2.save()
        a2_2 = Answer(for_puzzle=pz2_2, answer="correct")
        a2_2.save()
        team2 = Team(at_event=event)
        team2.save()
        team2.members.add(user2)

        # No correct answers => noone has finished => no finishing positions!
        self.assertEqual(event.finishing_positions(), [])
        self.assertEqual(event.team_finishing_position(team1), None)
        self.assertEqual(event.team_finishing_position(team2), None)


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
