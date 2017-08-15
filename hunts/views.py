from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from hunter2.resolvers import reverse
from string import Template
from teams.mixins import TeamMixin
from collections import defaultdict

from . import models
from . import rules
from . import utils
from .runtimes.registry import RuntimesRegistry as rr

import events
import teams


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

        puzzles = episode.unlocked_puzzles(request.team)

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

        files = {f.slug: f.file.url for f in request.event.eventfile_set.all()}
        flavour = Template(episode.flavour).safe_substitute(**files)

        return TemplateResponse(
            request,
            'hunts/episode.html',
            context={
                'admin': admin,
                'episode': episode.name,
                'flavour': flavour,
                'position': position,
                'episode_number': episode_number,
                'event_id': request.event.pk,
                'puzzles': puzzles,
            }
        )


class EpisodeList(LoginRequiredMixin, View):
    def get(self, request):
        admin = rules.is_admin_for_event(request.user, request.event)

        if not admin:
            raise PermissionDenied

        return JsonResponse([{
            'id': episode.pk,
            'name': episode.name
        } for episode in models.Episode.objects.filter(event=request.event)], safe=False)


class Guesses(LoginRequiredMixin, View):
    def get(self, request):
        admin = rules.is_admin_for_event(request.user, request.event)

        if not admin:
            raise PermissionDenied

        return TemplateResponse(
            request,
            'hunts/guesses.html',
        )


class GuessesContent(LoginRequiredMixin, View):
    def get(self, request):
        admin = rules.is_admin_for_event(request.user, request.event)

        if not admin:
            return HttpResponseForbidden()

        episode = request.GET.get('episode')
        puzzle = request.GET.get('puzzle')
        team = request.GET.get('team')

        puzzles = models.Puzzle.objects.filter(episode__event=request.event)
        if puzzle:
            puzzles = puzzles.filter(id=puzzle)
        if episode:
            puzzles = puzzles.filter(episode=episode)

        all_guesses = models.Guess.objects.filter(
            for_puzzle__in=puzzles
        ).order_by(
            '-given'
        )

        if team:
            team = teams.models.Team.objects.get(id=team)
            all_guesses = all_guesses.filter(by__in=team.members.all())

        guess_pages = Paginator(all_guesses, 50)
        page = request.GET.get('page')
        try:
            guesses = guess_pages.page(page)
        except PageNotAnInteger:
            guesses = guess_pages.page(1)
        except EmptyPage:
            guesses = guess_pages.page(guess_pages.num_pages)

        if request.GET.get('highlight_unlocks'):
            for g in guesses:
                unlockanswers = models.UnlockAnswer.objects.filter(unlock__puzzle=g.for_puzzle)
                if any([a.validate_guess(g) for a in unlockanswers]):
                    g.unlocked = True

        return TemplateResponse(
            request,
            'hunts/guesses_content.html',
            context={
                'event_id': request.event.pk,
                'guesses': guesses,
            }
        )


class Stats(LoginRequiredMixin, View):
    def get(self, request):
        admin = rules.is_admin_for_event(request.user, request.event)

        if not admin:
            raise PermissionDenied

        return TemplateResponse(
            request,
            'hunts/stats.html',
        )


