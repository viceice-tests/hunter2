def event_team(request):
    return {
        'event': request.tenant,
        'events': request.events,
        'team': request.team,
    }
