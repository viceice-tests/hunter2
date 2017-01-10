from django.conf.urls import include, url
from django.views.generic import TemplateView

import django.contrib.auth.urls
import ihunt.views

eventpatterns = [
    url(r'^hunt$', ihunt.views.hunt, name='hunt'),
    url(
        r'^ep/(?P<episode_number>[1-9]\d*)',
        ihunt.views.episode,
        name='episode'
    ),
    url(
        r'^ep/(?P<episode_number>[1-9]\d*)/pz/(?P<puzzle_number>[1-9]\d*)$',
        ihunt.views.puzzle,
        name='puzzle'
    ),
    url(
        r'^$',
        TemplateView.as_view(template_name='ihunt/index.html'),
        name='index'
    ),
]

urlpatterns = [
    url(r'^', include(django.contrib.auth.urls)),
    url(r'^event/(?P<event_id>[1-9]\d*)/', include(eventpatterns)),
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
