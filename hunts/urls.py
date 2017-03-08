from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

import django.contrib.auth.urls

eventpatterns = [
    url(r'^hunt$', views.hunt, name='hunt'),
    url(
        r'^ep/(?P<episode_number>[1-9]\d*)$',
        views.episode,
        name='episode'
    ),
    url(
        r'^ep/(?P<episode_number>[1-9]\d*)/pz/(?P<puzzle_number>[1-9]\d*)$',
        views.puzzle,
        name='puzzle'
    ),
    url(
        r'^ep/(?P<episode_number>[1-9]\d*)/pz/(?P<puzzle_number>[1-9]\d*)/cb$',
        views.callback,
        name='callback'
    ),
    url(
        r'^$',
        TemplateView.as_view(template_name='hunts/index.html'),
        name='index'
    ),
]

urlpatterns = [
    url(r'^', include(django.contrib.auth.urls)),
    url(r'^event/(?P<event_id>[1-9]\d*)/', include(eventpatterns)),
    url(
        r'^faq$',
        TemplateView.as_view(template_name='hunts/faq.html'),
        name='faq'
    ),
    url(
        r'^help$',
        TemplateView.as_view(template_name='hunts/help.html'),
        name='help'
    ),
    url(r'^', include(eventpatterns)),
]
