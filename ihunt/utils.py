from ihunt.models import Guess


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
