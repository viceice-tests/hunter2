

def current_puzzle(puzzlesets, team):
    for cs in puzzlesets:
        for c in cs.puzzles.all():
            if not c.answered(team):
                return c
    return None
