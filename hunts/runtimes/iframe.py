# vim: set fileencoding=utf-8 :
from urllib.parse import parse_qs, urlencode, urlparse


class IFrameRuntime():
    def evaluate(self, url, team_puzzle_data, user_puzzle_data, team_data, user_data):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params['token'] = user_puzzle_data.token
        parsed_url.query = query_params
        url = urlencode(parsed_url, doseq=True)
        return f'<iframe src="{url}"></iframe>'

    def validate_guess(self, validator, guess, team_puzzle_data, team_data):
        raise NotImplementedError("IFrameRuntime can not be used for guess validation")
