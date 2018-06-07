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


from django.shortcuts import get_object_or_404
import logging

from .models import Event


class EventMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'event_id' in view_kwargs:
            event_id = view_kwargs['event_id']
            request.event = get_object_or_404(Event, pk=event_id)
            logging.debug(f'Explicit Event: {request.event}')
            # Remove the event_id kwarg in case views are not expecting it.
            del view_kwargs['event_id']
        else:
            try:
                request.event = Event.objects.filter(current=True).get()
                logging.debug(f'Implicit Event: {request.event}')
            except Event.DoesNotExist:
                request.event = None
        return
