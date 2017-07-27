# vim: set fileencoding=utf-8 :
import os
import tempfile
import logging
from io import StringIO

import builtins
from colour_runner.django_runner import ColourRunnerMixin
from django.contrib.sites.models import Site
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.test.runner import DiscoverRunner

from hunter2.management.commands import setupsite
from .utils import generate_secret_key, load_or_create_secret_key


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # Disable non-critial logging for test runs
        logging.disable(logging.CRITICAL)
        return super(TestRunner, self).run_tests(test_labels, extra_tests, **kwargs)


# Adapted from:
# https://github.com/django/django/blob/7588d7e439a5deb7f534bdeb2abe407b937e3c1a/tests/auth_tests/test_management.py
def mock_inputs(inputs):
    """
    Decorator to temporarily replace input/getpass to allow interactive
    createsuperuser.
    """

    def inner(test_function):
        def wrap_input(*args):
            def mock_input(prompt):
                for key, value in inputs.items():
                    if key in prompt.lower():
                        return value
                return ""

            old_input = builtins.input
            builtins.input = mock_input
            try:
                test_function(*args)
            finally:
                builtins.input = old_input

        return wrap_input

    return inner


class MockTTY:
    """
    A fake stdin object that pretends to be a TTY to be used in conjunction
    with mock_inputs.
    """

    def isatty(self):
        return True


class MigrationsTests(TestCase):
    # Adapted for Python3 from:
    # http://tech.octopus.energy/news/2016/01/21/testing-for-missing-migrations-in-django.html
    @override_settings(MIGRATION_MODULES={})
    def test_for_missing_migrations(self):
        output = StringIO()
        try:
            call_command(
                'makemigrations',
                interactive=False,
                dry_run=True,
                exit_code=True,
                stdout=output
            )
        except SystemExit as e:
            # The exit code will be 1 when there are no missing migrations
            self.assertEqual(str(e), '1')
        else:
            self.fail("There are missing migrations:\n %s" % output.getvalue())


class SecretKeyGenerationTests(TestCase):
    def test_secret_key_length(self):
        secret_key = generate_secret_key()
        self.assertGreaterEqual(len(secret_key), 50)

    def test_subsequent_secret_keys_are_different(self):
        secret_key1 = generate_secret_key()
        secret_key2 = generate_secret_key()
        self.assertNotEqual(secret_key1, secret_key2)

    def test_write_generated_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            secrets_file = os.path.join(temp_dir, "secrets.ini")
            self.assertFalse(os.path.exists(secrets_file))
            load_or_create_secret_key(secrets_file)
            self.assertTrue(os.path.exists(secrets_file))

    def test_preserve_existing_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            secrets_file = os.path.join(temp_dir, "secrets.ini")
            self.assertFalse(os.path.exists(secrets_file))
            secret_key1 = load_or_create_secret_key(secrets_file)
            self.assertTrue(os.path.exists(secrets_file))
            secret_key2 = load_or_create_secret_key(secrets_file)
            self.assertEqual(secret_key1, secret_key2)


class SetupSiteManagementCommandTests(TestCase):
    TEST_SITE_NAME   = "Test Site"
    TEST_SITE_DOMAIN = "test-domain.local"

    def test_no_site_name_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --name and --domain with --noinput."):
            call_command('setupsite', interactive=False, site_domain="custom-domain.local", stdout=output)

    def test_no_site_domain_argument(self):
        output = StringIO()
        with self.assertRaisesMessage(CommandError, "You must use --name and --domain with --noinput."):
            call_command('setupsite', interactive=False, site_name="Custom Site", stdout=output)

    def test_non_interactive_usage(self):
        output = StringIO()
        call_command(
            'setupsite',
            interactive=False,
            site_name=self.TEST_SITE_NAME,
            site_domain=self.TEST_SITE_DOMAIN,
            stdout=output
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Set site name as \"{}\" with domain \"{}\"".format(
            self.TEST_SITE_NAME,
            self.TEST_SITE_DOMAIN
        ))

        site = Site.objects.get()
        self.assertEqual(site.name,   self.TEST_SITE_NAME)
        self.assertEqual(site.domain, self.TEST_SITE_DOMAIN)

    @mock_inputs({
        'site name':   TEST_SITE_NAME,
        'site domain': TEST_SITE_DOMAIN
    })
    def test_interactive_usage(self):
        output = StringIO()
        call_command(
            'setupsite',
            interactive=True,
            stdout=output,
            stdin=MockTTY(),
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Set site name as \"{}\" with domain \"{}\"".format(
            self.TEST_SITE_NAME,
            self.TEST_SITE_DOMAIN
        ))
        site = Site.objects.get()
        self.assertEqual(site.name,   self.TEST_SITE_NAME)
        self.assertEqual(site.domain, self.TEST_SITE_DOMAIN)

    @mock_inputs({
        'site name':   "",
        'site domain': "",
    })
    def test_interactive_defaults_usage(self):
        output = StringIO()
        call_command(
            'setupsite',
            interactive=True,
            stdout=output,
            stdin=MockTTY(),
        )
        command_output = output.getvalue().strip()
        self.assertEqual(command_output, "Set site name as \"{}\" with domain \"{}\"".format(
            setupsite.Command.DEFAULT_SITE_NAME,
            setupsite.Command.DEFAULT_SITE_DOMAIN
        ))

        site = Site.objects.get()
        self.assertEqual(site.name,   setupsite.Command.DEFAULT_SITE_NAME)
        self.assertEqual(site.domain, setupsite.Command.DEFAULT_SITE_DOMAIN)

    def test_domain_validation(self):
        output = StringIO()
        test_domain = "+.,|!"
        with self.assertRaisesMessage(CommandError, "Domain name \"{}\" is not a valid domain name.".format(test_domain)):
            call_command(
                'setupsite',
                interactive=False,
                site_name=self.TEST_SITE_NAME,
                site_domain=test_domain,
                stdout=output
            )
