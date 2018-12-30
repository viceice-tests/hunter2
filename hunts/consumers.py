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

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_save
from asgiref.sync import async_to_sync
from channels.consumer import get_handler_name
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from collections import defaultdict

from .models import Guess
from .utils import encode_uuid
from . import models, utils


def activate_tenant(f):
    def wrapper(self, *args, **kwargs):
        try:
            self.scope['tenant'].activate()
        except (AttributeError, KeyError):
            raise ValueError('%s has no scope or no tenant on its scope' % self)
        return f(self, *args, **kwargs)

    return wrapper


class TenantMixin:
    @database_sync_to_async
    def dispatch(self, message):
        # We have to completely override the method rather than call back to SyncConsumer's
        # dispatch because that is *also* decorated with sync_to_async, so the handler will run in
        # another thread... and the whole point here is to activate the tenant for the thread
        # the handler will run in!
        try:
            self.scope['tenant'].activate()
        except (AttributeError, KeyError):
            raise ValueError('%s has no scope or no tenant on its scope' % self)
        handler = getattr(self, get_handler_name(message), None)
        if handler:
            handler(message)
        else:
            raise ValueError("No handler for message type %s" % message["type"])


class TeamMixin:
    def websocket_connect(self, message):
        # Add a team object to the scope. We can't do this in middleware because the user object
        # isn't resolved yet (I don't know what causes it to be resolved, either...) and we can't do
        # it in __init__ here because the middleware hasn't even run then, so we have no user or
        # tenant or anything!
        # This means this is a bit weirdly placed.
        try:
            user = self.scope['user'].profile
            self.team = user.team_at(self.scope['tenant'])
        except ObjectDoesNotExist:
            # A user on the website will never open the websocket without getting a userprofile and team.
            self.close()
            return
        return super().websocket_connect(message)


