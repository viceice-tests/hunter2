# vim: set fileencoding=utf-8 :


class IFrameRuntime():
    def evaluate(self, url, team_puzzle_data, user_puzzle_data, team_data, user_data):
        return f'<iframe src="{url}"></iframe>'

    def validate_guess(self, validator, guess, team_puzzle_data, team_data):
        return False
