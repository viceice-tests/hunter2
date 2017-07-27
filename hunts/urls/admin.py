from django.conf.urls import include, url
from .. import views

eventpatterns = [
    url(r'^(?P<event_id>[1-9]\d*)/guesses$', views.Guesses.as_view(), name='guesses'),
    url(r'^(?P<event_id>[1-9]\d*)/guesses_content$', views.GuessesContent.as_view(), name='guesses_content'),
]

urlpatterns = [
    url(r'^eventadmin/', include(eventpatterns)),
]
