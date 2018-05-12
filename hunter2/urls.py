from allauth.account.views import logout as allauth_logout
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.defaults import page_not_found, server_error, bad_request, permission_denied
from django.views.csrf import csrf_failure

from accounts.urls import urlpatterns as accounts_patterns
from hunts.urls import urlpatterns as hunts_patterns
from teams.urls import urlpatterns as teams_patterns

from . import settings

# Wrap the admin login page with login_required so that it goes through allauth login.
admin.site.login = login_required(admin.site.login)
# Replace the admin logout view with the allauth logout view.
# Unfortunately the admin UI makes a GET so we can't avoid the confirmation page.
admin.site.logout = allauth_logout

urlpatterns = [
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^nested_admin/', include('nested_admin.urls')),
] \
    + staticfiles_urlpatterns() \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + accounts_patterns \
    + hunts_patterns \
    + teams_patterns

if settings.DEBUG:

    import debug_toolbar

    urlpatterns += [
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

    if settings.USE_SILK:  # nocover
        urlpatterns.append(
            url(r'^silk/', include('silk.urls', namespace='silk')),
        )
