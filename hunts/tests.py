import datetime
import random

import freezegun
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from accounts.factories import SiteFactory, UserProfileFactory
from accounts.models import UserProfile
from events.factories import EventFactory
from events.models import Event
from hunter2.resolvers import reverse
from teams.factories import TeamFactory, TeamMemberFactory
from teams.models import Team
from .factories import (
    AnnouncementFactory,
    AnswerFactory,
    EpisodeFactory,
    GuessFactory,
    HintFactory,
    PuzzleFactory,
    PuzzleFileFactory,
    TeamDataFactory,
    TeamPuzzleDataFactory,
    UnlockAnswerFactory,
    UnlockFactory,
    UserDataFactory,
    UserPuzzleDataFactory,
)
from .models import Answer, Episode, Guess, Hint, Puzzle, PuzzleData, TeamPuzzleData, Unlock
from . import runtimes


class FactoryTests(TestCase):

    def test_puzzle_factory_default_construction(self):
        PuzzleFactory.create()

    def test_puzzle_file_factory_default_construction(self):
        PuzzleFileFactory.create()

    def test_hint_factory_default_construction(self):
        HintFactory.create()

    def test_unlock_factory_default_construction(self):
        UnlockFactory.create()

    def test_unlock_answer_factory_default_construction(self):
        UnlockAnswerFactory.create()

    def test_answer_factory_default_construction(self):
        AnswerFactory.create()

    def test_guess_factory_default_construction(self):
        GuessFactory.create()

    def test_guess_factory_correct(self):
        guess = GuessFactory(correct=True)
        self.assertEqual(guess.guess, guess.for_puzzle.answer_set.get().answer)

    def test_team_data_factory_default_construction(self):
        TeamDataFactory.create()

    def test_user_data_factory_default_construction(self):
        UserDataFactory.create()

    def test_team_puzzle_data_factory_default_construction(self):
        TeamPuzzleDataFactory.create()

    def test_user_puzzle_data_factory_default_construction(self):
        UserPuzzleDataFactory.create()

    def test_episode_factory_default_construction(self):
        EpisodeFactory.create()

    def test_announcement_factory_default_construction(self):
        AnnouncementFactory.create()


class HomePageTests(TestCase):
    def test_load_homepage(self):
        # Need one default event.
        EventFactory.create()
        url = reverse('index', subdomain='www')
        response = self.client.get(url, HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)


class StaticValidationTests(TestCase):
    def test_static_save_answer(self):
        AnswerFactory(runtime=runtimes.STATIC, answer='answer')

    def test_static_save_unlock_answer(self):
        UnlockAnswerFactory(runtime=runtimes.STATIC, guess='unlock')

    def test_static_answers(self):
        answer = AnswerFactory(runtime=runtimes.STATIC, answer='correct')
        guess = GuessFactory(guess='correct', for_puzzle=answer.for_puzzle)
        self.assertTrue(answer.validate_guess(guess))
        guess = GuessFactory(guess='correctnot', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))
        guess = GuessFactory(guess='incorrect', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))
        guess = GuessFactory(guess='wrong', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))


class RegexValidationTests(TestCase):
    def test_regex_save_answer(self):
        AnswerFactory(runtime=runtimes.REGEX, answer='[Rr]egex.*')
        with self.assertRaises(ValidationError):
            AnswerFactory(runtime=runtimes.REGEX, answer='[NotARegex')

    def test_regex_save_unlock_answer(self):
        UnlockAnswerFactory(runtime=runtimes.REGEX, guess='[Rr]egex.*')
        with self.assertRaises(ValidationError):
            UnlockAnswerFactory(runtime=runtimes.REGEX, guess='[NotARegex')

    def test_regex_answers(self):
        answer = AnswerFactory(runtime=runtimes.REGEX, answer='cor+ect')
        guess = GuessFactory(guess='correct', for_puzzle=answer.for_puzzle)
        self.assertTrue(answer.validate_guess(guess))
        guess = GuessFactory(guess='correctnot', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))
        guess = GuessFactory(guess='incorrect', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))
        guess = GuessFactory(guess='wrong', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))


