from django.shortcuts import get_object_or_404
from .models import Event

import logging
import traceback


def with_event(f):
    """ Returns a wed function that receives an `event` kwarg """

    def view_func(request, event_id=None, *args, **kwargs):
        logging.debug(traceback.format_stack())
        if event_id is not None:
            logging.debug('Event ID: {}'.format(event_id))
            event = get_object_or_404(Event, pk=event_id)
            logging.debug('Event: {}'.format(event))
        else:
            try:
                event = Event.objects.filter(current=True).get()
            except Event.DoesNotExist:
                event = None

        return f(request, event=event, *args, **kwargs)

    return view_func
