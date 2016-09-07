from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from ihunt.urls import urlpatterns as app_patterns

import nested_admin.urls
import registration.backends.hmac.urls

urlpatterns = [
    url(r'^accounts/', include(registration.backends.hmac.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nested_admin/', include(nested_admin.urls)),
] + app_patterns + static('/static/', document_root='static')
