from ihunt.utils import with_event
from ihunt.models import UserProfile


@with_event
def event_team(request, event):
    try:
        if hasattr(request.user, 'profile'):
            user = request.user.profile
            team = user.teams.get(at_event=event)
        else:
            team = None
    except UserProfile.DoesNotExist:
        team = None

    return {
        'team': team
    }
