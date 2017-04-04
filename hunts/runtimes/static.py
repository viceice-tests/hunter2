# vim: set fileencoding=utf-8 :
from . import AbstractRuntime


class StaticRuntime(AbstractRuntime):
    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        return script

    def validate_guess(self, validator, guess, team_puzzle_data, team_data):
        return validator.lower() == guess.lower()
