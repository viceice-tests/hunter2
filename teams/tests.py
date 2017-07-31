from django.test import TestCase
from .models import Team, UserProfile

import json


class TeamCreateTests(TestCase):
    fixtures = ['teams_test']

    def test_team_create(self):
        self.assertTrue(self.client.login(username='test_b', password='hunter2'))
        response = self.client.post(
            '/create_team',
            {
                'name': 'Test Team',
                'invites': [3],
            },
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 302)
        creator = UserProfile.objects.get(pk=2)
        invitee = UserProfile.objects.get(pk=3)
        team = Team.objects.get(pk=2)
        self.assertTrue(creator in team.members.all())
        self.assertTrue(invitee in team.invites.all())


class InviteTests(TestCase):
    fixtures = ['teams_test']

    def setUp(self):
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            '/team/1/invite',
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
            '/team/1/acceptinvite',
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
            '/team/1/invite',
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
            '/team/1/acceptinvite',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user in team.members.all())
        self.assertTrue(user in team.invites.all())

    def test_invite_cancel(self):
        response = self.client.post(
            '/team/1/cancelinvite',
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
            '/team/1/denyinvite',
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
            '/team/1/invite',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/cancelinvite',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/acceptinvite',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/denyinvite',
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
        self.assertTrue(self.client.login(username='test_b', password='hunter2'))
        response = self.client.post(
            '/team/1/request',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)

    def test_request_accept(self):
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            '/team/1/acceptrequest',
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
            '/team/1/request',
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
            '/team/1/acceptinvite',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(user in team.members.all())
        self.assertTrue(user in team.requests.all())

    def test_request_cancel(self):
        response = self.client.post(
            '/team/1/cancelrequest',
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
            '/team/1/denyrequest',
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
            '/team/1/request',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/cancelrequest',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/acceptrequest',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/denyrequest',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
