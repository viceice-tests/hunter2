from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.db import transaction
from django.utils import timezone
from django.urls import reverse

from events.models import Event
from events.tests import EventTestCase
from teams.models import Team, UserProfile
from .models import Answer, Episode, Guess, Hint, Puzzle, PuzzleData, TeamPuzzleData, Unlock, UnlockAnswer
from .runtimes.registry import RuntimesRegistry as rr

import datetime
import freezegun


class HomePageTests(EventTestCase):
    fixtures = ['hunts_test']

    def test_load_homepage(self):
        url = reverse('index', subdomain='www')
        response = self.client.get(url, HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)


class RegexValidationTests(EventTestCase):
    fixtures = ['hunts_test']

    def test_save_answer(self):
        puzzle = Puzzle.objects.get(pk=1)
        Answer(for_puzzle=puzzle, runtime=rr.REGEX, answer='[Rr]egex.*').save()
        with self.assertRaises(ValidationError):
            Answer(for_puzzle=puzzle, runtime=rr.REGEX, answer='[NotARegex').save()

    def test_save_unlock_answer(self):
        unlock = Unlock.objects.get(pk=1)
        UnlockAnswer(unlock=unlock, runtime=rr.REGEX, guess='[Rr]egex.*').save()
        with self.assertRaises(ValidationError):
            UnlockAnswer(unlock=unlock, runtime=rr.REGEX, guess='[NotARegex').save()


class AnswerValidationTests(EventTestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        self.puzzle = Puzzle.objects.get(pk=1)
        self.team = Team.objects.get(pk=1)
        self.data = PuzzleData(self.puzzle, self.team)

    def test_static_answers(self):
        answer = Answer.objects.get(for_puzzle=self.puzzle, runtime=rr.STATIC)
        guess = Guess.objects.filter(guess='correct', for_puzzle=self.puzzle).get()
        self.assertTrue(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='correctnot', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='incorrect', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='wrong', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))

    def test_regex_answers(self):
        answer = Answer.objects.get(for_puzzle=self.puzzle, runtime=rr.REGEX)
        guess = Guess.objects.filter(guess='correct', for_puzzle=self.puzzle).get()
        self.assertTrue(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='correctnot', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='incorrect', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='wrong', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))

    def test_lua_answers(self):
        answer = Answer.objects.get(for_puzzle=self.puzzle, runtime=rr.LUA)
        guess = Guess.objects.filter(guess='correct', for_puzzle=self.puzzle).get()
        self.assertTrue(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='correctnot', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='incorrect', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))
        guess = Guess.objects.filter(guess='wrong', for_puzzle=self.puzzle).get()
        self.assertFalse(answer.validate_guess(guess))


