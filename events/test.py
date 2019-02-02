# Copyright (C) 2018 The Hunter2 Contributors.
#
# This file is part of Hunter2.
#
# Hunter2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Hunter2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with Hunter2.  If not, see <http://www.gnu.org/licenses/>.

from datetime import timedelta

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
            Event.deactivate()
        super()._fixture_teardown()


class EventTestCase(FastTenantTestCase):
    def _pre_setup(self):
        super()._pre_setup()
        self.client = TenantClient(self.tenant)

    @classmethod
    def setup_tenant(cls, tenant):
        theme = ThemeFactory()
        tenant.current = True
        tenant.end_date = timezone.now() + timedelta(days=5)
        tenant.name = 'Test Event'
        tenant.theme = theme
