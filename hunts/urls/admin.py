from django.conf.urls import include, url
from .. import views

eventpatterns = [
    url(r'^(?P<event_id>[1-9]\d*)/guesses$', views.Guesses.as_view(), name='guesses'),
    url(r'^(?P<event_id>[1-9]\d*)/guesses_content$', views.GuessesContent.as_view(), name='guesses_content'),
    url(r'^(?P<event_id>[1-9]\d*)/stats$', views.Stats.as_view(), name='stats'),
    url(r'^(?P<event_id>[1-9]\d*)/stats_content/(?P<episode_id>[a-z0-9]+)$', views.StatsContent.as_view(), name='stats_content'),
    url(r'^(?P<event_id>[1-9]\d*)/episode_list$', views.EpisodeList.as_view(), name='episode_list'),
]

urlpatterns = [
    url(r'^eventadmin/', include(eventpatterns)),
]
