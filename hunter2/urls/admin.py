from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from hunts.urls.admin import urlpatterns as hunts_patterns

from .. import settings

admin_patterns = [
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^nested_admin/', include('nested_admin.urls')),
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
