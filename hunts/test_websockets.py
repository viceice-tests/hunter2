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


from datetime import timedelta
from urllib.parse import unquote, urlparse
import time

from django.db import connection
from django.urls import reverse
from django.utils import timezone
import pytest
from channels.testing import WebsocketCommunicator, ApplicationCommunicator
from channels.db import database_sync_to_async

from teams.factories import TeamFactory, TeamMemberFactory
from .factories import (
    AnnouncementFactory,
    AnswerFactory,
    EpisodeFactory,
    GuessFactory,
    HintFactory,
    PuzzleFactory,
    PuzzleFileFactory,
    SolutionFileFactory,
    TeamDataFactory,
    TeamPuzzleDataFactory,
    UnlockAnswerFactory,
    UnlockFactory,
    UserDataFactory,
    UserPuzzleDataFactory,
)
from events.factories import ThemeFactory
from events.models import Event, Domain
from events.test import EventTestCase
from .consumers import PuzzleEventWebsocket
from hunter2.routing import application

#theme = ThemeFactory()
#event = Event(schema_name='test')
#event.current = True
#event.end_date = timezone.now() + timedelta(days=5)
#event.name = 'Test Event'
#event.theme = theme
#event.save()
#
#domain = Domain(tenant=event, domain='hunter2.test.com')
#domain.save()
#connection.set_tenant(event)

class PytestTestRunner(object):
    """Runs pytest to discover and run tests.
    
    Copied from pytest-django FAQ"""

    def __init__(self, verbosity=1, failfast=False, keepdb=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb

    def run_tests(self, test_labels):
        """Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """
        import pytest

        argv = []
        if self.verbosity == 0:
            argv.append('--quiet')
        if self.verbosity == 2:
            argv.append('--verbose')
        if self.verbosity == 3:
            argv.append('-vv')
        if self.failfast:
            argv.append('--exitfirst')
        if self.keepdb:
            argv.append('--reuse-db')

        argv.extend(test_labels)
        return pytest.main(argv)


class AuthCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, scope, headers=None, subprotocols=None):
        if not isinstance(path, str):
            raise TypeError("Expected str, got {}".format(type(path)))
        parsed = urlparse(path)
        self.scope = {
            "type": "websocket",
            "path": unquote(parsed.path),
            "query_string": parsed.query.encode("utf-8"),
            "headers": headers or [],
            "subprotocols": subprotocols or [],
        }
        self.scope.update(scope)
        ApplicationCommunicator.__init__(self, application, self.scope)

def get_communicator(episode, puzzle, domain):
    url = 'ws/hunt/ep/%d/pz/%d/' % (episode.get_relative_id(), puzzle.get_relative_id())
    comm = WebsocketCommunicator(application, url, headers=[(b'host', domain.domain.encode('idna'))])
    return comm


class EventTestCaseGlue(object):
    @pytest.fixture(scope="class", autouse=True)
    def unittest_class_setup(self, request, django_db_blocker, django_db_setup):
        django_db_blocker.unblock()
        request.cls.testcase = EventTestCase()
        request.cls.testcase.setUpClass()
        request.cls.tenant = request.cls.testcase.tenant
        request.cls.domain = request.cls.testcase.domain
        yield

        # Teardown
        self.testcase.tearDownClass()
        django_db_blocker.block()

    @pytest.fixture(autouse=True)
    def unittest_test_setup(self):
        self.testcase._pre_setup()
        self.testcase.setUp()
        self.client = self.testcase.client
        print('start', time.time())
        yield
        print('done', time.time())
        self.testcase.tearDown()
        self.testcase._post_teardown()


#@pytest.mark.django_db
class TestWebsocket(EventTestCaseGlue):
    @pytest.mark.asyncio
    #@pytest.mark.django_db
    async def _test_anonymous_access(self):
        #ep = EpisodeFactory(event=event)
        pz = PuzzleFactory()
        ep = pz.episode_set.get()
        comm = get_communicator(ep, pz, self.domain)
        connected, subprotocol = await comm.connect()
        assert connected is False

    @pytest.mark.asyncio
    async def test_logged_in_access(self):
        pz = PuzzleFactory()
        ep = pz.episode_set.get()
        profile = TeamMemberFactory()
        print(profile.team_at(self.tenant))
        from teams.models import Team
        print(Team.objects.all())
        print('in test', time.time())
        self.client.force_login(profile.user)
        url = 'ws/hunt/ep/%d/pz/%d/' % (ep.get_relative_id(), pz.get_relative_id())
        cookies = self.client.cookies.output(header='', sep='; ').encode()
        headers = [(b'origin', b'hunter2.local'), (b'host', self.domain.domain.encode('idna')), (b'cookie', cookies)]
        comm = AuthCommunicator(application, url, scope={'user': profile.user}, headers=headers)
        print('pre-connect', Team.objects.all())
        connected, subprotocol = await comm.connect()
        print('test again')
        print(time.time())
        print(Team.objects.all())
        print('plz')
        assert connected is True
