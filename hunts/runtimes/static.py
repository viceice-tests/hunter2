from .abstract import AbstractRuntime


class StaticRuntime(AbstractRuntime):
    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        return script

    def validate_guess(self, validator, guess):
        return validator.lower() == guess.lower()
