class AbstractRuntime:
    def check_script(self, script):
        return True

    def evaluate(self, script, team_puzzle_data, user_puzzle_data, team_data, user_data):
        raise NotImplementedError("Abstract")

    # TODO: Consider changing to allow returning a result and unlock hints for this puzzle.
    def validate_guess(self, validator, guess):
        raise NotImplementedError("Abstract")
