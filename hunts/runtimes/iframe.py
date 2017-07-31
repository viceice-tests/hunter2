# vim: set fileencoding=utf-8 :
from urllib.parse import parse_qs, urlencode, urlparse


class IFrameRuntime():
    def evaluate(self, url, team_puzzle_data, user_puzzle_data, team_data, user_data):
        url_parts = urlparse(url)
        query_params = parse_qs(url_parts.query)
        query_params['token'] = user_puzzle_data.token
        url_parts = url_parts._replace(query=urlencode(query_params, doseq=True))
        url = url_parts.geturl()
        return f'<iframe src="{url}"></iframe>'

    def validate_guess(self, validator, guess):
        raise NotImplementedError("IFrameRuntime can not be used for guess validation")
