from django.conf.urls import url
from django.contrib.sites.models import Site
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^', RedirectView.as_view(url=f'//www.{Site.objects.get_current().domain}'))
]
