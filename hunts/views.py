from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from .models import Guess, TeamPuzzleData, UserPuzzleData
from . import rules
from . import runtime
from . import utils


@login_required
def episode(request, episode_number):
    episode = utils.event_episode(request.event, episode_number)
    admin = rules.is_admin_for_episode(request.user, episode)

    # TODO: Head starts
    if episode.start_date > timezone.now() and not admin:
        return TemplateResponse(
            request,
            'hunts/episodenotstarted.html',
            context={'episode': episode.name, 'startdate': episode.start_date}
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


@login_required
def puzzle(request, episode_number, puzzle_number):
    episode = utils.event_episode(request.event, episode_number)
    puzzle = episode.get_puzzle(puzzle_number)
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
        return TemplateResponse(request, 'hunts/puzzlelocked.html', status=403)

    if request.method == 'POST':
        given_answer = request.POST['answer']
        guess = Guess(
            guess=given_answer,
            for_puzzle=puzzle,
            by=request.user.profile
        )
        guess.save()

    answered = puzzle.answered_by(request.team)

    team_data, created = TeamPuzzleData.objects.get_or_create(
        puzzle=puzzle, team=request.team
    )
    user_data, created = UserPuzzleData.objects.get_or_create(
        puzzle=puzzle, user=request.user.profile
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
                    'team_data': team_data,
                    'user_data': user_data,
                }
            )
        }
    )

    team_data.save()
    user_data.save()

    return response


@login_required
def callback(request, episode_number, puzzle_number):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if request.content_type != 'application/json':
        return HttpResponse(status=415)
    if 'application/json' not in request.META['HTTP_ACCEPT']:
        return HttpResponse(status=406)

    episode = utils.event_episode(request.event, episode_number)
    puzzle = utils.episode_puzzle(episode, puzzle_number)

    team_data, created = TeamPuzzleData.objects.get_or_create(
        puzzle=puzzle, team=request.team
    )
    user_data, created = UserPuzzleData.objects.get_or_create(
        puzzle=puzzle, user=request.user.profile
    )

    response = HttpResponse(
        runtime.runtime_eval[puzzle.cb_runtime](
            puzzle.cb_content,
            {
                'team_data': team_data,
                'user_data': user_data,
            }
        )
    )

    team_data.save()
    user_data.save()

    return response


@login_required
def hunt(request):
    user = request.user.profile
    event = request.event
    team = user.teams.get(at_event=event)

    now = timezone.now()
    episodes = list(
        event.episodes.filter(start_date__lt=now).order_by('start_date')
    )
    puzzle = utils.current_puzzle(episodes, team)

    if puzzle is not None:
        if request.method == 'POST':
            given_answer = request.POST['answer']
            guess = Guess(
                guess=given_answer,
                for_puzzle=puzzle,
                by=get_user(request).profile
            )
            guess.save()
            if puzzle.answered_by(team):
                puzzle = utils.current_puzzle(episodes, team)
                if puzzle is None:
                    return TemplateResponse(
                        request,
                        'hunts/done.html',
                    )
        return TemplateResponse(
            request,
            'hunts/puzzle.html',
            context={'puzzle': puzzle},
        )
    else:
        return TemplateResponse(
            request,
            'hunts/done.html',
        )