class LuaValidationTests(TestCase):
    def test_lua_save_answer(self):
        AnswerFactory(runtime=runtimes.LUA, answer='''return {} == nil''')
        with self.assertRaises(ValidationError):
            AnswerFactory(runtime=runtimes.LUA, answer='''@''')

    def test_lua_save_unlock_answer(self):
        UnlockAnswerFactory(runtime=runtimes.LUA, guess='''return {} == nil''')
        with self.assertRaises(ValidationError):
            UnlockAnswerFactory(runtime=runtimes.LUA, guess='''@''')

    def test_lua_answers(self):
        answer = AnswerFactory(runtime=runtimes.LUA, answer='''return guess == "correct"''')
        guess = GuessFactory(guess='correct', for_puzzle=answer.for_puzzle)
        self.assertTrue(answer.validate_guess(guess))
        guess = GuessFactory(guess='correctnot', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))
        guess = GuessFactory(guess='incorrect', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))
        guess = GuessFactory(guess='wrong', for_puzzle=answer.for_puzzle)
        self.assertFalse(answer.validate_guess(guess))


class AnswerSubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteFactory.create()
        cls.site = Site.objects.get_current()
        cls.puzzle = PuzzleFactory()
        cls.episode = cls.puzzle.episode_set.get()
        cls.event = cls.episode.event
        cls.user = TeamMemberFactory(team__at_event=cls.event)
        cls.url = reverse('answer', subdomain='www', kwargs={
            'event_id': cls.event.id,
            'episode_number': cls.episode.get_relative_id(),
            'puzzle_number': cls.puzzle.get_relative_id()
        },)

    def setUp(self):
        self.client.force_login(self.user.user)

    def test_no_answer_given(self):
        response = self.client.post(self.url, HTTP_HOST=f'www.{self.site.domain}')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'no answer given')

    def test_answer_cooldown(self):
        with freezegun.freeze_time() as frozen_datetime:
            response = self.client.post(self.url, {'last_updated': '0', 'answer': 'incorrect'}, HTTP_HOST=f'www.{self.site.domain}')
            self.assertEqual(response.status_code, 200)
            response = self.client.post(self.url, {'last_updated': '0', 'answer': 'incorrect'}, HTTP_HOST=f'www.{self.site.domain}')
            self.assertEqual(response.status_code, 429)
            self.assertTrue(b'error' in response.content)
            frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
            response = self.client.post(self.url, {'last_updated': '0', 'answer': 'incorrect'}, HTTP_HOST=f'www.{self.site.domain}')
            self.assertEqual(response.status_code, 200)


class PuzzleStartTimeTests(TestCase):
    def test_start_times(self):
        SiteFactory.create()
        self.site = Site.objects.get_current()
        self.puzzle = PuzzleFactory()
        self.episode = self.puzzle.episode_set.get()
        self.event = self.episode.event
        self.user = TeamMemberFactory(team__at_event=self.event)

        self.client.force_login(self.user.user)

        response = self.client.get(self.puzzle.get_absolute_url(), HTTP_HOST=f'www.{self.site.domain}')
        self.assertEqual(response.status_code, 200, msg='Puzzle is accessible on absolute url')

        first_time = TeamPuzzleData.objects.get().start_time
        self.assertIsNot(first_time, None, msg='Start time is set on first access to a puzzle')

        response = self.client.get(self.puzzle.get_absolute_url(), HTTP_HOST=f'www.{self.site.domain}')
        self.assertEqual(response.status_code, 200, msg='Puzzle is accessible on absolute url')

        second_time = TeamPuzzleData.objects.get().start_time
        self.assertEqual(first_time, second_time, msg='Start time does not alter on subsequent access')


class PuzzleAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteFactory.create()
        cls.site = Site.objects.get_current()
        cls.episode = EpisodeFactory(parallel=False)
        cls.puzzles = PuzzleFactory.create_batch(3, episode=cls.episode)
        cls.event = cls.episode.event
        cls.user = TeamMemberFactory(team__at_event=cls.event)

    def test_puzzle_view_authorisation(self):
        http_host = f'www.{self.site.domain}'

        self.client.force_login(self.user.user)

        def _check_load_callback_answer(puzzle, expected_response):
            kwargs = {
                'event_id': self.event.id,
                'episode_number': self.episode.get_relative_id(),
                'puzzle_number': puzzle.get_relative_id(),
            }

            # Load
            response = self.client.get(
                reverse('puzzle', subdomain='www', kwargs=kwargs),
                HTTP_HOST=http_host,
            )
            self.assertEqual(response.status_code, expected_response)

            # Callback
            response = self.client.post(
                reverse('callback', subdomain='www', kwargs=kwargs),
                content_type='application/json',
                HTTP_ACCEPT='application/json',
                HTTP_HOST=http_host,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            )
            self.assertEqual(response.status_code, expected_response)

            # Answer
            response = self.client.post(
                reverse('answer', subdomain='www', kwargs=kwargs),
                {'answer': 'NOT_CORRECT'},  # Deliberately incorrect answer
                HTTP_HOST=http_host,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, expected_response)

        # This test submits two answers on the same puzzle so we have to jump forward 5 seconds
        with freezegun.freeze_time() as frozen_datetime:
            # Create an initial correct guess and wait 5 seconds before attempting other answers.
            GuessFactory(
                by=self.user,
                for_puzzle=self.puzzles[0],
                correct=True
            )
            frozen_datetime.tick(delta=datetime.timedelta(seconds=5))

            # Can load, callback and answer the first two puzzles
            _check_load_callback_answer(self.puzzles[0], 200)
            _check_load_callback_answer(self.puzzles[1], 200)
            # Can't load, callback or answer the third puzzle
            _check_load_callback_answer(self.puzzles[2], 403)

            # Answer the second puzzle after a delay of 5 seconds
            frozen_datetime.tick(delta=datetime.timedelta(seconds=5))
            response = self.client.post(
                reverse('answer', subdomain='www', kwargs={
                    'event_id': self.event.id,
                    'episode_number': self.episode.get_relative_id(),
                    'puzzle_number': self.puzzles[1].get_relative_id()}),
                {
                    'answer': self.puzzles[1].answer_set.get().answer
                },
                HTTP_HOST=http_host,
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            self.assertEqual(response.status_code, 200)
            # Can now load, callback and answer the third puzzle
            _check_load_callback_answer(self.puzzles[2], 200)


class EpisodeBehaviourTests(TestCase):
    def test_reuse_puzzle(self):
        puzzles = PuzzleFactory.create_batch(2)
        with self.assertRaises(ValidationError, msg='Reusing a puzzle raises a ValidationError'):
            puzzles[0].episode_set.get().puzzles.add(puzzles[1])

    def test_linear_episodes_are_linear(self):
        linear_episode = EpisodeFactory(parallel=False)
        PuzzleFactory.create_batch(10, episode=linear_episode)
        user = UserProfileFactory()
        team = TeamFactory(at_event=linear_episode.event, members=user)

        # TODO: Scramble puzzle order before starting (so they are not in the order they were created).

        # Check we can start and that it is a linear episode.
        self.assertTrue(linear_episode.unlocked_by(team), msg='Episode is unlocked by team')
        self.assertFalse(linear_episode.parallel, msg='Episode is not set as parallel')

        for i in range(1, linear_episode.puzzles.count() + 1):
            # Test we have unlocked the question, but not answered it yet.
            self.assertTrue(linear_episode.get_puzzle(i).unlocked_by(team), msg=f'Puzzle[{i}] is unlocked')
            self.assertFalse(linear_episode.get_puzzle(i).answered_by(team), msg=f'Puzzle[{i}] is not answered')

            # Test that we have not unlocked the next puzzle before answering.
            if i < linear_episode.puzzles.count():
                self.assertFalse(linear_episode.get_puzzle(i + 1).unlocked_by(team), msg=f'Puzzle[{i + 1}] is not unlocked until previous puzzle answered')

            # Answer the question and assert that it's now answered.
            GuessFactory.create(for_puzzle=linear_episode.get_puzzle(i), by=user, correct=True)
            self.assertTrue(linear_episode.get_puzzle(i).answered_by(team), msg=f'Correct guess has answered puzzle[{i}]')

    def test_can_see_all_parallel_puzzles(self):
        parallel_episode = EpisodeFactory(parallel=True)
        PuzzleFactory.create_batch(5, episode=parallel_episode)
        team = TeamFactory(at_event=parallel_episode.event)

        # Check we can start and that it is a parallel episode.
        self.assertTrue(parallel_episode.unlocked_by(team))
        self.assertTrue(parallel_episode.parallel)

        # Ensure all puzzles in a parallel episode are unlocked.
        for puzzle in parallel_episode.puzzles.all():
            self.assertTrue(puzzle.unlocked_by(team), msg='Puzzle unlocked in parallel episode')

    # def test_headstarts(self):
    #     self.assertEqual(self.linear_episode.headstart_granted(self.team),
    #                      self.parallel_episode.headstart_applied(self.team))
    #     self.assertEqual(self.linear_episode.headstart_granted(self.team), datetime.timedelta(minutes=10))
    #     Guess(for_puzzle=self.linear_episode.get_puzzle(2), by=self.user, guess="correct").save()
    #     self.assertEqual(self.linear_episode.headstart_granted(self.team),
    #                      self.parallel_episode.headstart_applied(self.team))
    #     self.assertEqual(self.linear_episode.headstart_granted(self.team), datetime.timedelta(minutes=15))
    #     # Test that headstart does not apply in the wrong direction
    #     self.assertEqual(self.linear_episode.headstart_applied(self.team), datetime.timedelta(minutes=0))

    def test_next_linear_puzzle(self):
        linear_episode = EpisodeFactory(parallel=False)
        PuzzleFactory.create_batch(10, episode=linear_episode)
        user = UserProfileFactory()
        team = TeamFactory(at_event=linear_episode.event, members=user)

        # TODO: Scramble puzzle order before starting (so they are not in the order they were created).

        # Check we can start and that it is a linear episode.
        self.assertTrue(linear_episode.unlocked_by(team), msg='Episode is unlocked by team')
        self.assertFalse(linear_episode.parallel, msg='Episode is not set as parallel')

        for i in range(1, linear_episode.puzzles.count() + 1):
            # Test we have unlocked the question, but not answered it yet.
            self.assertEqual(linear_episode.next_puzzle(team), i, msg=f'Puzzle[{i}]\'s next puzzle is Puzzle[{i + 1}]')

            # Answer the question and assert that it's now answered.
            GuessFactory.create(for_puzzle=linear_episode.get_puzzle(i), by=user, correct=True)
            self.assertTrue(linear_episode.get_puzzle(i).answered_by(team), msg=f'Correct guess has answered puzzle[{i}]')

    def test_next_parallel_puzzle(self):
        parallel_episode = EpisodeFactory(parallel=True)
        PuzzleFactory.create_batch(10, episode=parallel_episode)
        user = UserProfileFactory()
        team = TeamFactory(at_event=parallel_episode.event, members=user)

        # TODO: Scramble puzzle order before starting (so they are not in the order they were created).

        # Check we can start and that it is a linear episode.
        self.assertTrue(parallel_episode.unlocked_by(team), msg='Episode is unlocked by team')
        self.assertTrue(parallel_episode.parallel, msg='Episode is not set as parallel')

        # Answer all questions in a random order.
        answer_order = list(range(1, parallel_episode.puzzles.count() + 1))
        random.shuffle(answer_order)

        for i in answer_order:
            # Should be no 'next' puzzle for parallel episodes, unless there is just one left.
            # TODO: Check that this is the behaviour that we want, never having a next seems more logical.
            if i != answer_order[-1]:
                self.assertIsNone(parallel_episode.next_puzzle(team), msg='Parallel episode has no next puzzle')
            else:
                self.assertEqual(parallel_episode.next_puzzle(team), i, msg='Last unanswered is next puzzle in parallel episode')

            # Answer the question and assert that it's now answered.
            GuessFactory.create(for_puzzle=parallel_episode.get_puzzle(i), by=user, correct=True)
            self.assertTrue(parallel_episode.get_puzzle(i).answered_by(team), msg=f'Correct guess has answered puzzle[{i}]')
        self.assertIsNone(parallel_episode.next_puzzle(team), msg='Parallel episode has no next puzzle when all puzzles are answered')

    def test_puzzle_numbers(self):
        for episode in EpisodeFactory.create_batch(5):
            for i, puzzle in enumerate(PuzzleFactory.create_batch(5, episode=episode)):
                self.assertEqual(puzzle.get_relative_id(), i + 1, msg='Relative ID should match index in episode')
                self.assertEqual(episode.get_puzzle(puzzle.get_relative_id()), puzzle, msg='A Puzzle\'s relative ID should retrieve it from its Episode')


class EpisodeSequenceTests(TestCase):
    fixtures = ['hunts_episodesequence']

    def setUp(self):
        self.episode1 = Episode.objects.get(pk=1)
        self.episode2 = Episode.objects.get(pk=2)
        self.episode2.prequels.add(self.episode1)
        self.team = Team.objects.get(pk=1)
        self.user = self.team.members.get(pk=1)

    def test_episode_prequel_validation(self):
        # Because we intentionally throw exceptions we need to use transaction.atomic() to avoid a TransactionManagementError
        with self.assertRaises(ValidationError), transaction.atomic():
            self.episode1.prequels.add(self.episode1)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.episode1.prequels.add(self.episode2)

    def test_episode_unlocking(self):
        self.assertTrue(self.client.login(username='test', password='hunter2'))

        # Can load first episode
        response = self.client.get(reverse('episode', subdomain='www', kwargs={'event_id': 1, 'episode_number': 1}), HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('episode_content', subdomain='www', kwargs={'event_id': 1, 'episode_number': 1}),
            HTTP_HOST='www.testserver',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        # Can't load second episode
        response = self.client.get(reverse('episode', subdomain='www', kwargs={'event_id': 1, 'episode_number': 2}), HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse('episode_content', subdomain='www', kwargs={'event_id': 1, 'episode_number': 2}),
            HTTP_HOST='www.testserver',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 403)

        # Unlock second episode
        Guess(for_puzzle=self.episode1.get_puzzle(1), by=self.user, guess="correct").save()

        # Can now load second episode
        response = self.client.get(reverse('episode', subdomain='www', kwargs={'event_id': 1, 'episode_number': 2}), HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            reverse('episode_content', subdomain='www', kwargs={'event_id': 1, 'episode_number': 2}),
            HTTP_HOST='www.testserver',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)


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
        self.assertTrue(unlock.unlocked_by(self.team))
        fail_team = Team.objects.get(pk=2)
        self.assertFalse(unlock.unlocked_by(fail_team))


class AdminTeamTests(TestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()

    def test_can_view_episode(self):
        self.assertTrue(self.client.login(username='admin', password='hunter2'))

        response = self.client.get(reverse('episode', subdomain='www', kwargs={'event_id': 1, 'episode_number': 1}), HTTP_HOST='www.testserver')
        self.assertEqual(response.status_code, 200)


class AdminViewTests(TestCase):
    fixtures = ['hunts_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()

    def test_can_view_guesses(self):
        self.assertTrue(self.client.login(username='admin', password='hunter2'))
        response = self.client.get(reverse('guesses', subdomain='admin', kwargs={'event_id': 1}), HTTP_HOST='admin.testserver')
        self.assertEqual(response.status_code, 200)


class ProgressionTests(TestCase):
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


class CorrectnessCacheTests(TestCase):
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


class GuessTeamDenormalisationTests(TestCase):
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
        self.team1.members.set([])
        self.team2.members.set([self.user1])
        self.team1.save()
        self.team2.save()
        self.team1.members.set([self.user2])
        self.team1.save()

        guess1.refresh_from_db()
        guess2.refresh_from_db()
        self.assertEqual(guess1.by_team, self.team2)
        self.assertEqual(guess2.by_team, self.team1)
