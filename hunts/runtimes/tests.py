# vim: set fileencoding=utf-8 :
from django.test import TestCase

from .iframe import IFrameRuntime
from .regex import RegexRuntime
from .static import StaticRuntime

from .. import models

import re


class IFrameRuntimeTestCase(TestCase):
    def setUp(self):
        self.iframe_runtime = IFrameRuntime()

    def test_evaluate_no_param(self):
        iframe_url = r'https://example.com/'
        up_data = models.UserPuzzleData()
        response = self.iframe_runtime.evaluate(iframe_url, None, up_data, None, None)
        self.assertTrue(
            re.search(r'<iframe .* src="https://example.com/\?token=[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"></iframe>', response)
        )

    def test_evaluate_with_param(self):
        iframe_url = r'https://example.com/?k=v'
        up_data = models.UserPuzzleData()
        response = self.iframe_runtime.evaluate(iframe_url, None, up_data, None, None)
        self.assertTrue(
            re.match(r'<iframe .* src="https://example.com/\?k=v&token=[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"></iframe>', response)
        )

    def test_validate_guess(self):
        iframe_url = r'https://example.com/'
        with self.assertRaises(NotImplementedError):
            self.iframe_runtime.validate_guess(iframe_url, "")


class RegexRuntimeTestCase(TestCase):
    def test_evaluate(self):
        regex_runtime = RegexRuntime()
        regex_script = r'.*'
        with self.assertRaises(NotImplementedError):
            regex_runtime.evaluate(regex_script, None, None, None, None)

    def test_validate_guess(self):
        regex_runtime = RegexRuntime()
        regex_script = r'Hello \w*!'
        guess1 = "Hello Planet!"
        result = regex_runtime.validate_guess(regex_script, guess1)
        self.assertTrue(result)
        guess2 = "Goodbye World!"
        result = regex_runtime.validate_guess(regex_script, guess2)
        self.assertFalse(result)

    def test_evaluate_syntax_error_fails(self):
        regex_runtime = RegexRuntime()
        regex_script = r'[]'
        with self.assertRaises(SyntaxError):
            regex_runtime.validate_guess(regex_script, "")


class StaticRuntimeTestCase(TestCase):
    def test_evaluate(self):
        static_runtime = StaticRuntime()
        static_script = '''Hello  World!'''
        result = static_runtime.evaluate(static_script, None, None, None, None)
        self.assertEqual(result, static_script)

    def test_validate_guess(self):
        static_runtime = StaticRuntime()
        static_script = '''answer'''
        guess1 = "answer"
        result = static_runtime.validate_guess(static_script, guess1)
        self.assertTrue(result)
        guess2 = "incorrect answer"
        result = static_runtime.validate_guess(static_script, guess2)
        self.assertFalse(result)
