from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

puzzlepatterns = [
    url(r'^$', views.Puzzle.as_view(), name='puzzle'),
    url(r'^an$', views.Answer.as_view(), name='answer'),
    url(r'^cb$', views.Callback.as_view(), name='callback'),
]

episodepatterns = [
    url(r'^$', views.Episode.as_view(), name='episode'),
    url(r'^pz/(?P<puzzle_number>[1-9]\d*)/', include(puzzlepatterns)),
]

eventpatterns = [
    url(r'^$', views.EventDirect.as_view()),
    url(
        r'^(?P<event_id>[1-9]\d*)/$',
        views.EventIndex.as_view(),
        name='event'),
    url(
        r'^(?P<event_id>[1-9]\d*)/ep/(?P<episode_number>[1-9]\d*)/',
        include(episodepatterns)
    ),
]

urlpatterns = [
    url(
        r'^$',
        views.Index.as_view(),
        name='index'
    ),
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
    url(r'^event/', include(eventpatterns)),
    url(r'^puzzle_info$', views.PuzzleInfo.as_view(), name='puzzle_info'),
]
