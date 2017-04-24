from django.conf.urls import include, url
from django.conf.urls.static import static

from teams.urls import urlpatterns as teams_patterns
from hunts.urls import urlpatterns as hunts_patterns

from .. import settings

www_patterns = [
    url(r'^accounts/', include('allauth.urls')),
] \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
    + teams_patterns + hunts_patterns

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
else:
    urlpatterns = www_patterns
