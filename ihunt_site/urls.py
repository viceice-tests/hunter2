from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from hunts.urls import urlpatterns as app_patterns

from . import settings

import nested_admin.urls
import registration.backends.hmac.urls

urlpatterns = [
    url(r'^accounts/', include(registration.backends.hmac.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nested_admin/', include(nested_admin.urls)),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_URL) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
    + app_patterns

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
