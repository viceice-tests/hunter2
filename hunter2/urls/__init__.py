from django.conf.urls import include, url
from django.views.defaults import page_not_found, server_error, bad_request, permission_denied
from django.views.csrf import csrf_failure

from ..settings import DEBUG, USE_SILK

if DEBUG:
    from .admin import admin_patterns
    from .www import www_patterns

    import debug_toolbar

    urlpatterns = admin_patterns + www_patterns + [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    # Http error code handlers (including CSRF validation)
    urlpatterns += [
        url(r'^test/http/400/$', bad_request, kwargs={'exception': Exception("Bad Request!")}),
        url(r'^test/http/403/$', permission_denied, kwargs={'exception': Exception("Permission Denied")}),
        url(r'^test/http/403/csrf/$', csrf_failure),
        url(r'^test/http/404/$', page_not_found, kwargs={'exception': Exception("Page not Found")}),
        url(r'^test/http/500/$', server_error),
    ]

    if USE_SILK:
        urlpatterns.append(
            url(r'^silk/', include('silk.urls', namespace='silk')),
        )
else:
    urlpatterns = []
