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

import asyncio
from collections import defaultdict
import time

from asgiref.sync import async_to_sync, sync_to_async
from channels.consumer import get_handler_name
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.signals import pre_save, pre_delete, post_delete
from django.utils import timezone

from teams.models import Team
from .models import Guess
from .utils import encode_uuid
from . import models, utils


def activate_tenant(f):
    """Decorator for use on methods which must be run with an active tenant, but which are not run through tenant middleware"""
    def wrapper(self, *args, **kwargs):
        try:
            self.scope['tenant'].activate()
        except (AttributeError, KeyError):
            raise ValueError('%s has no scope or no tenant on its scope' % self)
        return f(*args, **kwargs)

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


def pre_save_handler(func):
    """The purpose of this decorator is to connect signal handlers to consumer class methods.

    Before the normal signature of the signal handler, func is passed the class (as a normal classmethod) and "old",
    the instance in the database before save was called (or None). func will then be called after the current
    transaction has been successfully committed, ensuring that the instance argument is stored in the database and
    accessible via database connections in other threads, and that data is ready to be sent to clients."""
    def inner(cls, sender, instance, *args, **kwargs):
        try:
            old = type(instance).objects.get(pk=instance.pk)
        except ObjectDoesNotExist:
            old = None

        def after_commit():
            func(cls, old, sender, instance, *args, **kwargs)

        transaction.on_commit(after_commit)

    return classmethod(inner)


#def post_delete_handler(func):
#    """Connects signal handlers as pre_save_handler, but for post_delete.
#
#    For us pre- or post-delete doesn't make much difference. This decorator does NOT make it possible to get the
#    instance from the database in another thread. This is why we hook post-delete, because the functionality is
#    most similar. If we ever need that for some reason, we would need to use pre_delete and would sacrifice knowing
#    that the transaction completed."""
#    def inner(cls, sender, instance, *args, **kwargs):
#        def after_commit():
#            func(cls, sender, instance, *args, **kwargs)
#
#        transaction.on_commit(after_commit)
#
#    return classmethod(inner)


