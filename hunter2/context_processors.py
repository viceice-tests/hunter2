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

from urllib.parse import urlparse

from django.urls import reverse

from .utils import wwwize
from . import settings


def login_url(request):
    return {
        'login_url': wwwize(reverse('account_login'), request),
    }


def sentry_dsn(request):
    dsn = settings.SENTRY_DSN
    if dsn:
        # If we have an old-style Sentry DSN with a password we need to strip it
        stripped = dsn._replace(netloc=f'{dsn.username}@{dsn.hostname}')
        dsn = stripped.geturl()
    return {
        'sentry_dsn': dsn,
    }
