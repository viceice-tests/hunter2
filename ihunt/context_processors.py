from ihunt.utils import with_event
from ihunt.models import UserProfile


@with_event
def event_team(request, event):
    try:
        user = request.user.profile
        team = user.teams.get(at_event=event)
    except UserProfile.DoesNotExist:
        team = None

    return {
        'team': team
    }
