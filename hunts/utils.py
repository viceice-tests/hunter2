def current_puzzle(puzzlesets, team):
    for cs in puzzlesets:
        for c in cs.puzzles.all():
            if not c.answered(team):
                return c
    return None


def event_episode(event, episode_number):
    episodes = event.episodes.order_by('start_date')
    ep_int = int(episode_number)
    return episodes[ep_int - 1:ep_int].get()
