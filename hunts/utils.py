from django.http import Http404

def current_puzzle(puzzlesets, team):
    for cs in puzzlesets:
        for c in cs.puzzles.all():
            if not c.answered(team):
                return c
    return None


def event_episode(event, episode_number):
    from .models import Episode

    episodes = event.episode_set.order_by('start_date')
    ep_int = int(episode_number)
    try:
        return episodes[ep_int - 1:ep_int].get()
    except Episode.DoesNotExist as e:
        raise Http404 from e


def event_episode_puzzle(event, episode_number, puzzle_number):
    from .models import Puzzle

    episode = event_episode(event, episode_number)
    try:
        return episode, episode.get_puzzle(puzzle_number)
    except Puzzle.DoesNotExist as e:
        raise Http404 from e
