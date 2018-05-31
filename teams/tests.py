import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.views import View
from django_tenants.test.client import TenantRequestFactory

from accounts.factories import UserFactory, UserProfileFactory
from accounts.models import UserProfile
from events.factories import EventFactory
from events.models import Event
from events.test import EventTestCase
from .factories import TeamFactory
from .mixins import TeamMixin
from .models import Team


class FactoryTests(EventTestCase):

    def test_team_factory_default_construction(self):
        TeamFactory.create()


class EmptyTeamView(TeamMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


class TeamRulesTests(EventTestCase):
    def test_max_team_size(self):
        event = self.tenant
        event.max_team_size = 2
        event.save()
        team  = TeamFactory(at_event=event)

        # Add 3 users to a team when that max is less than that.
        self.assertLess(event.max_team_size, 3)
        users = UserProfileFactory.create_batch(3)

        with self.assertRaises(ValidationError):
            for user in users:
                team.members.add(user)

    def test_one_team_per_member_per_event(self):
        event = self.tenant
        teams = TeamFactory.create_batch(2, at_event=event)
        user = UserProfileFactory()

        with self.assertRaises(ValidationError):
            teams[0].members.add(user)
            teams[1].members.add(user)


class TeamCreateTests(EventTestCase):
    def test_team_create(self):
        creator = UserProfileFactory()
        team_template = TeamFactory.build()

        self.client.force_login(creator.user)
        response = self.client.post(
            reverse('create_team'),
            {
                'name': team_template.name,
            },
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
        factory = TenantRequestFactory(self.tenant)
        request = factory.get('/irrelevant')  # Path is not used because we call the view function directly
        request.tenant = Event.objects.get()
        request.user = UserFactory()
        view = EmptyTeamView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        profile = UserProfile.objects.get(user=request.user)
        Team.objects.get(members=profile)


class InviteTests(EventTestCase):
    def setUp(self):
        self.event = self.tenant
        self.team_admin = UserProfileFactory()
        self.invitee = UserProfileFactory()
        self.team = TeamFactory(at_event=self.event, members={self.team_admin})

        # Create an invite for the "invitee" user using the "team_admin" account.
        self.client.force_login(self.team_admin.user)
        response = self.client.post(
            reverse('invite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.invitee.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_invite_accept(self):
        self.client.force_login(self.invitee.user)
        response = self.client.post(
            reverse('acceptinvite', kwargs={'team_id': self.team.id}),
            json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.invitee in self.team.members.all())
        self.assertFalse(self.invitee in self.team.invites.all())

        # Now try to invite to a full team
        self.event.max_team_size = 2
        self.event.save()
        invitee2 = UserProfileFactory()
        self.client.force_login(self.invitee.user)
        response = self.client.post(
            reverse('invite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': invitee2.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(invitee2 in self.team.members.all())
        self.assertFalse(invitee2 in self.team.invites.all())

        # Now bypass the invitation mechanism to add an invite anyway and
        # check it can't be accepted
        self.team.invites.add(invitee2)
        self.client.force_login(invitee2.user)
        response = self.client.post(
            reverse('acceptinvite', kwargs={'team_id': self.team.id}),
            json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(invitee2 in self.team.members.all())
        # Finally check we cleaned up the invite after failing
        self.assertFalse(invitee2 in self.team.invites.all())

    def test_invite_cancel(self):
        response = self.client.post(
            reverse('cancelinvite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.invitee.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.invitee in self.team.members.all())
        self.assertFalse(self.invitee in self.team.invites.all())

    def test_invite_deny(self):
        self.client.force_login(self.invitee.user)
        response = self.client.post(
            reverse('denyinvite', kwargs={'team_id': self.team.id}),
            json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.invitee in self.team.members.all())
        self.assertFalse(self.invitee in self.team.invites.all())

    def test_invite_views_forbidden(self):
        self.client.logout()
        response = self.client.post(
            reverse('invite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('cancelinvite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('acceptinvite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('denyinvite', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)


class RequestTests(EventTestCase):
    def setUp(self):
        self.event = self.tenant
        self.team_admin = UserProfileFactory()
        self.applicant = UserProfileFactory()
        self.team = TeamFactory(at_event=self.event, members={self.team_admin})

        # The "applicant" is requesting a place on "team".
        self.client.force_login(self.applicant.user)
        response = self.client.post(
            reverse('request', kwargs={'team_id': self.team.id}),
            json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_request_accept(self):
        self.client.force_login(self.team_admin.user)
        response = self.client.post(
            reverse('acceptrequest', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.applicant.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.applicant in self.team.members.all())
        self.assertFalse(self.applicant in self.team.requests.all())

        # Now try to send a request to the full team
        self.event.max_team_size = 2
        self.event.save()
        applicant2 = UserProfileFactory()
        self.client.force_login(applicant2.user)
        response = self.client.post(
            reverse('request', kwargs={'team_id': self.team.id}),
            json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(applicant2 in self.team.members.all())
        self.assertFalse(applicant2 in self.team.requests.all())

        # Now bypass the request mechanism to add a request anyway and
        # check it can't be accepted
        self.team.requests.add(applicant2)
        self.client.force_login(self.team_admin.user)
        response = self.client.post(
            reverse('acceptrequest', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': applicant2.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(applicant2 in self.team.members.all())
        # Finally check we cleaned up the request after failing
        self.assertFalse(applicant2 in self.team.requests.all())

    def test_request_cancel(self):
        response = self.client.post(
            reverse('cancelrequest', kwargs={'team_id': self.team.id}),
            json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.applicant in self.team.members.all())
        self.assertFalse(self.applicant in self.team.requests.all())

    def test_request_deny(self):
        self.client.force_login(self.team_admin.user)
        response = self.client.post(
            reverse('denyrequest', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.applicant.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.applicant in self.team.members.all())
        self.assertFalse(self.applicant in self.team.requests.all())

    def test_request_views_forbidden(self):
        self.client.logout()
        response = self.client.post(
            reverse('request', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('cancelrequest', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('acceptrequest', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse('denyrequest', kwargs={'team_id': self.team.id}),
            json.dumps({
                'user': self.team_admin.id
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)
