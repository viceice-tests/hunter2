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

from django.core.exceptions import ObjectDoesNotExist
from channels.generic.websocket import JsonWebsocketConsumer
import json

from events.models import Domain

def activate_tenant(f):
    def wrapper(self, *args, **kwargs):
        try:
            self.scope['tenant'].activate()
        except (AttributeError, KeyError):
            raise ValueError('%s has no scope or no tenant on its scope' % self)
        return f(self, *args, **kwargs)

    return wrapper


class TeamMixin:
    @activate_tenant
    def websocket_connect(self, message):
        # Add a team object to the scope. We can't do this in middleware because the user object
        # isn't resolved yet (I don't know what causes it to be resolved, either...) and we can't do
        # it in __init__ here because the middleware hasn't even run then, so we have no user or
        # tenant or anything!
        # This means this is a bit weirdly placed.
        try:
            user = self.scope['user'].profile
            self.team = user.team_at(self.scope['tenant'])
        except ObjectDoesNotExist:
            # A user on the website will never open the websocket without getting a userprofile and team.
            self.close()
            return
        return super().websocket_connect(message)


# MRO is important as long as TeamMixin uses websocket_connect().
class PuzzleEventWebsocket(TeamMixin, JsonWebsocketConsumer):
    def get_team(self):
        self.team = self.user.profile.team_at(self.scope['tenant'])

    @activate_tenant
    def connect(self):
        self.user = self.scope['user']
        print(self.team)
        self.channel_layer.group_add('test_channel', self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        self.channel_layer.group_discard('test_channel', self.channel_name)

    def receive_json(self, content):
        data = content
        if data['message'] == 'hello':
            message = 'hello, ' + str(self.scope['user'])
        else:
            message = 'uwotm8'

        self.send_json({
            'message': message,
        })

    def answer(self, event):
        message = event['message']

        self.send({
            'message': message,
        })
