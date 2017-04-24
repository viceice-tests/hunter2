from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^team/(?P<team_id>[1-9]\d*)', views.Team.as_view(), name='team'),
]
