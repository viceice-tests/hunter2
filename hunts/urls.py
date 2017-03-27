from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

puzzlepatterns = [
    url('^$', views.Puzzle.as_view(), name='puzzle'),
    url('^an$', views.Answer.as_view(), name='answer'),
    url('^cb$', views.Callback.as_view(), name='callback'),
]

episodepatterns = [
    url('^$', views.Episode.as_view(), name='episode'),
    url('^pz/(?P<puzzle_number>[1-9]\d*)/', include(puzzlepatterns)),
]

eventpatterns = [
    url(
        r'^$',
        TemplateView.as_view(template_name='hunts/index.html'),
        name='index'
    ),
    url(r'^ep/(?P<episode_number>[1-9]\d*)/', include(episodepatterns)),
]

urlpatterns = [
    url(r'', include(eventpatterns)),
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
]
