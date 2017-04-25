# from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
# from django.utils.decorators import method_decorator
from django.views import View
from . import models


# @method_decorator(login_required, name='dispatch')
class Team(View):
    def get(self, request, team_id):
        team = get_object_or_404(
            models.Team, at_event=request.event, pk=team_id
        )
        return TemplateResponse(
            request,
            'teams/team.html',
            context={
                'team': team.name,
                'members': team.members.all(),
                'invites': team.invites.all(),
                'requests': team.requests.all(),
            }
        )
