from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.utils import timezone
from ihunt.models import Event, Guess, Puzzle, PuzzleSet
from ihunt.utils import answered, current_puzzle, with_event


def render_with_context(request, *args, **kwargs):
    render_context = RequestContext(request)
    return render_to_response(*args, context_instance=render_context, **kwargs)


def dumb_template(template_name):
    """ Returns a view function that renders the template """
    def view_func(request):
        return render_with_context(request, template_name)
    return view_func


index = dumb_template('index.html.tmpl')
help = dumb_template('help.html.tmpl')
faq = dumb_template('faq.html.tmpl')


@login_required
@with_event
def puzzle(request, puzzle_id, event=None):
    user = request.user.profile

    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    puzzleset = get_object_or_404(PuzzleSet, puzzles=puzzle, event=event)

    return render_with_context(
        request,
        'puzzle.html.tmpl',
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
                    return render_with_context(
                        request,
                        'done.html.tmpl',
                        {}
                    )
        return render_with_context(
            request,
            'puzzle.html.tmpl',
            {'puzzle': puzzle},
        )
    else:
        return render_with_context(
            request,
            'done.html.tmpl',
            {},
        )


def login_view(request):
    if request.method == 'GET':
        return render_with_context(request, 'login.html.tmpl')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('index')
        return render_with_context(
            request, 'login.html.tmpl', {'flash': 'Invalid login'}
        )


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('index')
