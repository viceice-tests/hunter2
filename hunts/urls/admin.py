# Copyright (C) 2018 The Hunter2 Contributors.
#
# This file is part of Hunter2.
#
# Hunter2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Hunter2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with Hunter2.  If not, see <http://www.gnu.org/licenses/>.


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