class PuzzleEventWebsocket(TenantMixin, TeamMixin, JsonWebsocketConsumer):
    @classmethod
    def _group_name(cls, puzzle, team=None):
        if team:
            return f'puzzle-{puzzle.id}.events.team-{team.id}'
        else:
            return f'puzzle-{puzzle.id}.events'

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
        async_to_sync(self.channel_layer.group_add)(
            self._group_name(self.puzzle), self.channel_name
        )
        self.setup_hint_timers()
        self.accept()

    def disconnect(self, close_code):
        for e in self.hint_events.values():
            e.cancel()
        async_to_sync(self.channel_layer.group_discard)(
            self._group_name(self.puzzle, self.team), self.channel_name
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
        self.send_json({'type': 'error', 'content': {'error': message}})

    def setup_hint_timers(self):
        self.hint_events = {}
        for hint in self.puzzle.hint_set.all():
            self.schedule_hint(hint)

    def schedule_hint_msg(self, message):
        try:
            hint = models.Hint.objects.get(id=message['hint_uid'])
        except (TypeError, KeyError):
            raise ValueError('Cannot schedule a hint without either a hint instance or a dictionary with `hint_uid` key.')
        self.schedule_hint(hint)

    def schedule_hint(self, hint):
        try:
            self.hint_events[hint.id].cancel()
        except KeyError:
            pass

        delay = hint.delay_for_team(self.team).total_seconds()
        if time is None or delay < 0:
            return
        loop = sync_to_async.threadlocal.main_event_loop
        # run the hint sender function on the asyncio event loop so we don't have to bother writing scheduler stuff
        task = loop.create_task(self.send_new_hint(self.team, hint, delay))
        self.hint_events[hint.id] = task

    def cancel_scheduled_hint(self, content):
        hint = models.Hint.objects.get(id=content['hint_uid'])

        try:
            self.hint_events[hint.id].cancel()
            del self.hint_events[hint.id]
        except KeyError:
            pass

    ###
    ### These class methods define the JS server -> client protocol of the websocket
    ###

    @classmethod
    def send_new_unlock(cls, guess, unlock):
        cls._send_message(guess.for_puzzle, guess.by_team, {
            'type': 'new_unlock',
            'content': {
                'guess': guess.guess,
                'unlock': unlock.text,
                'unlock_uid': encode_uuid(unlock.id)
            }
        })

    @classmethod
    def send_new_guess(cls, guess, unlocks):
        cls._send_message(guess.for_puzzle, guess.by_team, {
            'type': 'new_guess',
            'content': {
                'timestamp': str(guess.given),
                'guess': guess.guess,
                'guess_uid': encode_uuid(guess.id),
                'correct': guess.correct_for is not None,
                'by': guess.by.username,
            }
        })

    @classmethod
    def send_change_unlock(cls, old_unlock, new_unlock, guess):
        cls._send_message(old_unlock.puzzle, guess.by_team, {
            'type': 'change_unlock',
            'content': {
                'unlock': new_unlock.text,
                'unlock_uid': encode_uuid(old_unlock.id)
            }
        })

    @classmethod
    def send_delete_unlock(cls, unlock, guess):
        cls._send_message(unlock.puzzle, guess.by_team, {
            'type': 'delete_unlock',
            'content': {
                'unlock_uid': encode_uuid(unlock.id),
            }
        })

    @classmethod
    def send_delete_unlockguess(cls, old_unlock, guess):
        cls._send_message(old_unlock.puzzle, guess.by_team, {
            'type': 'delete_unlockguess',
            'content': {
                'guess': guess.guess,
                'unlock_uid': encode_uuid(old_unlock.id),
            }
        })

    @classmethod
    def _new_hint_json(self, hint):
        return {
            'type': 'new_hint',
            'content': {
                'hint': hint.text,
                'hint_uid': encode_uuid(hint.id),
                'time': str(hint.time)
            }
        }

    @classmethod
    def send_new_hint_to_team(cls, team, hint):
        cls._send_message(hint.puzzle, team, cls._new_hint_json(hint))

    async def send_new_hint(self, team, hint, delay, **kwargs):
        # We can't have a sync function (added to the event loop via call_later) because it would have to call back
        # ultimately to SyncConsumer's send method, which is wrapped in async_to_sync, which refuses to run in a thread
        # with a running asyncio event loop.
        # See https://github.com/django/asgiref/issues/56
        await asyncio.sleep(delay)

        # AsyncConsumer replaces its own base_send attribute with an async_to_sync wrapped version if the instance is (a
        # subclass of) SyncConsumer. While bizarre, the original async function is available as AsyncToSync.awaitable.
        # We also have to reproduce the functionality of JsonWebsocketConsumer and WebsocketConsumer here (they don't
        # have async versions.)
        await self.base_send.awaitable({'type': 'websocket.send', 'text': self.encode_json(self._new_hint_json(hint))})
        del self.hint_events[hint.id]

    @classmethod
    def send_delete_hint(cls, team, hint):
        cls._send_message(hint.puzzle, team, {
            'type': 'delete_hint',
            'content': {
                'hint_uid': encode_uuid(hint.id)
            }
        })

    # handler: Guess.pre_save
    @pre_save_handler
    def _new_guess(cls, old, sender, guess, raw, *args, **kwargs):
        # Do not trigger unless this was a newly created guess.
        # Note this means an admin modifying a guess will not trigger anything.
        if old or raw:
            return

        # required info:
        # guess, correctness, new unlocks, timestamp, whodunnit
        all_unlocks = models.Unlock.objects.filter(puzzle=guess.for_puzzle)
        unlocks = []
        for u in all_unlocks:
            if any([a.validate_guess(guess) for a in u.unlockanswer_set.all()]):
                unlocks.append(u.text)
                cls.send_new_unlock(guess, u)

        cls.send_new_guess(guess, unlocks)

    def send_old_guesses(self, start):
        if start == 'all':
            guesses = Guess.objects.filter(for_puzzle=self.puzzle, by_team=self.team)
        else:
            guesses = Guess.objects.filter(for_puzzle=self.puzzle, by_team=self.team, given__gt=start)

        # TODO can this be unified with _new_guess?
        for g in guesses:
            # TODO work out what to do with protocol that can be sent straight back out on
            # the same websocket. Note this is currently sharing the protocol of new_guess.
            self.send_json({
                'type': 'old_guess',
                'content': {
                    # TODO hash with id or something idunno
                    'timestamp': str(g.given),
                    'guess': g.guess,
                    'correct': g.correct_for is not None,
                    'by': g.by.username,
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
                unlocks[g].append(u)

        # TODO: something for sorting unlocks? The View sorts them as in the admin, but this is not alterable,
        # even though it is often meaningful. Currently JS sorts them alphabetically.
        for g in guesses:
            for u in unlocks[g]:
                # TODO same issue as old_guess above
                self.send_json({
                    'type': 'old_unlock',
                    'content': {
                        'guess': g.guess,
                        'unlock': u.text,
                        'unlock_uid': encode_uuid(u.id)
                    }
                })

    # handler: Unlockanswer.pre_save
    @pre_save_handler
    def _new_unlockanswer(cls, old_unlockanswer, sender, instance, raw, *args, **kwargs):
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
            'by_team'
        )
        if old_unlockanswer:
            old_unlock = old_unlockanswer.unlock
            if old_unlock != unlock:
                # TODO: do we need to handle when some muppet moved an unlockanswer manually to another unlock?
                pass
            others = unlock.unlockanswer_set.exclude(id=unlockanswer.id)
            for g in guesses:
                if old_unlockanswer.validate_guess(g) and not any(a.validate_guess(g) for a in others):
                    # The unlockanswer was the only one giving us this and it no longer does
                    cls.send_delete_unlockguess(old_unlock, g)
        for g in guesses:
            if unlockanswer.validate_guess(g):
                # Just notify about all guesses that match this answer. Some may already have done so but that's OK.
                cls.send_new_unlock(g, unlock)

    # handler: Unlock.pre_save
    @pre_save_handler
    def _changed_unlock(cls, old, sender, instance, raw, *args, **kwargs):
        # TODO use this for hints too
        if raw:
            return
        if not old:
            # New unlocks are boring; we will then notify via the unlockanswer hook
            return

        unlock = instance
        puzzle = unlock.puzzle
        guesses = models.Guess.objects.filter(
            for_puzzle=puzzle
        ).select_related(
            'by_team'
        )

        # This could conceivably be different if someone adds an unlock to the wrong puzzle! Probably never going
        # to happen. Better safe than sorry.
        if puzzle == old.puzzle:
            done_teams = []
            for g in guesses:
                if g.by_team in done_teams:
                    continue
                if any([u.validate_guess(g) for u in old.unlockanswer_set.all()]):
                    done_teams.append(g.by_team)
                    cls.send_change_unlock(old, unlock, g)
        else:
            for g in guesses:
                if any([u.validate_guess(g) for u in old.unlockanswer_set.all()]):
                    # If the puzzles are different we send *one* message to delete that unlock to the
                    # old puzzle websocket, then add the unlock to the new puzzle, one guess at a time.
                    if g.by_team not in done_teams:
                        cls.send_delete_unlock(unlock, g)
                    done_teams.append(g.by_team)
                    cls.send_new_unlock(g, old)

    # handler: Hint.pre_save
    @pre_save_handler
    def _new_hint(cls, old, sender, instance, raw, *args, **kwargs):
        if raw:
            return
        hint = instance
        if old and hint.puzzle != old.puzzle:
            raise NotImplemented

        for team in Team.objects.all():
            data = models.PuzzleData(hint.puzzle, team)
            layer = get_channel_layer()
            if hint.unlocked_by(team, data):
                async_to_sync(layer.group_send)(cls._group_name(hint.puzzle, team), {'type': 'cancel_scheduled_hint', 'hint_uid': str(hint.id)})
                cls.send_new_hint_to_team(team, hint)
            else:
                if old and old.unlocked_by(team, data):
                    cls.send_delete_hint(team, hint)
                async_to_sync(layer.group_send)(cls._group_name(hint.puzzle, team), {'type': 'schedule_hint_msg', 'hint_uid': str(hint.id)})

    # handler: UnlockAnswer.pre_delete
    @classmethod
    def _deleted_unlockanswer(cls, sender, instance, *args, **kwargs):
        # TODO if the Unlock is being deleted it will cascade to the answers. In that case
        # we don't actually need to send events for them.
        unlockanswer = instance
        unlock = unlockanswer.unlock
        puzzle = unlock.puzzle

        guesses = models.Guess.objects.filter(
            for_puzzle=puzzle,
        ).select_related(
            'by_team',
        )

        others = unlock.unlockanswer_set.exclude(id=unlockanswer.id)

        done_teams = []

        for g in guesses:
            if g.by_team in done_teams:
                continue
            if unlockanswer.validate_guess(g) and not any(a.validate_guess(g) for a in others):
                cls.send_delete_unlockguess(g)
                done_teams.append(g.by_team)

    # handler: Unlock.pre_delete
    @classmethod
    def _deleted_unlock(cls, sender, instance, *args, **kwargs):
        unlock = instance
        puzzle = unlock.puzzle

        guesses = models.Guess.objects.filter(
            for_puzzle=puzzle
        ).select_related(
            'by_team',
        )

        done_teams = []

        for g in guesses:
            if g.by_team in done_teams:
                continue
            if any([u.validate_guess(g) for u in instance.unlockanswer_set.all()]):
                done_teams.append(g.by_team)
                cls.send_delete_unlock(unlock, g)

    # handler: Hint.pre_delete
    @classmethod
    def _deleted_hint(cls, sender, instance, *arg, **kwargs):
        hint = instance

        for team in Team.objects.all():
            data = models.PuzzleData(hint.puzzle, team)
            if hint.unlocked_by(team, data):
                cls.send_delete_hint(team, hint)


pre_save.connect(PuzzleEventWebsocket._new_guess, sender=models.Guess)
pre_save.connect(PuzzleEventWebsocket._new_unlockanswer, sender=models.UnlockAnswer)
pre_save.connect(PuzzleEventWebsocket._changed_unlock, sender=models.Unlock)
pre_save.connect(PuzzleEventWebsocket._new_hint, sender=models.Hint)

pre_delete.connect(PuzzleEventWebsocket._deleted_unlockanswer, sender=models.UnlockAnswer)
pre_delete.connect(PuzzleEventWebsocket._deleted_unlock, sender=models.Unlock)
pre_delete.connect(PuzzleEventWebsocket._deleted_hint, sender=models.Hint)
