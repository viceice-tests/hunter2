from django.conf.urls import include, url
from django.contrib.auth.views import logout
from django.views.generic import TemplateView

import ihunt.views

eventpatterns = [
    url(r'hunt$', ihunt.views.hunt, name='hunt'),
    url(r'puzzle/(?P<puzzle_id>[0-9]+)$', ihunt.views.puzzle, name='puzzle'),
]

urlpatterns = [
    url(r'^event/(?P<event_id>[0-9]+)/', include(eventpatterns)),
    url(r'^$', TemplateView.as_view(template_name="ihunt/index.html"), name='index'),
    url(r'^faq$', TemplateView.as_view(template_name="ihunt/faq.html"), name='faq'),
    url(r'^help$', TemplateView.as_view(template_name="ihunt/help.html"), name='help'),
    url(r'^login$', ihunt.views.login_view, name='login'),
    url(r'^logout$', logout, name='logout'),
    url(r'', include(eventpatterns)),
]
