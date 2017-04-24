# vim: set fileencoding=utf-8 :
from io import StringIO
from django.core.management import call_command
from django.test import TestCase, override_settings
from .utils import generate_secret_key, load_or_create_secret_key
import tempfile
import os


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
