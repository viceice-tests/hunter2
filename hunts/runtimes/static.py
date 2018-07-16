# vim: set fileencoding=utf-8 :
from .abstract import AbstractRuntime


class StaticRuntime(AbstractRuntime):
    def __init__(self, case_sensitive):
        self.case_sensitive = case_sensitive

    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        return script

    def validate_guess(self, validator, guess):
        if self.case_sensitive:
            return validator == guess
        else:
            return validator.lower() == guess.lower()
