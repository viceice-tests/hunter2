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
            logging.debug('Explicit Event: {}'.format(request.event))
            # Remove the event_id kwarg in case views are not expecting it.
            del view_kwargs['event_id']
        else:
            try:
                request.event = Event.objects.filter(current=True).get()
                logging.debug('Implicit Event: {}'.format(request.event))
            except Event.DoesNotExist:
                request.event = None
        return
