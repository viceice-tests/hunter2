from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from .models import Guess
from . import rules
from . import runtime
from . import utils


@method_decorator(login_required, name='dispatch')
class Episode(View):
    def get(self, request, episode_number):
        episode = utils.event_episode(request.event, episode_number)
        admin = rules.is_admin_for_episode(request.user, episode)

        # TODO: Head starts
        if episode.start_date > timezone.now() and not admin:
            return TemplateResponse(
                request,
                'hunts/episodenotstarted.html',
                context={
                    'episode': episode.name,
                    'startdate': episode.start_date
                }
            )

        puzzles = list(episode.puzzles.all())

        return TemplateResponse(
            request,
            'hunts/episode.html',
            context={
                'admin': admin,
                'episode': episode.name,
                'episode_number': episode_number,
                'event_id': request.event.pk,
                'puzzles': puzzles,
            }
        )


@method_decorator(login_required, name='dispatch')
class Puzzle(View):
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
                    episode_number=episode_number
                )
            else:
                return redirect('episode', episode_number=episode_number)

        # TODO: May need caching of progress to avoid DB load
        if not puzzle.unlocked_by(request.team):
            return TemplateResponse(
                request, 'hunts/puzzlelocked.html', status=403
            )

        answered = puzzle.answered_by(request.team)

        t_data, u_data, tp_data, up_data = utils.puzzle_data(
            puzzle, request.team, request.user.profile
        )

        response = TemplateResponse(
            request,
            'hunts/puzzle.html',
            context={
                'answered': answered,
                'admin': admin,
                'title': puzzle.title,
                'clue': runtime.runtime_eval[puzzle.runtime](
                    puzzle.content,
                    {
                        't_data': t_data,
                        'u_data': u_data,
                        'tp_data': tp_data,
                        'up_data': up_data,
                    }
                )
            }
        )

        t_data.save()
        u_data.save()
        tp_data.save()
        up_data.save()

        return response


@method_decorator(login_required, name='dispatch')
class Answer(View):
    def post(self, request, episode_number, puzzle_number):
        episode, puzzle = utils.event_episode_puzzle(
            request.event, episode_number, puzzle_number
        )

        t_data, u_data, tp_data, up_data = utils.puzzle_data(
            puzzle, request.team, request.user
        )

        given_answer = request.POST['answer']
        guess = Guess(
            guess=given_answer,
            for_puzzle=puzzle,
            by=request.user.profile
        )
        guess.save()

        t_data.save()
        u_data.save()
        tp_data.save()
        up_data.save()


@method_decorator(login_required, name='dispatch')
class Callback(View):
    def post(self, request, episode_number, puzzle_number):
        if request.content_type != 'application/json':
            return HttpResponse(status=415)
        if 'application/json' not in request.META['HTTP_ACCEPT']:
            return HttpResponse(status=406)

        episode, puzzle = utils.event_episode_puzzle(
            request.event, episode_number, puzzle_number
        )

        t_data, u_data, tp_data, up_data = utils.puzzle_data(
            puzzle, request.team, request.user
        )

        response = HttpResponse(
            runtime.runtime_eval[puzzle.cb_runtime](
                puzzle.cb_content,
                {
                    't_data': t_data,
                    'u_data': u_data,
                    'tp_data': tp_data,
                    'up_data': up_data,
                }
            )
        )

        t_data.save()
        u_data.save()
        tp_data.save()
        up_data.save()

        return response
