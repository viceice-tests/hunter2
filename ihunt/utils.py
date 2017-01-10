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
    return episode.puzzles[int(episode_number) - 1:1].get()


def event_episode(event, episode_number):
    episodes = event.episodes.order_by('start_date')
    return episodes[int(episode_number) - 1:1].get()
