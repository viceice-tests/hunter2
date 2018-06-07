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
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from accounts.urls import urlpatterns as accounts_patterns
from teams.urls import urlpatterns as teams_patterns
from hunts.urls.www import urlpatterns as hunts_patterns

from .. import settings

www_patterns = [
    url(r'^accounts/', include('allauth.urls')),
] \
    + staticfiles_urlpatterns() \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + accounts_patterns \
    + teams_patterns \
    + hunts_patterns

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
else:
    urlpatterns = www_patterns