class StatsContent(LoginRequiredMixin, View):
    def get(self, request, episode_id):
        admin = rules.is_admin_for_event(request.user, request.event)

        if not admin:
            raise PermissionDenied

        # TODO select and prefetch all the things
        episodes = models.Episode.objects.filter(event=request.event)
        if episode_id != 'all':
            episodes = episodes.filter(pk=episode_id)
            if not episodes.count():
                raise Http404

        # Directly use the through relation for sorted M2M so we can sort the entire query.
        episode_puzzles = models.Episode.puzzles.through.objects.filter(episode__in=episodes).select_related('puzzle')
        puzzles = [ep.puzzle for ep in episode_puzzles.order_by('episode', 'sort_value')]

        all_teams = teams.models.Team.objects.annotate(
            num_members=Count('members')
        ).filter(
            at_event=request.event, num_members__gte=1
        )

        # Get the first correct guess for each team on each puzzle.
        # We use Guess.correct_for (i.e. the cache) because otherwise we perform a query for every
        # (team, puzzle) pair i.e. a butt-ton. This comes at the cost of possibly seeing
        # a team doing worse than it really is.
        all_guesses = models.Guess.objects.filter(for_puzzle__in=puzzles, correct_for__isnull=False).select_related('for_puzzle', 'by_team')
        correct_guesses = defaultdict(dict)
        for guess in all_guesses:
            team_guesses = correct_guesses[guess.for_puzzle]
            if guess.by_team not in team_guesses or guess.given < team_guesses[guess.by_team].given:
                team_guesses[guess.by_team] = guess

        # The time of the latest correct guess, plus some padding which I cba to add in JS
        end_time = max([
            guesses.given
            for team_guesses in correct_guesses.values()
            for guesses in team_guesses.values() if guesses
        ]) + timedelta(minutes=10)

        puzzle_datas = models.TeamPuzzleData.objects.filter(puzzle__in=puzzles, team__in=all_teams).select_related('puzzle', 'team')
        start_times = defaultdict(lambda: defaultdict(dict))
        solved_times = defaultdict(list)
        for data in puzzle_datas:
            if data.team in correct_guesses[data.puzzle] and data.start_time:
                start_times[data.team][data.puzzle] = None
                solved_times[data.puzzle].append(correct_guesses[data.puzzle][data.team].given - data.start_time)
            else:
                start_times[data.team][data.puzzle] = data.start_time

        # TODO: use something more intelligent here. Episode end time once we have it...
        now = timezone.now()

        stuckness = {
            team: [
                now - start for start in start_times[team].values() if start
            ] for team in all_teams
        }
        active_teams = {
            puzzle: len([1 for t in all_teams if start_times[t][puzzle]])
            for puzzle in puzzles
        }

        puzzle_progress = [
            {
                'team': t.name,
                'progress': [{
                    'puzzle': p.title,
                    'time': correct_guesses[p][t].given
                } for p in puzzles if t in correct_guesses[p]]
            } for t in all_teams
        ]
        puzzle_completion = [
            {
                'puzzle': p.title,
                'completion': len(correct_guesses[p])
            } for p in puzzles]
        team_puzzle_stuckness = [
            {
                'team': t.name,
                'puzzleStuckness': [{
                    'puzzle': p.title,
                    'stuckness': (now - start_times[t][p]).total_seconds()
                } for p in puzzles if start_times[t][p]]
            } for t in all_teams]
        team_total_stuckness = [
            {
                'team': t.name,
                'stuckness': sum(stuckness[t], timedelta()).total_seconds(),
            } for t in all_teams]
        puzzle_average_stuckness = [
            {
                'puzzle': p.title,
                'stuckness': sum([
                    now - start_times[t][p] for t in all_teams if start_times[t][p]
                ], timedelta()).total_seconds() / active_teams[p]
            } for p in puzzles if active_teams[p] > 0]
        puzzle_difficulty = [
            {
                'puzzle': p.title,
                'average_time': sum(solved_times[p], timedelta()).total_seconds() / len(solved_times[p])
            } for p in puzzles if solved_times[p]]

        data = {
            'teams': [t.name for t in all_teams],
            'numTeams': all_teams.count(),
            'startTime': min([e.start_date for e in episodes]),
            'endTime': end_time,
            'puzzles': [p.title for p in puzzles],
            'puzzleCompletion': puzzle_completion,
            'puzzleProgress': puzzle_progress,
            'teamTotalStuckness': team_total_stuckness,
            'teamPuzzleStuckness': team_puzzle_stuckness,
            'puzzleAverageStuckness': puzzle_average_stuckness,
            'puzzleDifficulty': puzzle_difficulty
        }
        return JsonResponse(data)


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
            'hunts/event.html',
            context={
                'event_title':  event.name,
                'event_id':     event.id,
                'episodes':     list(episodes),
            }
        )


