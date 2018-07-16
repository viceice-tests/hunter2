# vim: set fileencoding=utf-8 :
import re

from .abstract import AbstractRuntime


class RegexRuntime(AbstractRuntime):
    flags = 0

    def __init__(self, case_sensitive):
        self.flags = 0 if case_sensitive else re.IGNORECASE

    def check_script(self, script):
        try:
            re.compile(script, flags=self.flags)
        except re.error as error:
            raise SyntaxError(error) from error

    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        raise NotImplementedError("RegexRuntime can not be used for static evaluation")

    def validate_guess(self, validator, guess):
        try:
            return re.fullmatch(validator, guess, flags=self.flags)
        except re.error as error:
            raise SyntaxError(error) from error
