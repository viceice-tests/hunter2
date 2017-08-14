from django.conf.urls import include, url

from .. import settings

if settings.DEBUG:
    from .admin import admin_patterns
    from .www import www_patterns

    import debug_toolbar

    urlpatterns = admin_patterns + www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    if settings.USE_SILK:  # nocover
        urlpatterns.append(
            url(r'^silk/', include('silk.urls', namespace='silk')),
        )
else:
    urlpatterns = []
