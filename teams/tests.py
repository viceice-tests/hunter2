from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views import View
from django.test import RequestFactory, TestCase

from accounts.factories import UserFactory, UserProfileFactory, SiteFactory
from accounts.models import UserProfile
from events.factories import EventFactory
from hunter2.resolvers import reverse
from .factories import TeamFactory
from .mixins import TeamMixin
from .models import Team

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
    def test_team_create(self):
        SiteFactory.create()
        site = Site.objects.get_current()

        password = "hunter2"
        event = EventFactory()
        creator = UserProfileFactory(user__password=password)
        team_template = TeamFactory.build()

        self.assertTrue(self.client.login(username=creator.user.username, password=password))
        response = self.client.post(
            reverse('create_team', kwargs={'event_id': event.id}, subdomain='www'),
            {
                'name': team_template.name,
            },
            HTTP_HOST='www.{}'.format(site.domain),
        )
        self.assertEqual(response.status_code, 302)
        team = Team.objects.get(name=team_template.name)
        self.assertTrue(creator in team.members.all())

    def test_team_name_uniqueness(self):
        old_event = EventFactory()
        new_event = EventFactory(current=False)
        team1 = TeamFactory(at_event=old_event)

        # Check that the new event team does not raise a validation error
        TeamFactory(name=team1.name, at_event=new_event)

        # Check that creating a team with the same name on the old event is not allowed.
        with self.assertRaises(ValidationError):
            TeamFactory(name=team1.name, at_event=old_event)

    def test_automatic_creation(self):
        factory = RequestFactory()
        request = factory.get('/irrelevant')  # Path is not used because we call the view function directly
        request.event = EventFactory()
        request.user = UserFactory()
        view = EmptyTeamView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        profile = UserProfile.objects.get(user=request.user)
        Team.objects.get(members=profile)


class InviteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteFactory.create()
        cls.site = Site.objects.get_current()
        cls.event = EventFactory(max_team_size=2)
        cls.password = "hunter2"
        cls.team_admin = UserProfileFactory(user__password=cls.password)
        cls.invitee = UserProfileFactory(user__password=cls.password)
        cls.team = TeamFactory(at_event=cls.event, members={cls.team_admin})

    def setUp(self):
        # Crete an invite for the "invitee" user using the "team_admin" account.
        self.assertTrue(self.client.login(username=self.team_admin.user.username, password=self.password))
        response = self.client.post(
            reverse('invite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.invitee.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)

    def test_invite_accept(self):
        self.assertTrue(self.client.login(username=self.invitee.user.username, password=self.password))
        response = self.client.post(
            reverse('acceptinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.invitee in self.team.members.all())
        self.assertFalse(self.invitee in self.team.invites.all())

        # Now try to invite to a full team
        invitee2 = UserProfileFactory(user__password=self.password)
        self.assertTrue(self.client.login(username=self.invitee.user.username, password=self.password))
        response = self.client.post(
            reverse('invite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': invitee2.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(invitee2 in self.team.members.all())
        self.assertFalse(invitee2 in self.team.invites.all())

        # Now bypass the invitation mechanism to add an invite anyway and
        # check it can't be accepted
        self.team.invites.add(invitee2)
        self.assertTrue(self.client.login(username=invitee2.user.username, password=self.password))
        response = self.client.post(
            reverse('acceptinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(invitee2 in self.team.members.all())
        # Finally check we cleaned up the invite after failing
        self.assertFalse(invitee2 in self.team.invites.all())

    def test_invite_cancel(self):
        response = self.client.post(
            reverse('cancelinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.invitee.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.invitee in self.team.members.all())
        self.assertFalse(self.invitee in self.team.invites.all())

    def test_invite_deny(self):
        self.assertTrue(self.client.login(username=self.invitee.user.username, password=self.password))
        response = self.client.post(
            reverse('denyinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.invitee in self.team.members.all())
        self.assertFalse(self.invitee in self.team.invites.all())

    def test_invite_views_forbidden(self):
        self.client.logout()
        response = self.client.post(
            reverse('invite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('cancelinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('acceptinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('denyinvite', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)


class RequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        SiteFactory.create()
        cls.site = Site.objects.get_current()
        cls.event = EventFactory(max_team_size=2)
        cls.password = "hunter2"
        cls.team_admin = UserProfileFactory(user__password=cls.password)
        cls.applicant = UserProfileFactory(user__password=cls.password)
        cls.team = TeamFactory(at_event=cls.event, members={cls.team_admin})

    def setUp(self):
        # The "applicant" is requesting a place on "team".
        self.assertTrue(self.client.login(username=self.applicant.user.username, password=self.password))
        response = self.client.post(
            reverse('request', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)

    def test_request_accept(self):
        self.assertTrue(self.client.login(username=self.team_admin.user.username, password=self.password))
        response = self.client.post(
            reverse('acceptrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.applicant.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.applicant in self.team.members.all())
        self.assertFalse(self.applicant in self.team.requests.all())

        # Now try to send a request to the full team
        applicant2 = UserProfileFactory(user__password=self.password)
        self.assertTrue(self.client.login(username=applicant2.user.username, password=self.password))
        response = self.client.post(
            reverse('request', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(applicant2 in self.team.members.all())
        self.assertFalse(applicant2 in self.team.requests.all())

        # Now bypass the request mechanism to add a request anyway and
        # check it can't be accepted
        self.team.requests.add(applicant2)
        self.assertTrue(self.client.login(username=self.team_admin.user.username, password=self.password))
        response = self.client.post(
            reverse('acceptrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': applicant2.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(applicant2 in self.team.members.all())
        # Finally check we cleaned up the request after failing
        self.assertFalse(applicant2 in self.team.requests.all())

    def test_request_cancel(self):
        response = self.client.post(
            reverse('cancelrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.applicant in self.team.members.all())
        self.assertFalse(self.applicant in self.team.requests.all())

    def test_request_deny(self):
        self.assertTrue(self.client.login(username=self.team_admin.user.username, password=self.password))
        response = self.client.post(
            reverse('denyrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.applicant.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.applicant in self.team.members.all())
        self.assertFalse(self.applicant in self.team.requests.all())

    def test_request_views_forbidden(self):
        self.client.logout()
        response = self.client.post(
            reverse('request', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('cancelrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('acceptrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('denyrequest', kwargs={'event_id': self.event.id, 'team_id': self.team.id}, subdomain='www'),
            json.dumps({
                'user': self.team_admin.id
            }),
            'application/json',
            HTTP_HOST='www.{}'.format(self.site.domain),
        )
        self.assertEqual(response.status_code, 403)
