from ihunt.utils import with_event


@with_event
def event_team(request, event):
    user = request.user.profile
    team = user.teams.get(at_event=event)

    return {
        'team': team
    }
