# vim: set fileencoding=utf-8 :
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import UserProfile
from .models import Team


class TeamMixin():
    def dispatch(self, request, *args, **kwargs):
        try:
            user = request.user.profile
        except ObjectDoesNotExist:
            user = UserProfile(user=request.user)
            user.save()
        # TODO: May conflict with assignment of request.team in TeamMiddleware but shouldn't cause problems
        try:
            request.team = user.team_at(request.tenant)
        except ObjectDoesNotExist:
            request.team = Team(name='', at_event=request.tenant)
            request.team.save()
            request.team.members.add(user)
        return super().dispatch(request, *args, **kwargs)
