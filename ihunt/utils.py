from ihunt.models import Guess


def answered(clue, team):
    guesses = Guess.objects.filter(
        by__in=team.users.all()
    ).filter(
        for_clue=clue
    ).filter(
        guess__in=clue.answers.values('answer')
    )
    return len(guesses) > 0


def current_clue(cluesets, team):
    for cs in cluesets:
        for c in cs.clues.all():
            if not answered(c, team):
                return c
    return None
