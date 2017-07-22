from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from string import Template
from datetime import timedelta
import json
from . import models
from . import rules
from .runtimes.registry import RuntimesRegistry as rr
from . import utils


class Index(View):
    def get(self, request):

        return TemplateResponse(
            request,
            'hunts/index.html',
        )


@method_decorator(login_required, name='dispatch')
class Episode(View):
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
class EventDirect(View):
    def get(self, request):
        event = models.Event.objects.filter(current=True).get()

        return redirect(
            'event',
            event_id=event.id,
        )


@method_decorator(login_required, name='dispatch')
class EventIndex(View):
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

        answered = puzzle.answered_by(request.team, data)
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
            runtime=puzzle.cb_runtime,
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


@method_decorator(login_required, name='dispatch')
class Answer(View):
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

        data = models.PuzzleData(puzzle, request.team)
        correct = any([a.validate_guess(guess, data) for a in puzzle.answer_set.all()])

        response = {}
        if correct:
            next = episode.next_puzzle(request.team)
            if next:
                response['url'] = reverse('puzzle', kwargs={'event_id': request.event.pk,
                                                            'episode_number': episode_number,
                                                            'puzzle_number': next})
            else:
                response['url'] = reverse('episode', kwargs={'event_id': request.event.pk,
                                                             'episode_number': episode_number})
        else:
            response['timeout'] = str(timezone.now() + timedelta(seconds=5))
        response['correct'] = str(correct).lower()

        return HttpResponse(json.dumps(response))

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

        data = models.PuzzleData(puzzle, request.team, request.user)

        response = HttpResponse(
            rr.evaluate(
                runtime=puzzle.cb_runtime,
                script=puzzle.content,
                team_puzzle_data=data.tp_data,
                user_puzzle_data=data.up_data,
                team_data=data.t_data,
                user_data=data.u_data,
            )
        )

        data.save()

        return response
