from django.core.management import call_command
from django.test import TransactionTestCase
from django_tenants.test.cases import FastTenantTestCase

from .models import Event, Theme


class EventAwareTestCase(TransactionTestCase):

    def _fixture_teardown(self):
        for event in Event.objects.all():
            event.delete(force_drop=True)
        super()._fixture_teardown()


class EventTestCase(FastTenantTestCase):

    def setUp(self):
        if self.fixtures:
            call_command('tenant_command', 'loaddata', *self.fixtures,
                         **{'verbosity': 0, 'schema_name': self.tenant.schema_name})

    @classmethod
    def setup_tenant(cls, tenant):
        theme = Theme(name='Test Theme')
        theme.save()
        tenant.name = 'Test Event'
        tenant.theme = theme