# It is important this class uses a synchronous Consumer, because each one of these consumers runs in a
# different thread. Asynchronous consumers can suspend while another consumer in the same thread runs.
# This would break, because the active tenant may need to be different between each consumer.
class PuzzleEventWebsocket(TenantMixin, TeamMixin, JsonWebsocketConsumer):
    @classmethod
    def _group_name(cls, puzzle, team):
        return f'puzzle-{puzzle.id}.events.team-{team.id}'

    @classmethod
    def _send_message(cls, puzzle, team, message):
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(cls._group_name(puzzle, team), {'type': 'send_json_msg', 'content': message})

    def connect(self):
        keywords = self.scope['url_route']['kwargs']
        episode_number = keywords['episode_number']
        puzzle_number = keywords['puzzle_number']
        self.episode, self.puzzle = utils.event_episode_puzzle(self.scope['tenant'], episode_number, puzzle_number)
        async_to_sync(self.channel_layer.group_add)(
            self._group_name(self.puzzle, self.team), self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self._group_name(self.puzzle, self.scope['team']), self.channel_name
        )

    def receive_json(self, content):
        if 'type' not in content:
            self._error('no type in message')
            return

        if content['type'] == 'guesses-plz':
            if 'from' not in content:
                self._error('required field "from" is missing')
                return
            self.send_old_guesses(content['from'])
        elif content['type'] == 'unlocks-plz':
            if 'from' not in content:
                self._error('required field "from" is missing')
                return
            self.send_old_unlocks(content['from'])
        else:
            self._error('invalid request type')

    def send_json_msg(self, content, close=False):
        # For some reason consumer dispatch doesn't strip off the outer dictionary with 'type': 'send_json'
        # (or whatever method name) so we override and do it here. This saves us having to define a separate
        # method which just calls send_json for each type of message.
        super().send_json(content['content'])

    def _error(self, message):
        self.send_json({'type': 'error', 'error': message})

    @classmethod
    def _new_guess(cls, sender, instance, created, raw, *args, **kwargs):
        # Do not trigger unless this was a newly created guess.
        # Note this means an admin modifying a guess will not trigger anything.
        if not created or raw:
            return

        guess = instance

        # required info:
        # guess, correctness, new unlocks, timestamp, whodunnit
        all_unlocks = models.Unlock.objects.filter(puzzle=guess.for_puzzle)
        unlocks = []
        for u in all_unlocks:
            if any([a.validate_guess(guess) for a in u.unlockanswer_set.all()]):
                unlocks.append(u.text)
                cls._send_message(guess.for_puzzle, guess.by_team, {
                    'type': 'new_unlock',
                    'content': {
                        'guess': guess.guess,
                        'unlock': u.text,
                        'unlock_uid': encode_uuid(u.id)
                    }
                })

        cls._send_message(guess.for_puzzle, guess.by_team, {
            'type': 'new_guess',
            'content': {
                # TODO hash with id or something idunno
                'timestamp': str(guess.given),
                'guess': guess.guess,
                'correct': guess.correct_for is not None,
                'by': guess.by.username,
                'unlocks': unlocks
            }
        })

    def send_old_guesses(self, start):
        if start == 'all':
            guesses = Guess.objects.filter(for_puzzle=self.puzzle, by_team=self.team)
        else:
            guesses = Guess.objects.filter(for_puzzle=self.puzzle, by_team=self.team, given__gt=start)

        # TODO can this be unified with _new_guess?
        all_unlocks = models.Unlock.objects.filter(puzzle=self.puzzle)
        unlocks = defaultdict(list)
        for u in all_unlocks:
            correct_guesses = u.unlocked_by(self.team)
            if not correct_guesses:
                continue

            correct_guesses = set(correct_guesses)
            for g in correct_guesses:
                unlocks[g].append(u.text)

        # TODO: separate out sending the unlocks to a send_old_unlocks method
        for g in guesses:
            self.send_json({
                'type': 'old_guess',
                'content': {
                    # TODO hash with id or something idunno
                    'timestamp': str(g.given),
                    'guess': g.guess,
                    'correct': g.correct_for is not None,
                    'by': g.by.username,
                    'unlocks': unlocks[g]
                }
            })

    def send_old_unlocks(self, start):
        if start == 'all':
            guesses = Guess.objects.filter(for_puzzle=self.puzzle, by_team=self.team)
        else:
            guesses = Guess.objects.filter(for_puzzle=self.puzzle, by_team=self.team, given__gt=start)

        all_unlocks = models.Unlock.objects.filter(puzzle=self.puzzle)
        unlocks = defaultdict(list)
        for u in all_unlocks:
            # Performance note: 1 query per unlock
            correct_guesses = u.unlocked_by(self.team)
            if not correct_guesses:
                continue

            correct_guesses = set(correct_guesses)
            for g in correct_guesses:
                unlocks[g].append(u.text)

        # TODO: something for sorting unlocks? The View sorts them as in the admin, but this is not alterable,
        # even though it is often meaningful.
        for g in guesses:
            for u in unlocks[g]:
                self.send_json({
                    'type': 'old_unlock',
                    'content': {
                        'guess': g.guess,
                        'unlock': u,
                        'unlock_uid': encode_uuid(u.id)
                    }
                })

    @classmethod
    def _new_unlockanswer(cls, sender, instance, raw, *args, **kwargs):
        # TODO remove old unlock entries if created == False
        if raw:
            return

        unlockanswer = instance
        unlock = unlockanswer.unlock
        puzzle = unlock.puzzle

        # TODO: performance check. This means that whenever an unlock is added or changed, every single guess on
        # that puzzle is going to be tested against that guess immediately. *Should* be fine since it's one query
        # and doing the validation is mostly simple. Could be costly with lua runtimes...
        guesses = models.Guess.objects.filter(
            for_puzzle=puzzle
        ).select_related(
            'by_team', 
        )
        if unlockanswer.id:
            old_unlockanswer = models.UnlockAnswer.objects.filter(id=unlockanswer.id).select_related('unlock').get()
            old_unlock = old_unlockanswer.unlock
            if old_unlock != unlock:
                # Why did this happen?!
                pass
            others = unlock.unlockanswer_set.exclude(id=unlockanswer.id)
            for g in guesses:
                if old_unlockanswer.validate_guess(g) and not any(a.validate_guess(g) for a in others):
                    cls._send_message(old_unlock.puzzle, g.by_team, {
                        'type': 'delete_unlockguess',
                        'content': {
                            'guess': g.guess,
                            'unlock': old_unlock.text,
                        }
                    })
        for g in guesses:
            if unlockanswer.validate_guess(g):
                cls._send_message(puzzle, g.by_team, {
                    'type': 'new_unlock',
                    'content': {
                        'guess': g.guess,
                        'unlock': unlock.text,
                        'unlock_uid': encode_uuid(unlock.id)
                    }
                })

    @classmethod
    def _changed_unlock(cls, sender, instance, raw, *args, **kwargs):
        # TODO use this for hints too
        if raw:
            return
        if not instance.id:
            # New unlocks are boring; we will then notify via the unlockanswer hook
            return
        unlock = instance
        old = models.Unlock.objects.filter(id=unlock.id).select_related('puzzle').get()

        puzzle = unlock.puzzle
        # This could conceivably be different if someone adds an unlock to the wrong puzzle! Probably never going
        # to happen. Better safe than sorry.
        old_puzzle = old.puzzle

        guesses = models.Guess.objects.filter(
            for_puzzle=puzzle
        ).select_related(
            'by_team', 
        )
        if puzzle == old.puzzle:
            done_teams = []
            for g in guesses:
                if g.by_team in done_teams:
                    continue
                if any([u.validate_guess(g) for u in old.unlockanswer_set.all()]):
                    done_teams.append(g.by_team)
                    cls._send_message(old_puzzle, g.by_team, {
                        'type': 'change_unlock',
                        'content': {
                            'old': old.text,
                            'new': unlock.text
                        }
                    })
        else:
            for g in guesses:
                if any([u.validate_guess(g) for u in old.unlockanswer_set.all()]):
                    # If the puzzles are different we send *one* message to delete unlocks with that text to the
                    # old puzzle websocket, then add the unlock to the new puzzle, one guess at a time.
                    if g.by_team not in done_teams:
                        cls._send_message(old_puzzle, g.by_team, {
                            'type': 'delete_unlock',
                            'content': {
                                'unlock_uid': encode_uuid(old.id),
                            }
                        })
                    done_teams.append(g.by_team)
                    cls._send_message(puzzle, g.by_team, {
                        'type': 'new_unlock',
                        'content': {
                            'guess': g.guess,
                            'unlock': old.text,
                            'unlock_uid': encode_uuid(old.id)
                        }
                    })


post_save.connect(PuzzleEventWebsocket._new_guess, sender=models.Guess)
pre_save.connect(PuzzleEventWebsocket._new_unlockanswer, sender=models.UnlockAnswer)
pre_save.connect(PuzzleEventWebsocket._changed_unlock, sender=models.Unlock)
