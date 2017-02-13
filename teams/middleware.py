import logging

from events.models import Event
from .models import Team, UserProfile

class TeamMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.events = None
        request.team = None

        try:
            user = request.user.profile
        except AttributeError:
            return
        except UserProfile.DoesNotExist:
            return

        request.events = set([t.at_event for t in user.teams.all()])
        request.events.add(Event.objects.filter(current=True).get())
        try:
            request.events.remove(request.event)
        except KeyError:
            # TODO: Requested event not in events list. Should we allow? 404?
            pass

        try:
            request.team = user.teams.get(at_event=request.event)
        except Team.DoesNotExist:
            request.team = None
            # TODO: User is not on a team for this event. Redirect to team creation?
            pass
        return
