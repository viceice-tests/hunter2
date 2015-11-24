from django.shortcuts import get_object_or_404
from ihunt.models import Event, Guess


def answered(puzzle, team):
    guesses = Guess.objects.filter(
        by__in=team.users.all()
    ).filter(
        for_puzzle=puzzle
    ).filter(
        guess__in=puzzle.answers.values('answer')
    )
    return len(guesses) > 0


def current_puzzle(puzzlesets, team):
    for cs in puzzlesets:
        for c in cs.puzzles.all():
            if not answered(c, team):
                return c
    return None


def with_event(f):
    """ Returns a wed function that receives an `event` kwarg """
    class NoCurrentEventError(Exception):
        pass

    def view_func(request, event_id=None, *args, **kwargs):
        if event_id is not None:
            event = get_object_or_404(Event, pk=event_id)
        else:
            event = Event.objects.filter(current=True).first()

        return f(request, event=event, *args, **kwargs)
    return view_func
