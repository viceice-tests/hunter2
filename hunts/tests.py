from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone
from events.models import Event, Theme
from teams.models import Team, UserProfile
from .models import Answer, Episode, Guess, Puzzle, TeamPuzzleData
from . import runtime


class StaticAnswerValidationTests(TestCase):
    def setUp(self):
        test_name = self.__class__.__name__
        puzzle = Puzzle.objects.create(title=test_name, content=test_name)
        user = User.objects.create()
        profile = UserProfile.objects.create(user=user)
        Answer.objects.create(
            for_puzzle=puzzle, runtime=runtime.STATIC, answer='correct'
        )
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='correct')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='correctnot')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='incorrect')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='wrong')

    def test_correct_answer(self):
        guess = Guess.objects.filter(guess='correct').get()
        self.assertTrue(guess.is_right())

    def test_incorrect_answers(self):
        guess = Guess.objects.filter(guess='correctnot').get()
        self.assertFalse(guess.is_right())
        guess = Guess.objects.filter(guess='incorrect').get()
        self.assertFalse(guess.is_right())
        guess = Guess.objects.filter(guess='wrong').get()
        self.assertFalse(guess.is_right())


class RegexAnswerValidationTests(TestCase):
    def setUp(self):
        test_name = self.__class__.__name__
        puzzle = Puzzle.objects.create(title=test_name, content=test_name)
        user = User.objects.create()
        profile = UserProfile.objects.create(user=user)
        Answer.objects.create(
            for_puzzle=puzzle, runtime=runtime.REGEX, answer='cor+ect'
        )
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='correct')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='correctnot')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='incorrect')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='wrong')

    def test_correct_answer(self):
        guess = Guess.objects.filter(guess='correct').get()
        self.assertTrue(guess.is_right())

    def test_incorrect_answers(self):
        guess = Guess.objects.filter(guess='correctnot').get()
        self.assertFalse(guess.is_right())
        guess = Guess.objects.filter(guess='incorrect').get()
        self.assertFalse(guess.is_right())
        guess = Guess.objects.filter(guess='wrong').get()
        self.assertFalse(guess.is_right())


class LuaAnswerValidationTests(TestCase):
    def setUp(self):
        test_name = self.__class__.__name__
        puzzle = Puzzle.objects.create(title=test_name, content=test_name)
        user = User.objects.create()
        profile = UserProfile.objects.create(user=user)
        Answer.objects.create(
            for_puzzle=puzzle,
            runtime=runtime.LUA,
            answer='return guess == "correct"'
        )
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='correct')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='correctnot')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='incorrect')
        Guess.objects.create(for_puzzle=puzzle, by=profile, guess='wrong')

    def test_correct_answer(self):
        guess = Guess.objects.filter(guess='correct').get()
        self.assertTrue(guess.is_right())

    def test_incorrect_answers(self):
        guess = Guess.objects.filter(guess='correctnot').get()
        self.assertFalse(guess.is_right())
        guess = Guess.objects.filter(guess='incorrect').get()
        self.assertFalse(guess.is_right())
        guess = Guess.objects.filter(guess='wrong').get()
        self.assertFalse(guess.is_right())


class PuzzleStartTimeTests(TestCase):
    def setUp(self):
        Site.objects.create(domain='localhost', name='localhost')
        test_name = self.__class__.__name__
        theme = Theme.objects.create(name=test_name)
        event = Event.objects.create(name=test_name, theme=theme)
        puzzle = Puzzle.objects.create(title=test_name, content=test_name)
        episode = Episode.objects.create(
            name=test_name,
            start_date=timezone.now(),
            event=event
        )
        episode.puzzles.add(puzzle)
        team = Team.objects.create(at_event=event)
        user = User.objects.create(username='user', password='hunter2')
        profile = UserProfile.objects.create(user=user)
        profile.teams.add(team)

    def test_start_times(self):
        self.assertTrue(self.client.login(username='user', password='hunter2'))
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/ep/1/pz/1')
        self.assertEquals(response.status_code, 200)
        first_time = TeamPuzzleData.objects.get().start_time
        self.assertIsNot(first_time, None)
        self.client.get('/ep/1/pz/1')
        second_time = TeamPuzzleData.objects.get().start_time
        self.assertEqual(first_time, second_time)
