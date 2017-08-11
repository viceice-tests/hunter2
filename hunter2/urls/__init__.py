from django.conf.urls import include, url

from ..settings import DEBUG, USE_SILK

if DEBUG:
    from .admin import admin_patterns
    from .www import www_patterns

    import debug_toolbar

    urlpatterns = admin_patterns + www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    if USE_SILK:  # nocover
        urlpatterns.append(
            url(r'^silk/', include('silk.urls', namespace='silk')),
        )
else:  # nocover
    urlpatterns = []
