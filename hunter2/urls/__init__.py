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


from django.conf.urls import include, url
from django.views.defaults import page_not_found, server_error, bad_request, permission_denied
from django.views.csrf import csrf_failure

from .. import settings

if settings.DEBUG:
    from .admin import admin_patterns
    from .www import www_patterns

    import debug_toolbar

    urlpatterns = admin_patterns + www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    # Http error code handlers (including CSRF validation)
    urlpatterns += [
        url(r'^test/http/400/$', bad_request, kwargs={'exception': Exception("Bad Request!")}),
        url(r'^test/http/403/$', permission_denied, kwargs={'exception': Exception("Permission Denied")}),
        url(r'^test/http/403/csrf/$', csrf_failure),
        url(r'^test/http/404/$', page_not_found, kwargs={'exception': Exception("Page not Found")}),
        url(r'^test/http/500/$', server_error),
    ]

    if settings.USE_SILK:  # nocover
        urlpatterns.append(
            url(r'^silk/', include('silk.urls', namespace='silk')),
        )
else:
    urlpatterns = []
