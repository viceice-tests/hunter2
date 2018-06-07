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


from allauth.account.views import logout as allauth_logout
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from hunts.urls.admin import urlpatterns as hunts_patterns

from .. import settings

# Wrap the admin login page with login_required so that it goes through allauth login.
admin.site.login = login_required(admin.site.login)
# Replace the admin logout view with the allauth logout view.
# Unfortunately the admin UI makes a GET so we can't avoid the confirmation page.
admin.site.logout = allauth_logout

admin_patterns = [
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^admin/uwsgi/', include('django_uwsgi.urls')),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
    + hunts_patterns

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = admin_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
else:
    urlpatterns = admin_patterns
