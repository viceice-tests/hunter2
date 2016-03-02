from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from ihunt.models import Guess, Puzzle
from ihunt.utils import answered, current_puzzle, with_event


@login_required
@with_event
def puzzle(request, puzzle_id, event=None):
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)

    return render(
        request,
        'ihunt/puzzle.html',
        {'puzzle': puzzle}
    )


@login_required
@with_event
def hunt(request, event=None):
    user = request.user.profile
    team = user.teams.get(at_event=event)

    now = timezone.now()
    puzzlesets = list(
        event.puzzlesets.filter(start_date__lt=now).order_by('start_date')
    )
    puzzle = current_puzzle(puzzlesets, team)

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
                puzzle = current_puzzle(puzzlesets, team)
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
