from __future__ import absolute_import
import rules


@rules.predicate
def is_admin_for_event(user, event):
    admin_team = event.teams.filter(is_admin=True).get()
    return user in admin_team.users

rules.add_perm('ihunt.change_event', is_admin_for_event)


@rules.predicate
def is_admin_for_puzzleset(user, puzzleset):
    return is_admin_for_event(user, puzzleset.event)

rules.add_perm('ihunt.change_puzzleset', is_admin_for_puzzleset)
rules.add_perm('ihunt.delete_puzzleset', is_admin_for_puzzleset)


@rules.predicate
def is_admin_for_puzzle(user, puzzle):
    return is_admin_for_puzzleset(user, puzzle.puzzleset)

rules.add_perm('ihunt.change_puzzle', is_admin_for_puzzle)
rules.add_perm('ihunt.delete_puzzle', is_admin_for_puzzle)


@rules.predicate
def is_admin_for_clue(user, clue):
    return is_admin_for_puzzle(user, clue.puzzle)

rules.add_perm('ihunt.change_hint', is_admin_for_clue)
rules.add_perm('ihunt.delete_hint', is_admin_for_clue)
rules.add_perm('ihunt.change_unlock', is_admin_for_clue)
rules.add_perm('ihunt.delete_unlock', is_admin_for_clue)