class Puzzle(LoginRequiredMixin, TeamMixin, View):
    def get(self, request, episode_number, puzzle_number):
        episode, puzzle = utils.event_episode_puzzle(
            request.event, episode_number, puzzle_number
        )
        admin = rules.is_admin_for_puzzle(request.user, puzzle)

        # Make the puzzle available on the request object
        request.puzzle = puzzle

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
            if not (admin and request.GET.get('preview')):
                return TemplateResponse(
                    request, 'hunts/puzzlelocked.html', status=403
                )

        data = models.PuzzleData(puzzle, request.team, request.user.profile)

        if not data.tp_data.start_time:
            data.tp_data.start_time = timezone.now()

        answered = puzzle.answered_by(request.team)
        hints = [
            h for h in puzzle.hint_set.all() if h.unlocked_by(request.team, data)
        ]
        unlocks = []
        for u in puzzle.unlock_set.all():
            guesses = u.unlocked_by(request.team)
            if not guesses:
                continue

            guesses = [g.guess for g in guesses]
            # Get rid of duplicates but preserve order
            duplicates = set()
            guesses = [g for g in guesses if not (g in duplicates or duplicates.add(g))]
            unlocks.append({'guesses': guesses, 'text': u.text})

        files = {
            **{f.slug: f.file.url for f in request.event.eventfile_set.all()},
            **{f.slug: f.file.url for f in puzzle.puzzlefile_set.all()},
        }  # Puzzle files with matching slugs override hunt counterparts

        text = Template(rr.evaluate(
            runtime=puzzle.runtime,
            script=puzzle.content,
            team_puzzle_data=data.tp_data,
            user_puzzle_data=data.up_data,
            team_data=data.t_data,
            user_data=data.u_data,
        )).safe_substitute(**files)

        flavour = Template(puzzle.flavour).safe_substitute(**files)

        response = TemplateResponse(
            request,
            'hunts/puzzle.html',
            context={
                'answered': answered,
                'admin': admin,
                'hints': hints,
                'title': puzzle.title,
                'flavour': flavour,
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

        minimum_time = timedelta(seconds=5)
        try:
            latest_guess = models.Guess.objects.filter(
                for_puzzle=puzzle,
                by=request.user.profile
            ).order_by(
                '-given'
            )[0]
        except IndexError:
            pass
        else:
            if latest_guess.given + minimum_time > timezone.now():
                return JsonResponse({'error': 'too fast'}, status=429)

        data = models.PuzzleData(puzzle, request.team)

        last_updated = request.POST.get('last_updated')
        if last_updated and data.tp_data.start_time:
            last_updated = datetime.fromtimestamp(int(last_updated) // 1000, timezone.utc)
            new_hints = puzzle.hint_set.filter(
                time__gt=(last_updated - data.tp_data.start_time),
                time__lt=(timezone.now() - data.tp_data.start_time),
            )
            new_hints = [{'time': str(hint.time), 'text': hint.text} for hint in new_hints]
        else:
            new_hints = []

        # Put answer in DB
        given_answer = request.POST['answer']
        guess = models.Guess(
            guess=given_answer,
            for_puzzle=puzzle,
            by=request.user.profile
        )
        guess.save()

        correct = any([a.validate_guess(guess) for a in puzzle.answer_set.all()])

        # Build the response JSON depending on whether the answer was correct
        response = {}
        if correct:
            next = episode.next_puzzle(request.team)
            if next:
                response['url'] = reverse('puzzle', subdomain=request.subdomain,
                                          kwargs={'event_id': request.event.pk,
                                                  'episode_number': episode_number,
                                                  'puzzle_number': next})
            else:
                response['url'] = reverse('episode', subdomain=request.subdomain,
                                          kwargs={'event_id': request.event.pk,
                                                  'episode_number': episode_number}, )
        else:
            all_unlocks = models.Unlock.objects.filter(puzzle=puzzle)
            unlocks = []
            for u in all_unlocks:
                correct_guesses = u.unlocked_by(request.team)
                if not correct_guesses:
                    continue

                guesses = [g.guess for g in correct_guesses]
                # Get rid of duplicates but preserve order
                duplicates = set()
                guesses = [g for g in guesses if not (g in duplicates or duplicates.add(g))]
                unlocks.append({'guesses': guesses,
                                'text': u.text,
                                'new': guess in correct_guesses})

            response['guess'] = given_answer
            response['timeout'] = str(timezone.now() + minimum_time)
            response['new_hints'] = new_hints
            response['unlocks'] = unlocks
        response['correct'] = str(correct).lower()

        return JsonResponse(response)


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


class AboutView(TemplateView):
    template_name = 'hunts/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_team = self.request.event.teams.get(is_admin=True)

        files = {f.slug: f.file.url for f in self.request.event.eventfile_set.all()}
        content = Template(self.request.event.about_text).safe_substitute(**files)

        context.update({
            'admins': admin_team.members.all(),
            'content': content,
            'event_name': self.request.event.name,
        })
        return context


class RulesView(TemplateView):
    template_name = 'hunts/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        files = {f.slug: f.file.url for f in self.request.event.eventfile_set.all()}
        content = Template(self.request.event.rules_text).safe_substitute(**files)

        context.update({
            'content': content,
            'event_name': self.request.event.name,
        })
        return context
