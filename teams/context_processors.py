def event_team(request):
    return {
        'event': request.event,
        'events': request.events,
        'team': request.team,
    }
