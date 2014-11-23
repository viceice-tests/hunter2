from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from ihunt.urls import urlpatterns as app_patterns

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ihunt.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
) + app_patterns + static('/static/', document_root='static')
