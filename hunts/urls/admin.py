from django.conf.urls import include, url
from .. import views

eventpatterns = [
    url(r'^episode_list$', views.EpisodeList.as_view(), name='episode_list'),
    url(r'^guesses$', views.Guesses.as_view(), name='guesses'),
    url(r'^guesses_content$', views.GuessesContent.as_view(), name='guesses_content'),
    url(r'^stats$', views.Stats.as_view(), name='stats'),
    url(r'^stats_content/(?P<episode_id>[a-z0-9]+)$', views.StatsContent.as_view(), name='stats_content'),
]

urlpatterns = [
    url(r'^eventadmin/(?P<event_id>[1-9]\d*)/', include(eventpatterns)),
]
