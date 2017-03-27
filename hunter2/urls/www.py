from django.conf.urls import include, url
from django.conf.urls.static import static

from hunts.urls import urlpatterns as app_patterns

from .. import settings

import registration.backends.hmac.urls

urlpatterns = [
    url(r'^accounts/', include('allauth.urls')),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
    + app_patterns

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
