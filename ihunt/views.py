from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import Guess
from . import rules
from .utils import answered, current_puzzle, episode_puzzle, event_episode

import logging


@login_required
def episode(request, episode_number):
    episode = event_episode(request.event, episode_number)
    admin = rules.is_admin_for_episode(request.user, episode)

    # TODO: Head starts
    if episode.start_date > timezone.now() and not admin:
        return render(
            request,
            'ihunt/futureepisode.html',
            {'episode': episode.name, 'startdate': episode.start_date}
        )

    puzzles = list(episode.puzzles.all())

    return render(
        request,
        'ihunt/episode.html',
        {
            'admin': admin,
            'episode': episode.name,
            'episode_number': episode_number,
            'event_id': request.event.pk,
            'puzzles': puzzles,
        }
    )


@login_required
def puzzle(request, episode_number, puzzle_number):
    episode = event_episode(request.event, episode_number)
    puzzle = episode_puzzle(episode, puzzle_number)
    admin = rules.is_admin_for_puzzle(request.user, puzzle)

    # TODO: May need caching of progress to avoid DB load
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

    return render(
        request,
        'ihunt/puzzle.html',
        {'admin': admin, 'puzzle': puzzle}
    )


@login_required
def hunt(request):
    user = request.user.profile
    event = request.event
    team = user.teams.get(at_event=event)

    now = timezone.now()
    episodes = list(
        event.episodes.filter(start_date__lt=now).order_by('start_date')
    )
    puzzle = current_puzzle(episodes, team)

    if puzzle is not None:
        if request.method == 'POST':
            given_answer = request.POST['answer']
            guess = Guess(
                guess=given_answer,
                for_puzzle=puzzle,
                by=get_user(request).profile
            )
            guess.save()
            if answered(puzzle, team):
                puzzle = current_puzzle(episodes, team)
                if puzzle is None:
                    return render(
                        request,
                        'ihunt/done.html',
                        {}
                    )
        return render(
            request,
            'ihunt/puzzle.html',
            {'puzzle': puzzle},
        )
    else:
        return render(
            request,
            'ihunt/done.html',
            {},
        )
