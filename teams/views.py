from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic import CreateView
from . import forms, models

import json


class UserProfileAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    raise_exception = True

    def get_queryset(self):
        qs = models.UserProfile.objects.exclude(pk=self.request.user.profile.pk)

        if self.q:
            qs = qs.filter(
                Q(user__username__startswith=self.q) |
                Q(user__email__startswith=self.q)
            )

        return qs


class TeamCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.TeamForm
    template_name = 'teams/team_form.html'

    def get_form_kwargs(self):
        kwargs = super(TeamCreateView, self).get_form_kwargs()
        kwargs['event'] = self.request.event
        kwargs['user'] = self.request.user.profile
        return kwargs


class Team(LoginRequiredMixin, View):
    def get(self, request, team_id):
        team = get_object_or_404(
            models.Team, at_event=request.event, pk=team_id
        )
        if team == request.team:
            invite_form = forms.InviteForm()
            return TemplateResponse(
                request,
                'teams/team_member.html',
                context={
                    'team': team.name,
                    'members': team.members.all(),
                    'invites': team.invites.all(),
                    'requests': team.requests.all(),
                    'invite_form': invite_form,
                }
            )
        else:
            return TemplateResponse(
                request,
                'teams/team_viewer.html',
                context={
                    'team': team.name,
                    'members': team.members.all(),
                    'invited': request.user.profile in team.invites.all(),
                    'requested': request.user.profile in team.requests.all(),
                    'requestable': request.team is None,
                }
            )


class Invite(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        user = request.user.profile
        if user not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a member to invite to a team',
            }, status=403)
        try:
            user = models.UserProfile.objects.get(pk=data['user'])
        except models.UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
            }, status=400)
        if user in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has already been invited',
            }, status=400)
        if models.Team.objects.filter(at_event=request.event, members=user).count() > 0:
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
            'username': user.user.username,
        })


class CancelInvite(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        if request.user.profile not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a team member to cancel an invite',
            }, status=403)
        try:
            user = models.UserProfile.objects.get(pk=data['user'])
        except models.UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
            }, status=400)
        if user not in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has not been invited',
            }, status=400)
        team.invites.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Invite cancelled',
        })


class AcceptInvite(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        user = request.user.profile
        if user not in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Not invited to this team',
            }, status=400)
        if models.Team.objects.filter(at_event=request.event, members=user).count() > 0:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Already on a team for this event',
            }, status=400)
        if team.is_full():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'This team is full',
            }, status=400)
        team.invites.remove(user)
        team.members.add(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Invite accepted',
        })


class DenyInvite(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        user = request.user.profile
        if user not in team.invites.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'You have not been invited',
            }, status=400)
        team.invites.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Invite denied',
        })


class Request(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        user = request.user.profile
        if models.Team.objects.filter(at_event=request.event, members=user).count() > 0:
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
        })


class CancelRequest(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        user = request.user.profile
        if user not in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Request does not exist',
            }, status=400)
        team.requests.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Requested cancelled',
        })


class AcceptRequest(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        if request.user.profile not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a team member to accept an request',
            }, status=403)
        try:
            user = models.UserProfile.objects.get(pk=data['user'])
        except models.UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
            }, status=400)
        if user not in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has not requested to join',
            }, status=400)
        if models.Team.objects.filter(at_event=request.event, members=user).count() > 0:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Already a member of a team for this event',
            }, status=403)
        if team.is_full():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'This team is full',
            }, status=400)
        team.members.add(user)
        team.requests.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Request accepted',
            'username': user.user.username,
        })


class DenyRequest(LoginRequiredMixin, View):
    raise_exception = True

    def post(self, request, team_id):
        data = json.loads(request.body)
        team = get_object_or_404(models.Team, at_event=request.event, pk=team_id)
        if request.user.profile not in team.members.all():
            return JsonResponse({
                'result': 'Forbidden',
                'message': 'Must be a team member to deny an request',
            }, status=403)
        try:
            user = models.UserProfile.objects.get(pk=data['user'])
        except models.UserProfile.DoesNotExist:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User does not exist',
            }, status=400)
        if user not in team.requests.all():
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'User has not requested to join',
            }, status=400)
        team.requests.remove(user)
        return JsonResponse({
            'result': 'OK',
            'message': 'Request denied',
        })
