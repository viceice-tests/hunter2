from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .www import urlpatterns as www_patterns

from .. import settings

import nested_admin.urls
import registration.backends.hmac.urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nested_admin/', include(nested_admin.urls)),
] \
    + www_patterns

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
