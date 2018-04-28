import unittest

import utils
from flask import json
import os
from unittest.mock import patch

os.system("cp test_db/* db") # Must be done before app is imported
from app import app
client = app.app.test_client()

class TestAPI(unittest.TestCase):

    def plain_post(self, path, body, auth=None):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        return client.post(path, content_type='application/json', data=json.dumps(body), headers=headers)

    def plain_put(self, path, body, auth=None):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        return client.put(path, content_type='application/json', data=json.dumps(body), headers=headers)

    def plain_get(self, path, auth=None):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        return client.get(path, headers=headers)

    def post(self, path, body):
        assert self.plain_post(path, body).status_code == 401
        return self.plain_post(path, body, self.auth)

    def put(self, path, body):
        assert self.plain_put(path, body).status_code == 401
        return self.plain_put(path, body, self.auth)

    def get(self, path, body):
        assert self.plain_get(path, body).status_code == 401
        return self.plain_get(path, body, self.auth)

    def setUp(self):
        r = self.plain_post('/v1/users/login/password', {"email": "hakan@debian.org", "password": "7tsLKBZo"})
        assert r.status_code == 200
        self.auth = r.json['token']

    def test_login(self):
        r = self.plain_post('/v1/users/login/password', {"email": "hakan@debian.org", "password": "badpass"})
        assert r.status_code == 401
        r = self.plain_post('/v1/users/login/password', {"email": "hakan@debian.org", "password": "7tsLKBZo"})
        assert r.status_code == 200
        auth = r.json['token']
        r = self.plain_get('v1/records')
        assert r.status_code == 401
        r = self.plain_get('v1/records', auth)
        assert r.status_code == 200

    def test_invite_and_change_password(self):
        # Invite
        with patch('app.send_mail') as send_mail:
            r = self.post('/v1/users/invite', { "email": "user@example.com", "individual": "xxx"  })
            assert r.status_code == 200
        assert send_mail.call_count == 1
        assert send_mail.call_args[0][0] == "user@example.com"
        password = send_mail.call_args[0][2].split('lösenord ')[1].split('\n')[0]
        print(password)

        # Try to change someone elses password
        r = self.post('/v1/users/password', {"old": "badpass", "new": "pass"})
        assert r.status_code == 401
        r = self.plain_post('/v1/users/login/password', {"email": "user@example.com", "password": "pass"})
        assert r.status_code == 401
        r = self.post('/v1/users/password', {"old": password, "new": "pass"})
        assert r.status_code == 401
        r = self.plain_post('/v1/users/login/password', {"email": "user@example.com", "password": "pass"})
        assert r.status_code == 401

        # Login
        r = self.plain_post('/v1/users/login/password', {"email": "user@example.com", "password": password})
        assert r.status_code == 200
        auth = r.json['token']

        # Change password
        r = self.plain_post('/v1/users/password', {"old": "badpass", "new": "pass"}, auth)
        assert r.status_code == 401
        r = self.plain_post('/v1/users/login/password', {"email": "user@example.com", "password": "pass"})
        assert r.status_code == 401
        r = self.plain_post('/v1/users/password', {"old": password, "new": "pass"}, auth)
        assert r.status_code == 200
        r = self.plain_post('/v1/users/login/password', {"email": "user@example.com", "password": "pass"})
        assert r.status_code == 200

