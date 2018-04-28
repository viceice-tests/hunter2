# vim: set fileencoding=utf-8 :
from urllib.parse import parse_qs, urlencode, urlparse

from .abstract import AbstractRuntime

class IFrameRuntime(AbstractRuntime):
    def check_script(self, url):
        url_parts = urlparse(url)

    def evaluate(self, url, team_puzzle_data, user_puzzle_data, team_data, user_data):
        url_parts = urlparse(url)
        query_params = parse_qs(url_parts.query)
        query_params['token'] = user_puzzle_data.token
        url_parts = url_parts._replace(query=urlencode(query_params, doseq=True))
        url = url_parts.geturl()
        return """<iframe width="100%%" frameborder="0" scrolling="no" onload="resizeIframe(this)" src="%s"></iframe>
<script>
    function resizeIframe(obj) {
        obj.style.height = obj.contentWindow.document.body.scrollHeight + "px";
    }
</script>""" % url

    def validate_guess(self, validator, guess):
        raise NotImplementedError("IFrameRuntime can not be used for guess validation")
