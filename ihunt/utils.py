from .models import Guess


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


def episode_puzzle(episode, puzzle_number):
    n = int(puzzle_number)
    return episode.puzzles.all()[n - 1:n].get()


def event_episode(event, episode_number):
    episodes = event.episodes.order_by('start_date')
    ep_int = int(episode_number)
    return episodes[ep_int - 1:ep_int].get()
