from django.conf.urls import include, url
from django.conf.urls.static import static

from hunts.urls import urlpatterns as app_patterns

from .. import settings

import registration.backends.hmac.urls

urlpatterns = [
    url(r'^accounts/', include(registration.backends.hmac.urls)),
] + app_patterns + static('/static/', document_root='static')

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
