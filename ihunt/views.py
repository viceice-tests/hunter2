from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import Guess
from .utils import answered, current_puzzle, episode_puzzle, event_episode

import logging


@login_required
def episode(request, episode_number):
    episode = event_episode(request.event, episode_number)
    puzzles = list(episode.puzzles.all())

    return render(request, 'ihunt/episode.html', {'episode': episode.name, 'puzzles': puzzles})


@login_required
def puzzle(request, episode_number, puzzle_number):
    episode = event_episode(request.event, episode_number)
    puzzle = episode_puzzle(episode, puzzle_number)

    return render(request, 'ihunt/puzzle.html', {'puzzle': puzzle})


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
