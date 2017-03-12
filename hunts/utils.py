from django.http import Http404
from .models import \
    Episode, Puzzle, TeamData, UserData, TeamPuzzleData, UserPuzzleData


def current_puzzle(puzzlesets, team):
    for cs in puzzlesets:
        for c in cs.puzzles.all():
            if not c.answered(team):
                return c
    return None


def event_episode(event, episode_number):
    episodes = event.episodes.order_by('start_date')
    ep_int = int(episode_number)
    try:
        return episodes[ep_int - 1:ep_int].get()
    except Episode.DoesNotExist as e:
        raise Http404 from e


def event_episode_puzzle(event, episode_number, puzzle_number):
    episode = event_episode(event, episode_number)
    try:
        return episode, episode.get_puzzle(puzzle_number)
    except Puzzle.DoesNotExist as e:
        raise Http404 from e


def puzzle_data(puzzle, team, user):
    t_data, created = TeamData.objects.get_or_create(team=team)
    u_data, created = UserData.objects.get_or_create(user=user)
    tp_data, created = TeamPuzzleData.objects.get_or_create(
        puzzle=puzzle, team=team
    )
    up_data, created = UserPuzzleData.objects.get_or_create(
        puzzle=puzzle, user=user
    )
    return t_data, tp_data, up_data
