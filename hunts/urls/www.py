from django.conf.urls import include, url
from .. import views
from django.views.generic import TemplateView

puzzlepatterns = [
    url(r'^$', views.Puzzle.as_view(), name='puzzle'),
    url(r'^an$', views.Answer.as_view(), name='answer'),
    url(r'^cb$', views.Callback.as_view(), name='callback'),
]

episodepatterns = [
    url(r'^$', views.Episode.as_view(), name='episode'),
    url(r'^content$', views.EpisodeContent.as_view(), name='episode_content'),
    url(r'^pz/(?P<puzzle_number>[1-9]\d*)/', include(puzzlepatterns)),
]

eventpatterns = [
    url(r'^$', views.EventIndex.as_view(), name='event'),
    url(r'^about$', views.AboutView.as_view(), name='about'),
    url(r'^rules$', views.RulesView.as_view(), name='rules'),
    url(r'^help$', views.HelpView.as_view(), name='help'),
    url(r'^examples$', views.ExamplesView.as_view(), name='examples'),
    url(r'^ep/(?P<episode_number>[1-9]\d*)/', include(episodepatterns)),
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
    url(r'^event/$', views.EventDirect.as_view()),
    url(r'^event/(?P<event_id>[1-9]\d*)/', include(eventpatterns)),
    url(r'^puzzle_info$', views.PuzzleInfo.as_view(), name='puzzle_info'),
]
