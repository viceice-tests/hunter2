from events.models import Event
from events.utils import with_event
from .models import Team, UserProfile

import logging


@with_event
def event_team(request, event):
    try:
        user = request.user.profile
        events = set([t.at_event for t in user.teams.all()])
        events.add(Event.objects.filter(current=True).get())
        events.remove(event)
        logging.debug('Event: {}'.format(event))
        logging.debug('Teams? {}'.format(user.teams))
        team = user.teams.get(at_event=event)
    except AttributeError:
        # User is probably anonymous
        events = []
        team = None
    except UserProfile.DoesNotExist:
        logging.warning('Page load by a user with no profile')
        events = []
        team = None
    except Team.DoesNotExist:
        logging.warning('User is not a member of a team')
        team = None

    return {
        'event': event,
        'events': events,
        'team': team
    }
