from django.contrib.auth.models import User
from django.test import TestCase
from teams.models import UserProfile
from .models import Answer, Guess, Puzzle
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
