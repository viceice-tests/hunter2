from django.test import TestCase
from .models import Team, UserProfile

import json


class TeamJoinTests(TestCase):
    fixtures = ['teams_test']

    def test_invites(self):
        response = self.client.post(
            '/team/1/invite',
            json.dumps({
                'user': 1
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            '/team/1/invite',
            json.dumps({
                'user': 2
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            '/team/2/invite',
            json.dumps({
                'user': 3
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            '/team/1/invite',
            json.dumps({
                'user': 3
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/team/1/invite',
            json.dumps({
                'user': 3
            }),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)


    def test_requests(self):
        response = self.client.post(
            '/team/1/request',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.client.login(username='test_a', password='hunter2'))
        response = self.client.post(
            '/team/1/request',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.client.login(username='test_c', password='hunter2'))
        response = self.client.post(
            '/team/1/request',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/team/1/request',
            json.dumps({}),
            'application/json',
            HTTP_HOST='www.testserver',
        )
        self.assertEqual(response.status_code, 400)
