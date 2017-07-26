from django.conf.urls import include, url

from ..settings import DEBUG

if DEBUG:
    from .admin import admin_patterns
    from .www import www_patterns

    import debug_toolbar

    urlpatterns = admin_patterns + www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^silk/', include('silk.urls', namespace='silk')),
    ]
else:
    urlpatterns = []
