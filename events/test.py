from django.test import TransactionTestCase
from django.utils import timezone
from django_tenants.test.cases import FastTenantTestCase
from django_tenants.test.client import TenantClient

from .factories import ThemeFactory
from .models import Event


class EventAwareTestCase(TransactionTestCase):

    def _fixture_teardown(self):
        for event in Event.objects.all():
            event.delete(force_drop=True)
        super()._fixture_teardown()


class EventTestCase(FastTenantTestCase):
    def _pre_setup(self):
        super()._pre_setup()
        self.client = TenantClient(self.tenant)

    @classmethod
    def setup_tenant(cls, tenant):
        theme = ThemeFactory()
        tenant.end_date = timezone.now()
        tenant.name = 'Test Event'
        tenant.theme = theme
