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

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async as db_access
from urllib.parse import urlparse
import json

from events.models import Domain

class TestConsumer(AsyncWebsocketConsumer):
    @db_access
    def get_team(self):
        self.event.activate()
        self.team = self.user.profile.team_at(self.event)
    
    @db_access
    def get_event(self, domain):
        event = Domain.objects.get(domain=domain).tenant
        self.event = event

    async def connect(self):
        try:
            headers = dict(self.scope['headers'])
            try:
                origin = headers[b'origin']
            except KeyError:
                #await self.send(text_data=json.dumps({
                #    'error': 'Bad Request',
                #    'message': 'No Origin header',
                #}))
                #await self.close()
                return

            domain = urlparse(origin).hostname.decode('ascii')
            self.user = self.scope['user']
            await self.get_event(domain)
            await self.get_team()
            self.event.activate()
            print(self.team)
            await self.channel_layer.group_add('test_channel', self.channel_name)
            await self.accept()
        except Exception as e:
            print(e)
            raise

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('test_channel', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['message'] == 'hello':
            message = 'hello, ' + str(self.scope['user'])
        else:
            message = 'uwotm8'

        await self.send(text_data=json.dumps({
            'message': message,
        }))

    async def answer(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
        }))
