from events.utils import with_event
from .models import Event, Team, UserProfile


@with_event
def event_team(request, event):
    try:
        user = request.user.profile
        events = set([t.at_event for t in user.teams.all()])
        events.add(Event.objects.filter(current=True).get())
        events.remove(event)
        team = user.teams.get(at_event=event)
    except AttributeError:
        # User is probably anonymous
        events = []
        team = None
    except UserProfile.DoesNotExist:
        events = []
        team = None
    except Team.DoesNotExist:
        team = None

    return {
        'event': event,
        'events': events,
        'team': team
    }
