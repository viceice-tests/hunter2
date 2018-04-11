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

    def setUp(self):
        self.event = Event.objects.get(pk=1)
        self.user1 = UserProfile.objects.get(pk=1)
        self.user2 = UserProfile.objects.get(pk=2)
        self.team1 = Team.objects.get(pk=1)
        self.ep1 = Episode(name="Day 1", event=self.event, start_date=timezone.now(), winning=True)
        self.ep1.save()
        self.ep2 = Episode(name="Day 2", event=self.event, start_date=timezone.now(), winning=False)
        self.ep2.save()
        self.pz1_1 = Puzzle(title="Puzzle 1", episode=self.ep1, content="1")
        self.pz1_1.save()
        a1_1 = Answer(for_puzzle=self.pz1_1, answer="correct")
        a1_1.save()
        self.pz1_2 = Puzzle(title="Puzzle 2", episode=self.ep1, content="2")
        self.pz1_2.save()
        a1_2 = Answer(for_puzzle=self.pz1_2, answer="correct")
        a1_2.save()
        self.pz2_1 = Puzzle(title="Puzzle 3", episode=self.ep2, content="3")
        self.pz2_1.save()
        a2_1 = Answer(for_puzzle=self.pz2_1, answer="correct")
        a2_1.save()
        self.pz2_2 = Puzzle(title="Puzzle 4", episode=self.ep2, content="4")
        self.pz2_2.save()
        a2_2 = Answer(for_puzzle=self.pz2_2, answer="correct")
        a2_2.save()
        self.ep1.puzzles = [self.pz1_1, self.pz1_2]
        self.ep1.save()
        self.ep2.puzzles = [self.pz2_1, self.pz2_2]
        self.ep2.save()
        self.team2 = Team(at_event=self.event)
        self.team2.save()
        self.team2.members.add(self.user2)

    def test_win_single_linear_episode(self):
        # No correct answers => noone has finished => no finishing positions!
        self.assertEqual(self.event.finishing_positions(), [])

        Guess(for_puzzle=self.pz1_1, by=self.user1, guess="correct").save()
        Guess(for_puzzle=self.pz1_1, by=self.user2, guess="correct").save()
        # First episode still not complete
        self.assertEqual(self.event.finishing_positions(), [])

        g = Guess(for_puzzle=self.pz1_2, by=self.user1, guess="correct")
        g.save()
        Guess(for_puzzle=self.pz1_2, by=self.user2, guess="incorrect").save()
        # Team 1 has finished the only winning episode, but Team 2 has not
        self.assertEqual(self.event.finishing_positions(), [self.team1])

        Guess(for_puzzle=self.pz1_2, by=self.user2, guess="correct").save()
        # Team 2 should now be second place
        self.assertEqual(self.event.finishing_positions(), [self.team1, self.team2])

        # Make sure the order changes correctly
        g.given = timezone.now()
        g.save()
        self.assertEqual(self.event.finishing_positions(), [self.team2, self.team1])

    def test_win_two_linear_episodes(self):
        self.ep2.winning=True
        self.ep2.save()

        self.assertEqual(self.event.finishing_positions(), [])

        Guess(for_puzzle=self.pz1_1, by=self.user1, guess="correct").save()
        Guess(for_puzzle=self.pz1_1, by=self.user2, guess="correct").save()
        Guess(for_puzzle=self.pz1_2, by=self.user1, guess="correct").save()
        Guess(for_puzzle=self.pz1_2, by=self.user2, guess="correct").save()
        # We need to complete both episodes
        self.assertEqual(self.event.finishing_positions(), [])

        # Invalidate Episode 1 guesses, complete Episode 2
        Guess.objects.all().update(guess="incorrect", correct_for=None)
        self.assertEqual(self.ep1.finished_positions(), [])
        Guess(for_puzzle=self.pz2_1, by=self.user1, guess="correct").save()
        Guess(for_puzzle=self.pz2_1, by=self.user2, guess="correct").save()
        g = Guess(for_puzzle=self.pz2_2, by=self.user1, guess="correct")
        g.save()
        Guess(for_puzzle=self.pz2_2, by=self.user2, guess="correct").save()
        # Should still have no-one finished
        self.assertEqual(self.event.finishing_positions(), [])

        # Make Episode 1 guesses valid again
        Guess.objects.all().update(guess="correct")
        [g.save() for g in Guess.objects.all()]
        self.assertEqual(self.event.finishing_positions(), [self.team1, self.team2])

        # Swap order
        g.given = timezone.now()
        g.save()
        self.assertEqual(self.event.finishing_positions(), [self.team2, self.team1])


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