class AnswerSubmissionTest(EventTestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()
        self.puzzle = Puzzle.objects.get(pk=1)
        self.team = Team.objects.get(pk=1)
        self.data = PuzzleData(self.puzzle, self.team)

    def test_answer_cooldown(self):
        self.assertTrue(self.client.login(username='test', password='hunter2'))
        url = reverse('answer', kwargs={'event_id': 1, 'episode_number': 1, 'puzzle_number': 1})
        with freezegun.freeze_time() as frozen_datetime:
            response = self.client.post(url, {'last_updated': '0', 'answer': 'incorrect'})
            self.assertEqual(response.status_code, 200)
            response = self.client.post(url, {'last_updated': '0', 'answer': 'incorrect'})
            self.assertEqual(response.status_code, 429)
            self.assertTrue(b'error' in response.content)
            frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
            response = self.client.post(url, {'last_updated': '0', 'answer': 'incorrect'})
            self.assertEqual(response.status_code, 200)


class PuzzleStartTimeTests(EventTestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()

    def test_start_times(self):
        self.assertTrue(self.client.login(username='test', password='hunter2'))
        response = self.client.get('/event/1/ep/1/pz/1/')
        self.assertEqual(response.status_code, 200)
        first_time = TeamPuzzleData.objects.get().start_time
        self.assertIsNot(first_time, None)
        response = self.client.get('/event/1/ep/1/pz/1/')
        self.assertEqual(response.status_code, 200)
        second_time = TeamPuzzleData.objects.get().start_time
        self.assertEqual(first_time, second_time)


class EpisodeBehaviourTest(EventTestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        self.linear_episode = Episode.objects.get(pk=1)
        self.parallel_episode = Episode.objects.get(pk=2)
        self.team = Team.objects.get(pk=1)
        self.user = self.team.members.get(pk=1)

    def test_reuse_puzzle(self):
        puzzle = Puzzle.objects.get(pk=2)
        with self.assertRaises(ValidationError):
            self.linear_episode.puzzles.add(puzzle)

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
        # Test that headstart does not apply in the wrong direction
        self.assertEqual(self.linear_episode.headstart_applied(self.team), datetime.timedelta(minutes=0))

    def test_next_puzzle(self):
        self.assertEqual(self.linear_episode.next_puzzle(self.team), 2)
        Guess(for_puzzle=self.linear_episode.get_puzzle(2), by=self.user, guess="correct").save()
        self.assertEqual(self.linear_episode.next_puzzle(self.team), 3)
        Guess(for_puzzle=self.linear_episode.get_puzzle(3), by=self.user, guess="correctish").save()
        self.assertEqual(self.linear_episode.next_puzzle(self.team), None)

        self.assertEqual(self.parallel_episode.next_puzzle(self.team), None)
        Guess(for_puzzle=self.parallel_episode.get_puzzle(2), by=self.user, guess="4").save()
        self.assertTrue(self.parallel_episode.get_puzzle(2).answered_by(self.team))
        self.assertEqual(self.parallel_episode.next_puzzle(self.team), 3)

    def test_puzzle_numbers(self):
        puzzle1 = Puzzle.objects.get(pk=1)
        puzzle2 = Puzzle.objects.get(pk=2)
        puzzle3 = Puzzle.objects.get(pk=3)
        puzzle4 = Puzzle.objects.get(pk=4)
        self.assertEqual(puzzle1.get_relative_id(), 1)
        self.assertEqual(puzzle2.get_relative_id(), 1)
        self.assertEqual(puzzle3.get_relative_id(), 2)
        self.assertEqual(puzzle4.get_relative_id(), 3)
        self.assertEqual(self.linear_episode.get_puzzle(puzzle1.get_relative_id()), puzzle1)
        self.assertEqual(self.parallel_episode.get_puzzle(puzzle2.get_relative_id()), puzzle2)
        self.assertEqual(self.parallel_episode.get_puzzle(puzzle3.get_relative_id()), puzzle3)
        self.assertEqual(self.parallel_episode.get_puzzle(puzzle4.get_relative_id()), puzzle4)


class EpisodeSequenceTests(EventTestCase):
    fixtures = ['hunts_episodesequence']

    def setUp(self):
        self.episode1 = Episode.objects.get(pk=1)
        self.episode2 = Episode.objects.get(pk=2)
        self.team = Team.objects.get(pk=1)
        self.user = self.team.members.get(pk=1)

    def test_episode_prequel_validation(self):
        self.episode2.prequels.add(self.episode1)
        # Because we intentionally throw exceptions we need to use transaction.atomic() to avoid a TransactionManagementError
        with self.assertRaises(ValidationError), transaction.atomic():
            self.episode1.prequels.add(self.episode1)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.episode1.prequels.add(self.episode2)

    def test_episode_unlocking(self):
        self.episode2.prequels.add(self.episode1)
        self.assertTrue(self.episode1.unlocked_by(self.team))
        self.assertFalse(self.episode2.unlocked_by(self.team))
        Guess(for_puzzle=self.episode1.get_puzzle(1), by=self.user, guess="correct").save()
        self.assertTrue(self.episode2.unlocked_by(self.team))


class ClueDisplayTests(EventTestCase):
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
        self.assertTrue(unlock.unlocked_by(self.team))
        fail_team = Team.objects.get(pk=2)
        self.assertFalse(unlock.unlocked_by(fail_team))


class AdminTeamTests(EventTestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()

    def test_can_view_episode(self):
        self.assertTrue(self.client.login(username='admin', password='hunter2'))

        response = self.client.get(reverse('episode', kwargs={'event_id': 1, 'episode_number': 1}))
        self.assertEqual(response.status_code, 200)


class AdminViewTests(EventTestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()

    def test_can_view_guesses(self):
        self.assertTrue(self.client.login(username='admin', password='hunter2'))
        response = self.client.get(reverse('guesses', kwargs={'event_id': 1}))
        self.assertEqual(response.status_code, 200)


class ProgressionTests(EventTestCase):
    fixtures = ['hunts_progression']

    def setUp(self):
        self.user1   = UserProfile.objects.get(pk=1)
        self.user2   = UserProfile.objects.get(pk=2)
        self.team1   = Team.objects.get(pk=1)
        self.team2   = Team.objects.get(pk=2)
        self.event   = Event.objects.get(current=True)
        self.episode = Episode.objects.get(pk=1)

    def test_answered_by_ordering(self):
        puzzle1 = self.episode.get_puzzle(1)

        # Submit two correct answers, 1 an hour after the other.
        future_time = timezone.now() + datetime.timedelta(hours=1)
        guess1 = Guess(for_puzzle=puzzle1, by=self.user1, guess="correct")
        guess2 = Guess(for_puzzle=puzzle1, by=self.user1, guess="correct")
        guess1.save()
        guess2.save()
        guess1.given = future_time
        guess1.save()

        # Ensure the first given answer is reported first
        self.assertEqual(len(puzzle1.answered_by(self.team1)), 2)
        self.assertEqual(puzzle1.answered_by(self.team1)[0], guess2)
        self.assertEqual(puzzle1.answered_by(self.team1)[1], guess1)

    def test_episode_finishing(self):
        # Check episode has not been completed
        self.assertFalse(self.episode.finished_by(self.team1))

        # Team 1 answer all questions correctly
        Guess(for_puzzle=self.episode.get_puzzle(1), by=self.user1, guess="correct").save()
        Guess(for_puzzle=self.episode.get_puzzle(2), by=self.user1, guess="correct").save()
        Guess(for_puzzle=self.episode.get_puzzle(3), by=self.user1, guess="correctish").save()

        # Ensure this team has finished the episode
        self.assertTrue(self.episode.finished_by(self.team1))

    def test_finish_positions(self):
        puzzle1 = self.episode.get_puzzle(1)
        puzzle2 = self.episode.get_puzzle(2)
        puzzle3 = self.episode.get_puzzle(3)

        # Check there are no winners to begin with
        self.assertFalse(self.episode.finished_by(self.team1))
        self.assertFalse(self.episode.finished_by(self.team2))
        self.assertEqual(len(self.episode.finished_positions()), 0)

        # Answer all the questions correctly for both teams with team 1 ahead to begin with then falling behind
        Guess(for_puzzle=puzzle1, by=self.user1, guess="correct").save()
        Guess(for_puzzle=puzzle2, by=self.user1, guess="correct").save()

        # Check only the first team has finished the first questions
        self.assertEqual(len(puzzle1.finished_teams(self.event)), 1)
        self.assertEqual(puzzle1.finished_teams(self.event)[0], self.team1)
        self.assertEqual(puzzle1.position(self.team1), 0)
        self.assertEqual(puzzle1.position(self.team2), None)

        # Team 2 completes all answers
        Guess(for_puzzle=puzzle1, by=self.user2, guess="correct").save()
        Guess(for_puzzle=puzzle2, by=self.user2, guess="correct").save()
        Guess(for_puzzle=puzzle3, by=self.user2, guess="correctish").save()

        # Ensure this team has finished the questions and is listed as first in the finished teams
        self.assertEqual(len(self.episode.finished_positions()), 1)
        self.assertEqual(self.episode.finished_positions()[0], self.team2)

        # Team 1 finishes as well.
        Guess(for_puzzle=puzzle3, by=self.user1, guess="correctish").save()

        # Ensure both teams have finished, and are ordered correctly
        self.assertEqual(len(self.episode.finished_positions()), 2)
        self.assertEqual(self.episode.finished_positions()[0], self.team2)
        self.assertEqual(self.episode.finished_positions()[1], self.team1)

    def test_guesses(self):
        puzzle1 = self.episode.get_puzzle(1)

        # Single incorrect guess
        Guess(for_puzzle=puzzle1, by=self.user1, guess="wrong").save()

        # Check we have no correct answers
        self.assertEqual(len(puzzle1.first_correct_guesses(self.event)), 0)

        # Add two correct guesses after each other
        first_correct_guess = Guess(for_puzzle=puzzle1, by=self.user1, guess="correct")
        first_correct_guess.save()
        future_time = timezone.now() + datetime.timedelta(hours=1)
        second_correct_guess = Guess(for_puzzle=puzzle1, by=self.user1, guess="correct")
        second_correct_guess.save()
        second_correct_guess.given = future_time
        second_correct_guess.save()

        # Ensure that the first correct guess is correctly returned
        self.assertEqual(puzzle1.first_correct_guesses(self.event)[self.team1], first_correct_guess)


class CorrectnessCacheTests(EventTestCase):
    fixtures = ['hunts_progression']

    def setUp(self):
        self.user1   = UserProfile.objects.get(pk=1)
        self.user2   = UserProfile.objects.get(pk=2)
        self.team1   = Team.objects.get(pk=1)
        self.team2   = Team.objects.get(pk=2)
        self.episode = Episode.objects.get(pk=1)
        self.puzzle1 = self.episode.get_puzzle(1)
        self.puzzle2 = self.episode.get_puzzle(2)
        self.answer1 = self.puzzle1.answer_set.get()

    def test_changing_answers(self):
        # Check starting state
        self.assertFalse(self.puzzle1.answered_by(self.team1))
        self.assertFalse(self.puzzle2.answered_by(self.team2))

        # Add a correct guess and check it is marked correct
        guess1 = Guess(for_puzzle=self.puzzle1, by=self.user1, guess="correct")
        guess1.save()
        self.assertTrue(guess1.correct_current)
        self.assertTrue(self.puzzle1.answered_by(self.team1))

        # Add an incorrect guess and check
        guess2 = Guess(for_puzzle=self.puzzle2, by=self.user2, guess="correct?")
        guess2.save()
        self.assertTrue(guess2.correct_current)
        self.assertFalse(self.puzzle2.answered_by(self.team2))

        # Alter the answer and check only the first guess is invalidated
        self.answer1.answer = "correct!"
        self.answer1.save()
        guess1.refresh_from_db()
        guess2.refresh_from_db()
        self.assertFalse(guess1.correct_current)
        self.assertTrue(guess2.correct_current)
        self.assertFalse(guess1.get_correct_for())
        self.assertFalse(self.puzzle1.answered_by(self.team1))

        # Update the first guess and check
        guess1.guess = "correct!"
        guess1.save()
        self.assertTrue(self.puzzle1.answered_by(self.team1))

        # Delete the first answer and check
        self.answer1.delete()
        guess1.refresh_from_db()
        guess2.refresh_from_db()
        self.assertFalse(guess1.correct_current)
        self.assertTrue(guess2.correct_current)
        self.assertFalse(guess1.get_correct_for())
        self.assertFalse(self.puzzle1.answered_by(self.team1))

        # Add an answer that matches guess 2 and check
        Answer(for_puzzle=self.puzzle2, runtime='S', answer='correct?').save()
        guess1.refresh_from_db()
        guess2.refresh_from_db()
        self.assertTrue(guess1.correct_current)
        self.assertFalse(guess2.correct_current)
        self.assertFalse(self.puzzle1.answered_by(self.team1))
        self.assertTrue(guess2.get_correct_for())
        self.assertTrue(self.puzzle2.answered_by(self.team2))


class GuessTeamDenormalisationTests(EventTestCase):
    fixtures = ['hunts_progression']

    def setUp(self):
        self.team1   = Team.objects.get(pk=1)
        self.team2   = Team.objects.get(pk=2)
        self.user1   = self.team1.members.get()
        self.user2   = self.team2.members.get()
        self.episode = Episode.objects.get(pk=1)
        self.puzzle1 = self.episode.get_puzzle(1)
        self.puzzle2 = self.episode.get_puzzle(2)
        self.answer1 = self.puzzle1.answer_set.get()

    def test_adding_guess(self):
        guess1 = Guess(for_puzzle=self.puzzle1, by=self.user1, guess="incorrect")
        guess2 = Guess(for_puzzle=self.puzzle2, by=self.user2, guess="incorrect")
        guess1.save()
        guess2.save()
        self.assertEqual(guess1.by_team, self.team1)
        self.assertEqual(guess2.by_team, self.team2)

    def test_join_team_updates_guesses(self):
        guess1 = Guess(for_puzzle=self.puzzle1, by=self.user1, guess="incorrect")
        guess2 = Guess(for_puzzle=self.puzzle2, by=self.user2, guess="incorrect")
        guess1.save()
        guess2.save()

        # Swap teams and check the guesses update
        self.team1.members = []
        self.team2.members = [self.user1]
        self.team1.save()
        self.team2.save()
        self.team1.members = [self.user2]
        self.team1.save()

        guess1.refresh_from_db()
        guess2.refresh_from_db()
        self.assertEqual(guess1.by_team, self.team2)
        self.assertEqual(guess2.by_team, self.team1)
