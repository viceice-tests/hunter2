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

from urllib.parse import urlsplit, urlunsplit

from django.views.generic.base import RedirectView

from events.models import Event


class DefaultEventView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        event = Event.objects.get(current=True)
        domain = event.domains.first()
        uri = self.request.build_absolute_uri(self.uri)
        components = urlsplit(uri)
        try:
            port = components.netloc.split(':')[1]
            netloc = f'{domain.domain}:{port}'
        except IndexError:
            netloc = domain.domain
        return urlunsplit(components[:1] + (netloc,) + components[2:])


class DefaultIndexView(DefaultEventView):
    uri = '/'


class DefaultAdminView(DefaultEventView):
    uri = '/admin'
