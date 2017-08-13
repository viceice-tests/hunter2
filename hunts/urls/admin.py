from django.conf.urls import include, url
from .. import views

eventpatterns = [
    url(r'^guesses$', views.Guesses.as_view(), name='guesses'),
    url(r'^guesses_content$', views.GuessesContent.as_view(), name='guesses_content'),
]

urlpatterns = [
    url(r'^eventadmin/(?P<event_id>[1-9]\d*)/', include(eventpatterns)),
]
