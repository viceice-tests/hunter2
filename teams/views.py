from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView

from accounts.models import UserProfile
from . import forms, models
from .forms import CreateTeamForm, InviteForm, RequestForm
from .mixins import TeamMixin

import json


class TeamAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = models.Team.objects.filter(at_event=self.request.tenant).order_by('name')

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class CreateTeamView(LoginRequiredMixin, TeamMixin, UpdateView):
    form_class = forms.CreateTeamForm
    template_name = 'teams/create.html'

    def get_object(self):
        return self.request.team

    def get_success_url(self):
        team_id = self.request.team.pk
        return reverse('team', kwargs={'team_id': team_id})


class ManageTeamView(LoginRequiredMixin, TeamMixin, View):
    def get(self, request):
        if request.team.is_explicit():
            invite_form = InviteForm()
            invites = request.team.invites.all()
            requests = request.team.requests.all()
            context = {
                'invite_form': invite_form,
                'invites': invites,
                'requests': requests,
            }
        else:
            invites = models.Team.objects.filter(invites=request.user.profile)
            requests = models.Team.objects.filter(requests=request.user.profile)
            create_form = CreateTeamForm(instance=request.team)
            request_form = RequestForm()
            context = {
                'invites': invites,
                'requests': requests,
                'create_form': create_form,
                'request_form': request_form,
            }
        return TemplateResponse(
            request,
            'teams/manage.html',
            context=context,
        )


class TeamView(LoginRequiredMixin, TeamMixin, View):
    def get(self, request, team_id):
        team = get_object_or_404(
            models.Team, at_event=request.tenant, pk=team_id
        )
        if not team.name:
            raise Http404
        else:
            return TemplateResponse(
                request,
                'teams/view.html',
                context={
                    'team': team.name,
                    'members': team.members.all(),
                    'invited': request.user.profile in team.invites.all(),
                    'requested': request.user.profile in team.requests.all(),
                }
            )


class Invite(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        user = request.user.profile
        if user not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a member to invite to a team',
            }, status=403)
        try:
            user = UserProfile.objects.get(pk=data['user'])
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
            }, status=400)
        if user in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has already been invited',
            }, status=400)
        if user.is_on_explicit_team(request.tenant):
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User is already a member of a team for this event',
            }, status=400)
        if team.is_full():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'This team is full',
            }, status=400)
        team.invites.add(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'User invited',
            'username': user.username,
        })


class CancelInvite(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        if request.user.profile not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a team member to cancel an invite',
            }, status=403)
        try:
            user = UserProfile.objects.get(pk=data['user'])
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
                'delete': True,
            }, status=400)
        if user not in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has not been invited',
                'delete': True,
            }, status=400)
        team.invites.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Invite cancelled',
        })


class AcceptInvite(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        user = request.user.profile
        if user not in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Not invited to this team',
                'delete': True,
            }, status=400)
        if user.is_on_explicit_team(request.tenant):
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Already on a team for this event',
                'delete': True,
            }, status=400)
        if team.is_full():
            team.invites.remove(user)
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'This team is full',
                'delete': True,
            }, status=400)
        old_team = request.user.profile.team_at(request.tenant)
        old_team.guess_set.update(by_team=team)
        old_team.delete()  # This is the user's implicit team, as checked above.
        user.team_invites.remove(*user.team_invites.filter(at_event=request.tenant))
        user.team_requests.remove(*user.team_requests.filter(at_event=request.tenant))
        team.members.add(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Invite accepted',
        })


class DenyInvite(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        user = request.user.profile
        if user not in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'You have not been invited',
                'delete': True,
            }, status=400)
        team.invites.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Invite denied',
        })


class Request(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        user = request.user.profile
        if user.is_on_explicit_team(request.tenant):
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Already a member of a team for this event',
            }, status=400)
        if user in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Already requested',
            }, status=400)
        if team.is_full():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'This team is full',
            }, status=400)
        team.requests.add(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Requested',
            'team': team.name,
        })


class CancelRequest(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        user = request.user.profile
        if user not in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Request does not exist',
                'delete': True,
            }, status=400)
        team.requests.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Requested cancelled',
        })


class AcceptRequest(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        if request.user.profile not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a team member to accept an request',
            }, status=403)
        try:
            user = UserProfile.objects.get(pk=data['user'])
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
                'delete': True,
            }, status=400)
        if user not in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has not requested to join',
                'delete': True,
            }, status=400)
        if user.is_on_explicit_team(request.tenant):
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Already a member of a team for this event',
                'delete': True,
            }, status=403)
        if team.is_full():
            team.requests.remove(user)
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'This team is full',
                'delete': True,
            }, status=400)
        old_team = user.team_at(request.tenant)
        old_team.guess_set.update(by_team=team)
        old_team.delete()  # This is the user's implicit team, as checked above.
        user.team_invites.remove(*user.team_invites.filter(at_event=request.tenant))
        user.team_requests.remove(*user.team_requests.filter(at_event=request.tenant))
        team.members.add(user)
        seat = user.attendance_at(request.tenant).seat
        return JsonResponse({
            'result': 'OK',
            'message': 'Request accepted',
            'username': user.username,
            'seat': seat,
        })


class DenyRequest(LoginRequiredMixin, TeamMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.tenant, pk=team_id)
        if request.user.profile not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a team member to deny an request',
            }, status=403)
        try:
            user = UserProfile.objects.get(pk=data['user'])
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
                'delete': True,
            }, status=400)
        if user not in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has not requested to join',
                'delete': True,
            }, status=400)
        team.requests.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Request denied',
        })
