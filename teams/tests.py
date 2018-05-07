from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views import View
from django.test import RequestFactory, TestCase

import teams
from events.models import Event
from hunter2.resolvers import reverse
from .mixins import TeamMixin
from .models import Team, UserProfile

from teams.factories import UserProfileFactory, TeamFactory
from events.factories import EventFactory

import events
import json


class EmptyTeamView(TeamMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


class TeamRulesTests(TestCase):
    def test_max_team_size(self):
        event = EventFactory(max_team_size=2)
        team  = TeamFactory(at_event=event)

        # Add 3 users to a team when that max is less than that.
        self.assertLess(event.max_team_size, 3)
        users = UserProfileFactory.create_batch(3)

        with self.assertRaises(ValidationError):
            for user in users:
                team.members.add(user)

    def test_one_team_per_member_per_event(self):
        event = EventFactory()
        teams = TeamFactory.create_batch(2, at_event=event)
        user = UserProfileFactory()

        with self.assertRaises(ValidationError):
            teams[0].members.add(user)
            teams[1].members.add(user)


class TeamCreateTests(TestCase):
    fixtures = ['teams_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()

    def test_team_create(self):
        self.assertTrue(self.client.login(username='test_b', password='hunter2'))
        response = self.client.post(
            reverse('create_team', kwargs={'event_id': 1}, subdomain='www'),
            {
                'name': 'Test Team',
            },
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 302)
        creator = UserProfile.objects.get(pk=2)
        team = Team.objects.get(name='Test Team')
        self.assertTrue(creator in team.members.all())

    def test_team_name_uniqueness(self):
        old_event = events.models.Event.objects.get(pk=1)
        new_event = events.models.Event(name='New Event', theme=old_event.theme, current=False)
        new_event.save()
        # Check that the new event team does not raise a validation error
        Team(name='Test A', at_event=new_event).save()
        with self.assertRaises(ValidationError):
            Team(name='Test A', at_event=old_event).save()

    def test_automatic_creation(self):
        factory = RequestFactory()
        request = factory.get('/irrelevant')  # Path is not used because we call the view function directly
        request.event = events.models.Event.objects.get(pk=1)
        request.user = User.objects.get(pk=4)
        view = EmptyTeamView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        profile = UserProfile.objects.get(user=request.user)
        Team.objects.get(members=profile)


class InviteTests(TestCase):
    fixtures = ['teams_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            reverse('invite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 2
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)

    def test_invite_accept(self):
        self.assertTrue(self.client.login(username='test_b', password='hunter2'))
        response = self.client.post(
            reverse('acceptinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        user = UserProfile.objects.get(pk=2)
        team = Team.objects.get(pk=1)
        self.assertTrue(user in team.members.all())
        self.assertFalse(user in team.invites.all())

        # Now try to invite to a full team
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            reverse('invite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 3
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        user = UserProfile.objects.get(pk=3)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user in team.members.all())
        self.assertFalse(user in team.invites.all())

        # Now bypass the invitation mechanism to add an invite anyway and
        # check it can't be accepted
        team.invites.add(user)
        self.assertTrue(self.client.login(username='test_c', password='hunter2'))
        response = self.client.post(
            reverse('acceptinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user in team.members.all())
        # Finally check we cleaned up the invite after failing
        self.assertFalse(user in team.invites.all())

    def test_invite_cancel(self):
        response = self.client.post(
            reverse('cancelinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 2
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        user = UserProfile.objects.get(pk=2)
        team = Team.objects.get(pk=1)
        self.assertFalse(user in team.members.all())
        self.assertFalse(user in team.invites.all())

    def test_invite_deny(self):
        self.assertTrue(self.client.login(username='test_b', password='hunter2'))
        response = self.client.post(
            reverse('denyinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        user = UserProfile.objects.get(pk=2)
        team = Team.objects.get(pk=1)
        self.assertFalse(user in team.members.all())
        self.assertFalse(user in team.invites.all())

    def test_invite_views_forbidden(self):
        self.client.logout()
        response = self.client.post(
            reverse('invite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('cancelinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('acceptinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('denyinvite', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)


class RequestTests(TestCase):
    fixtures = ['teams_test']

    def setUp(self):
        site = Site.objects.get()
        site.domain = 'testserver'
        site.save()
        self.assertTrue(self.client.login(username='test_b', password='hunter2'))
        response = self.client.post(
            reverse('request', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)

    def test_request_accept(self):
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            reverse('acceptrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 2
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        user = UserProfile.objects.get(pk=2)
        team = Team.objects.get(pk=1)
        self.assertTrue(user in team.members.all())
        self.assertFalse(user in team.requests.all())

        # Now try to send a request to the full team
        self.assertTrue(self.client.login(username='test_c', password='hunter2'))
        response = self.client.post(
            reverse('request', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        user = UserProfile.objects.get(pk=3)
        self.assertFalse(user in team.members.all())
        self.assertFalse(user in team.requests.all())

        # Now bypass the request mechanism to add a request anyway and
        # check it can't be accepted
        team.requests.add(user)
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            reverse('acceptrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 3
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user in team.members.all())
        # Finally check we cleaned up the request after failing
        self.assertFalse(user in team.requests.all())

    def test_request_cancel(self):
        response = self.client.post(
            reverse('cancelrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        user = UserProfile.objects.get(pk=2)
        team = Team.objects.get(pk=1)
        self.assertFalse(user in team.members.all())
        self.assertFalse(user in team.requests.all())

    def test_request_deny(self):
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            reverse('denyrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 2
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        user = UserProfile.objects.get(pk=2)
        team = Team.objects.get(pk=1)
        self.assertFalse(user in team.members.all())
        self.assertFalse(user in team.requests.all())

    def test_request_views_forbidden(self):
        self.client.logout()
        response = self.client.post(
            reverse('request', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('cancelrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('acceptrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('denyrequest', kwargs={'event_id': 1, 'team_id': 1}, subdomain='www'),
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
