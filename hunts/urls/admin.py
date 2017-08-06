from django.conf.urls import include, url
from .. import views

eventpatterns = [
    url(r'^(?P<event_id>[1-9]\d*)/guesses$', views.Guesses.as_view(), name='guesses'),
    url(r'^(?P<event_id>[1-9]\d*)/guesses_content$', views.GuessesContent.as_view(), name='guesses_content'),
    url(r'^(?P<event_id>[1-9]\d*)/stats$', views.Stats.as_view(), name='stats'),
    url(r'^(?P<event_id>[1-9]\d*)/stats_content$', views.StatsContent.as_view(), name='stats_content'),
]

urlpatterns = [
    url(r'^eventadmin/', include(eventpatterns)),
]
