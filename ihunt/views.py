from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from ihunt.models import Guess, Puzzle
from ihunt.utils import answered, current_puzzle, with_event


def dumb_template(template_name):
    """ Returns a view function that renders the template """
    def view_func(request):
        return render(request, template_name)
    return view_func


index = dumb_template('ihunt/index.html')
help = dumb_template('ihunt/help.html')
faq = dumb_template('ihunt/faq.html')


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


def login_view(request):
    if request.method == 'GET':
        return render(request, 'ihunt/login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('index')
        return render(
            request, 'ihunt/login.html', {'flash': 'Invalid login'}
        )


def logout_view(request):
    logout(request)
    return redirect('index')
