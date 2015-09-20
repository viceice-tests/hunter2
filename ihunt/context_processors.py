def event_team(request):
    user = request.user.profile
    team = user.teams.get(at_event=event)

    return {
        'team': team
    }
