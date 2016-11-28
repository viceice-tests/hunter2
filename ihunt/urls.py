from django.conf.urls import include, url
from django.views.generic import TemplateView
from ihunt.utils import with_event

import django.contrib.auth.urls
import ihunt.views

eventpatterns = [
    url(r'^hunt$', ihunt.views.hunt, name='hunt'),
    url(r'^puzzle/(?P<puzzle_id>[0-9]+)$', ihunt.views.puzzle, name='puzzle'),
    url(
        r'^$',
        with_event(TemplateView.as_view(template_name='ihunt/index.html')),
        name='index'
    ),
]

urlpatterns = [
    url(r'^', include(django.contrib.auth.urls)),
    url(r'^event/(?P<event_id>[0-9]+)/', include(eventpatterns)),
    url(
        r'^faq$',
        TemplateView.as_view(template_name='ihunt/faq.html'),
        name='faq'
    ),
    url(
        r'^help$',
        TemplateView.as_view(template_name='ihunt/help.html'),
        name='help'
    ),
    url(r'^', include(eventpatterns)),
]
