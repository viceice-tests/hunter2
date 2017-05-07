# vim: set fileencoding=utf-8 :
import sys

import validators
from django.contrib.sites.models import Site
from django.core.management import BaseCommand, CommandError


# Based on createsuperuser:
# https://github.com/django/django/blob/master/django/contrib/auth/management/commands/createsuperuser.py
class Command(BaseCommand):
    help = 'Setup site name and domain'

    DEFAULT_SITE_NAME   = "Hunter 2"
    DEFAULT_SITE_DOMAIN = "hunter2.local"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            dest='site_name',
            type=str,
            help="Name for the site",
            default=None,
        )
        parser.add_argument(
            '--domain',
            dest='site_domain',
            type=str,
            help="Domain name the site will be served from",
            default=None,
        )
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            dest='interactive',
            help=(
                "Tells Django to NOT prompt the user for input of any kind. "
                "You must use --site and --domain with --noinput."
            ),
        )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super().execute(*args, **options)

    def handle(self, *args, **options):
        site_name = options['site_name']
        site_domain = options['site_domain']

        if not options['interactive']:
            if not site_name or not site_domain:
                raise CommandError("You must use --name and --domain with --noinput.")

        while site_name is None:
            site_name = self.get_input_data("Site name", default=self.DEFAULT_SITE_NAME)

        while site_domain is None:
            site_domain = self.get_input_data("Site domain", default=self.DEFAULT_SITE_DOMAIN)

        if not validators.domain(site_domain):
            raise CommandError("Domain name \"{}\" is not a valid domain name.".format(site_domain))

        site = Site.objects.get()
        site.domain = site_domain
        site.name = site_name
        site.save()

        self.stdout.write("Set site name as \"{}\" with domain \"{}\"".format(site_name, site_domain))

    @staticmethod
    def get_input_data(field, default=None):
        if default:
            message = "{} (leave blank to use \'{}\'): ".format(field, default)
        else:
            message = "{}:".format(field)
        value = input(message)
        if default and value == '':
            value = default
        return value
