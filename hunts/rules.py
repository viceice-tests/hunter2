# Copyright (C) 2018 The Hunter2 Contributors.
#
# This file is part of Hunter2.
#
# Hunter2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Hunter2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with Hunter2.  If not, see <http://www.gnu.org/licenses/>.

import rules

from teams.rules import is_admin_for_event, is_admin_for_event_child
from .models import Episode, Puzzle, Unlock


def set_all_perms_for_model(app, model, predicate):
    rules.add_perm(f'{app}.add_{model}', predicate)
    rules.add_perm(f'{app}.change_{model}', predicate)
    rules.add_perm(f'{app}.delete_{model}', predicate)
    rules.add_perm(f'{app}.view_{model}', predicate)


@rules.predicate
def is_admin_for_episode_child(user, obj):
    if obj is None:  # If we have no object we're checking globally for the event specified by the active schema
        return is_admin_for_event.test(user, None)

    # We should either have an Episode or something with a direct foreign key to an Episode named episode
    try:
        episode = obj if isinstance(obj, Episode) else obj.episode
    except AttributeError as e:
        raise TypeError('is_admin_for_episode_child must be called with an Episode or a type with a foreign key to it called "episode"') from e

    return is_admin_for_event_child.test(user, episode)


@rules.predicate
def is_admin_for_puzzle_child(user, obj):
    if obj is None:  # If we have no object we're checking globally for the event specified by the active schema
        return is_admin_for_event.test(user, None)

    # We should either have a Puzzle or something with a direct foreign key to an Puzzle named puzzle
    try:
        puzzle = obj if isinstance(obj, Puzzle) else obj.puzzle
    except AttributeError as e:
        raise TypeError('is_admin_for_puzzle_child must be called with a Puzzle or a type with a foreign key to it called "puzzle"') from e

    return is_admin_for_episode_child.test(user, puzzle)


@rules.predicate
def is_admin_for_unlock_child(user, obj):
    if obj is None:  # If we have no object we're checking globally for the event specified by the active schema
        return is_admin_for_event.test(user, None)

    # We should either have a Unlock or something with a direct foreign key to an Unlock named unlock
    try:
        unlock = obj if isinstance(obj, Unlock) else obj.unlock
    except AttributeError as e:
        raise TypeError('is_admin_for_unlock_child must be called with a Unlock or a type with a foreign key to it called "unlock"') from e

    return is_admin_for_puzzle_child.test(user, unlock)


rules.add_perm('hunts', is_admin_for_event)

set_all_perms_for_model('hunts', 'announcement', is_admin_for_event_child)
set_all_perms_for_model('hunts', 'episode', is_admin_for_event_child)
set_all_perms_for_model('hunts', 'headstart', is_admin_for_episode_child)
set_all_perms_for_model('hunts', 'puzzle', is_admin_for_episode_child)
set_all_perms_for_model('hunts', 'answer', is_admin_for_puzzle_child)
set_all_perms_for_model('hunts', 'hint', is_admin_for_puzzle_child)
set_all_perms_for_model('hunts', 'unlock', is_admin_for_puzzle_child)
set_all_perms_for_model('hunts', 'puzzlefile', is_admin_for_puzzle_child)
set_all_perms_for_model('hunts', 'solutionfile', is_admin_for_puzzle_child)
set_all_perms_for_model('hunts', 'unlockanswer', is_admin_for_unlock_child)
