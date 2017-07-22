# vim: set fileencoding=utf-8 :
import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from teams.models import Team, UserProfile
from .models import Answer, Guess, Hint, Puzzle, PuzzleData, TeamPuzzleData, Unlock, Episode
from .runtimes.registry import RuntimesRegistry as rr


class AnswerValidationTests(TestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        self.puzzle = Puzzle.objects.get(pk=1)
        self.team = Team.objects.get(pk=1)
        self.data = PuzzleData(self.puzzle, self.team)

    def test_static_answers(self):
        answer = Answer.objects.get(for_puzzle=self.puzzle, runtime=rr.STATIC)
        guess = Guess.objects.filter(guess='correct', for_puzzle=self.puzzle).get()
        self.assertTrue(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='correctnot', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='incorrect', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='wrong', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))

    def test_regex_answers(self):
        answer = Answer.objects.get(for_puzzle=self.puzzle, runtime=rr.REGEX)
        guess = Guess.objects.filter(guess='correct', for_puzzle=self.puzzle).get()
        self.assertTrue(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='correctnot', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='incorrect', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='wrong', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))

    def test_lua_answers(self):
        answer = Answer.objects.get(for_puzzle=self.puzzle, runtime=rr.LUA)
        guess = Guess.objects.filter(guess='correct', for_puzzle=self.puzzle).get()
        self.assertTrue(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='correctnot', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='incorrect', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))
        guess = Guess.objects.filter(guess='wrong', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess, self.data))


class PuzzleStartTimeTests(TestCase):
    fixtures = ['hunts_test']

    def test_start_times(self):
        self.assertTrue(self.client.login(username='test', password='hunter2'))
        response = self.client.get('/event/1/ep/1/pz/1/', HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)
        first_time = TeamPuzzleData.objects.get().start_time
        self.assertIsNot(first_time, None)
        response = self.client.get('/event/1/ep/1/pz/1/', HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)
        second_time = TeamPuzzleData.objects.get().start_time
        self.assertEqual(first_time, second_time)


class EpisodeBehaviourTest(TestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        self.linear_episode = Episode.objects.get(pk=1)
        self.parallel_episode = Episode.objects.get(pk=2)
        self.team = Team.objects.get(pk=1)
        self.user = self.team.members.get(pk=1)

    def test_episode_behaviour(self):
        self.linear_episodes_are_linear()
        self.can_see_all_parallel_puzzles()

    def linear_episodes_are_linear(self):
        self.assertTrue(self.linear_episode.unlocked_by(self.team))
        self.assertFalse(self.linear_episode.parallel)
        self.assertTrue(self.linear_episode.get_puzzle(1).unlocked_by(self.team))
        self.assertTrue(self.linear_episode.get_puzzle(2).unlocked_by(self.team))
        self.assertFalse(self.linear_episode.get_puzzle(3).unlocked_by(self.team))
        self.assertFalse(self.linear_episode.get_puzzle(2).answered_by(self.team))

        Guess(for_puzzle=self.linear_episode.get_puzzle(2), by=self.user, guess="correct").save()
        self.assertTrue(self.linear_episode.get_puzzle(2).answered_by(self.team))
        self.assertTrue(self.linear_episode.get_puzzle(3).unlocked_by(self.team))
        self.assertFalse(self.linear_episode.get_puzzle(3).answered_by(self.team))

        Guess(for_puzzle=self.linear_episode.get_puzzle(3), by=self.user, guess="correctish").save()
        self.assertTrue(self.linear_episode.get_puzzle(3).answered_by(self.team))

    def can_see_all_parallel_puzzles(self):
        self.assertTrue(self.parallel_episode.unlocked_by(self.team))
        self.assertTrue(self.parallel_episode.parallel)
        for puzzle in self.parallel_episode.puzzles.all():
            self.assertTrue(puzzle.unlocked_by(self.team), msg=puzzle)

    def test_headstarts(self):
        self.assertEqual(self.linear_episode.headstart_granted(self.team),
                         self.parallel_episode.headstart_applied(self.team))
        self.assertEqual(self.linear_episode.headstart_granted(self.team), datetime.timedelta(minutes=10))
        Guess(for_puzzle=self.linear_episode.get_puzzle(2), by=self.user, guess="correct").save()
        self.assertEqual(self.linear_episode.headstart_granted(self.team),
                         self.parallel_episode.headstart_applied(self.team))
        self.assertEqual(self.linear_episode.headstart_granted(self.team), datetime.timedelta(minutes=15))


class ClueDisplayTests(TestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        user = UserProfile.objects.get(pk=1)
        self.puzzle = Puzzle.objects.get(pk=1)
        self.team = Team.objects.get(pk=1)
        self.data = PuzzleData(self.puzzle, self.team, user)

    def test_hint_display(self):
        hint = Hint.objects.get()
        self.assertFalse(hint.unlocked_by(self.team, self.data))
        self.data.tp_data.start_time = timezone.now() + datetime.timedelta(minutes=-5)
        self.assertFalse(hint.unlocked_by(self.team, self.data))
        self.data.tp_data.start_time = timezone.now() + datetime.timedelta(minutes=-10)
        self.assertTrue(hint.unlocked_by(self.team, self.data))

    def test_unlock_display(self):
        unlock = Unlock.objects.get(pk=1)
        self.assertTrue(unlock.unlocked_by(self.team, self.data))
        fail_team = Team.objects.get(pk=2)
        fail_user = UserProfile.objects.get(pk=2)
        fail_data = PuzzleData(self.puzzle, fail_team, fail_user)
        self.assertFalse(unlock.unlocked_by(fail_team, fail_data))


class AdminTeamTests(TestCase):
    fixtures = ['hunts_test']

    def test_can_view_episode(self):
        self.assertTrue(self.client.login(username='admin', password='hunter2'))

        response = self.client.get(reverse('episode', kwargs={'event_id': 1, 'episode_number': 1}))
        self.assertEqual(response.status_code, 200)


class AdminViewTests(TestCase):
    fixtures = ['hunts_test']

    def test_can_view_guesses(self):
        self.assertTrue(self.client.login(username='admin', password='hunter2'))
        response = self.client.get(reverse('guesses', kwargs={'event_id': 1}))
        self.assertEqual(response.status_code, 200)
