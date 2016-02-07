from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
import nested_admin

from ihunt.urls import urlpatterns as app_patterns

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nested_admin/', include('nested_admin.urls')),
] + app_patterns + static('/static/', document_root='static')
