from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from string import Template

from teams.mixins import TeamMixin

from . import models
from . import rules
from .runtimes.registry import RuntimesRegistry as rr
from . import utils

import events


class Index(View):
    def get(self, request):
        return TemplateResponse(
            request,
            'hunts/index.html',
        )


class Episode(LoginRequiredMixin, TeamMixin, View):
    def get(self, request, episode_number):
        episode = utils.event_episode(request.event, episode_number)
        admin = rules.is_admin_for_episode(request.user, episode)

        if not episode.started(request.team) and not admin:
            return TemplateResponse(
                request,
                'hunts/episodenotstarted.html',
                context={
                    'episode': episode.name,
                    'startdate': episode.start_date - episode.headstart_applied(request.team),
                    'headstart': episode.headstart_applied(request.team),
                }
            )

        # TODO: May need caching of progress to avoid DB load
        if not episode.unlocked_by(request.team):
            return TemplateResponse(
                request, 'hunts/episodelocked.html', status=403
            )

        all_puzzles = episode.puzzles.all()
        puzzles = []
        for p in all_puzzles:
            if p.unlocked_by(request.team):
                puzzles.append(p)

        positions = episode.finished_positions()
        if request.team in positions:
            position = positions.index(request.team)
            if position < 3:
                position = {0: 'first', 1: 'second', 2: 'third'}[position]
            else:
                position += 1
                position = f'in position {position}'
        else:
            position = None

        return TemplateResponse(
            request,
            'hunts/episode.html',
            context={
                'admin': admin,
                'episode': episode.name,
                'position': position,
                'episode_number': episode_number,
                'event_id': request.event.pk,
                'puzzles': puzzles,
            }
        )


class EventDirect(LoginRequiredMixin, View):
    def get(self, request):
        event = events.models.Event.objects.filter(current=True).get()

        return redirect(
            'event',
            event_id=event.id,
        )


class EventIndex(LoginRequiredMixin, View):
    def get(self, request):

        event = request.event

        episodes = models.Episode.objects \
                                 .filter(event=event.id) \
                                 .filter(start_date__lte=timezone.now()) \

        return TemplateResponse(
            request,
            'events/index.html',
            context={
                'event_title':  event.name,
                'event_id':     event.id,
                'episodes':     list(episodes),
            }
        )


#class Puzzle(LoginRequiredMixin, TeamMixin, View):
class Puzzle(LoginRequiredMixin, View):
    def get(self, request, episode_number, puzzle_number):
        episode, puzzle = utils.event_episode_puzzle(
            request.event, episode_number, puzzle_number
        )
        admin = rules.is_admin_for_puzzle(request.user, puzzle)

        # If episode has not started redirect to episode holding page
        if episode.start_date > timezone.now() and not admin:
            if request.event:
                return redirect(
                    'episode',
                    event_id=request.event.pk,
                    episode_number=episode_number,
                )
            else:
                return redirect('episode', episode_number=episode_number)

        # TODO: May need caching of progress to avoid DB load
        if not puzzle.unlocked_by(request.team):
            return TemplateResponse(
                request, 'hunts/puzzlelocked.html', status=403
            )

        data = models.PuzzleData(puzzle, request.team, request.user.profile)

        if not data.tp_data.start_time:
            data.tp_data.start_time = timezone.now()

        answered = reversed(puzzle.answered_by(request.team, data))
        hints = [
            h for h in puzzle.hint_set.all() if h.unlocked_by(request.team, data)
        ]
        unlocks = [
            {
                'guesses': u.unlocked_by(request.team, data),
                'text': u.text
            }
            for u in puzzle.unlock_set.all()
        ]
        unlocks = [u for u in unlocks if len(u['guesses'])]

        files = {f.slug: f.file.url for f in puzzle.puzzlefile_set.all()}

        text = Template(rr.evaluate(
            runtime=puzzle.runtime,
            script=puzzle.content,
            team_puzzle_data=data.tp_data,
            user_puzzle_data=data.up_data,
            team_data=data.t_data,
            user_data=data.u_data,
        )).safe_substitute(**files)

        response = TemplateResponse(
            request,
            'hunts/puzzle.html',
            context={
                'answered': answered,
                'admin': admin,
                'hints': hints,
                'title': puzzle.title,
                'text': text,
                'unlocks': unlocks,
            }
        )

        data.save()

        return response


class Answer(LoginRequiredMixin, TeamMixin, View):
    def post(self, request, episode_number, puzzle_number):
        episode, puzzle = utils.event_episode_puzzle(
            request.event, episode_number, puzzle_number
        )

        given_answer = request.POST['answer']
        guess = models.Guess(
            guess=given_answer,
            for_puzzle=puzzle,
            by=request.user.profile
        )
        guess.save()

        if request.event:
            return redirect(
                'puzzle',
                event_id=request.event.pk,
                episode_number=episode_number,
                puzzle_number=puzzle_number,
            )
        else:
            return redirect(
                'episode',
                episode_number=episode_number,
                puzzle_number=puzzle_number,
            )


class Callback(LoginRequiredMixin, TeamMixin, View):
    def post(self, request, episode_number, puzzle_number):
        if request.content_type != 'application/json':
            return HttpResponse(status=415)
        if 'application/json' not in request.META['HTTP_ACCEPT']:
            return HttpResponse(status=406)

        episode, puzzle = utils.event_episode_puzzle(
            request.event, episode_number, puzzle_number
        )

        data = models.PuzzleData(puzzle, request.team, request.user)

        response = HttpResponse(
            rr.evaluate(
                runtime=puzzle.cb_runtime,
                script=puzzle.cb_content,
                team_puzzle_data=data.tp_data,
                user_puzzle_data=data.up_data,
                team_data=data.t_data,
                user_data=data.u_data,
            )
        )

        data.save()

        return response


class PuzzleInfo(View):
    """View for translating a UUID "token" into information about a user's puzzle attempt"""
    def get(self, request):
        token = request.GET.get('token')
        if token is None:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Must provide token',
            }, status=400)
        try:
            up_data = models.UserPuzzleData.objects.get(token=token)
        except ValidationError:
            return JsonResponse({
                'result': 'Bad Request',
                'message': 'Token must be a UUID',
            }, status=400)
        except models.UserPuzzleData.DoesNotExist:
            return JsonResponse({
                'result': 'Not Found',
                'message': 'No such token',
            }, status=404)
        user = up_data.user
        team = up_data.team()
        return JsonResponse({
            'result': 'Success',
            'team_id': team.pk,
            'user_id': user.pk,
        })
