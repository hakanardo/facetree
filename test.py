import base64
import unittest
from threading import Thread
from uuid import uuid4

from PIL import Image
from io import BytesIO

from werkzeug.security import generate_password_hash

import utils
from flask.json import dumps as json_dumps
import os
from unittest.mock import patch
from flask.wrappers import Response

# Must be done before app is imported
os.system("mkdir db")
os.system("rm -r db/*")
os.system("cp -r test_db/images db")

from app import app, users
email = "hakan@debian.org"
users[email] = {'email': email, 'individual': 'xxx', 'password': generate_password_hash("7tsLKBZo")}
client = app.app.test_client()

class Base(unittest.TestCase):
    def plain_post(self, path, body, auth=None, json=True):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        if json:
            return client.post(path, content_type='application/json', data=json_dumps(body), headers=headers)
        else:
            return client.post(path, data=body, headers=headers)

    def plain_put(self, path, body, auth=None, json=True):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        if json:
            return client.put(path, content_type='application/json', data=json_dumps(body), headers=headers)
        else:
            return client.put(path, data=body, headers=headers)

    def plain_get(self, path, auth=None):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        return client.get(path, headers=headers)

    def plain_delete(self, path, auth=None):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        return client.delete(path, headers=headers)

    def post(self, path, body, json=True):
        assert self.plain_post(path, body, json=json).status_code == 401
        return self.plain_post(path, body, self.auth, json=json)

    def put(self, path, body, json=True):
        assert self.plain_put(path, body, json=json).status_code == 401
        return self.plain_put(path, body, self.auth, json=json)

    def get(self, path):
        assert self.plain_get(path).status_code == 401
        return self.plain_get(path, self.auth)

    def delete(self, path):
        assert self.plain_delete(path).status_code == 401
        return self.plain_delete(path, self.auth)


class TestAPI(Base):
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

    def test_create_and_update_record(self):
        # Create ver1
        r = self.post('/v1/records', {'type': 'Individual', 'name': 'Håkan Ardö'})
        assert r.status_code == 200
        record_v1 = r.json
        assert record_v1['name'] == 'Håkan Ardö'

        # Check ver1
        r = self.get('/v1/records/%s/%s' % (record_v1['id'], record_v1['version']))
        assert r.status_code == 200
        assert r.json == record_v1
        r = self.get('/v1/records/%s' % (record_v1['id']))
        assert r.status_code == 200
        assert r.json == record_v1

        # Create ver2
        record = dict(record_v1)
        record['name'] = 'Håkan Tester Ardö'
        r = self.post('/v1/records', record)
        assert r.status_code == 200
        record_v2 = r.json
        assert record_v2['name'] == 'Håkan Tester Ardö'
        assert record_v2['id'] == record_v1['id']
        assert record_v2['version'] != record_v1['version']
        assert record_v2['prev_version'] == record_v1['version']

        # Check ver1 and ver2
        r = self.get('/v1/records/%s/%s' % (record_v1['id'], record_v1['version']))
        assert r.status_code == 200
        assert r.json == record_v1
        r = self.get('/v1/records/%s/%s' % (record_v2['id'], record_v2['version']))
        assert r.status_code == 200
        assert r.json == record_v2
        r = self.get('/v1/records/%s' % (record_v1['id']))
        assert r.status_code == 200
        assert r.json == record_v2

        # Add another record and list records
        r = self.post('/v1/records', {'type': 'Individual', 'name': 'Björn Ardö'})
        assert r.status_code == 200
        record2 = r.json
        r = self.get('/v1/records')
        records = r.json
        assert record_v2 in records
        assert record2 in records
        assert record_v1 not in records

        # Delete original record
        r = self.delete('v1/records/%s' % record_v1['id'])
        r = self.get('/v1/records')
        records = r.json
        assert record_v2 not in records
        assert record2 in records
        assert record_v1 not in records

    def test_history(self):
        # Create some records
        r = self.post('/v1/records', {'type': 'Individual', 'name': 'Kajsa'})
        assert r.status_code == 200
        record = r.json
        assert self.post('/v1/records', {'type': 'Individual', 'name': 'Kalle'}).status_code == 200
        assert self.post('/v1/records', {'type': 'Individual', 'name': 'Olle'}).status_code == 200
        assert self.post('/v1/records', {'type': 'Individual', 'name': 'Sven'}).status_code == 200
        assert self.post('/v1/records', {'type': 'Individual', 'name': 'Nils'}).status_code == 200
        record['name'] = 'Kajsa Ver2'
        assert self.post('/v1/records', record).status_code == 200

        # Check history
        r = self.get('/v1/history/NOW/2')
        assert r.status_code == 200
        records = r.json['records']
        assert [r['name'] for r in records] == ['Kajsa Ver2', 'Nils']
        r = self.get('/v1/history/%s/4' % r.json['before'])
        assert r.status_code == 200
        records2 = r.json['records']
        assert [r['name'] for r in records2] == ['Sven', 'Olle', 'Kalle', 'Kajsa']
        assert records[0]['id'] == records2[3]['id']

    def test_updates(self):
        # Start longpoll and add som data
        poll = LongPoll(self, '/v1/updates/NOW')
        poll.start()
        r = self.post('/v1/records', {'type': 'Individual', 'name': 'Kalle'})
        assert r.status_code == 200
        poll.join()
        assert poll.result.status_code == 200
        assert poll.result.json['records'][0] == r.json

        # Add more data
        r = self.post('/v1/records', {'type': 'Individual', 'name': 'Olle'})
        r = self.post('/v1/records', {'type': 'Individual', 'name': 'Nils'})

        # Poll again
        r = self.get('/v1/updates/%s' % poll.result.json['since'])
        assert r.status_code == 200
        records = r.json['records']
        assert [r['name'] for r in records] == ['Olle', 'Nils']

    def test_get_image(self):
        r = self.get("/v1/images/82fa2364-ed5f-4c9f-99d2-497f347d2f9b/original.jpg")
        assert r.status_code == 200
        assert len(r.data) == 166640

    def test_post_image(self):
        jpeg_data = open("test.jpg", "rb").read()
        r = self.post("/v1/images", jpeg_data, json=False)
        assert r.status_code == 200
        id = r.json['id']
        r = self.get("/v1/images/%s/original.jpg" % id)
        assert r.status_code == 200
        assert r.data == jpeg_data
        r = self.get("/v1/images/%s/original.jpg/base64" % id)
        assert r.status_code == 200
        assert base64.decodebytes(r.data) == jpeg_data

    def test_post_bad_image(self):
        r = self.post("/v1/images", b'', json=False)
        assert r.status_code == 400
        r = self.post("/v1/images", b'Bad data', json=False)
        assert r.status_code == 400


    def test_rescale_image(self):
        r = self.get("/v1/images/82fa2364-ed5f-4c9f-99d2-497f347d2f9b/thumb.jpg")
        assert r.status_code == 200
        img = Image.open(BytesIO(r.data))
        assert img.size == (256, 336)

    def test_crop_image(self):
        r = self.post("/v1/images/82fa2364-ed5f-4c9f-99d2-497f347d2f9b/crop",
                      {"left": 10, "upper": 10, "right": 100, "lower": 100})
        assert r.status_code == 200
        r = self.get("/v1/images/%s/original.jpg" % (r.json['id']))
        assert r.status_code == 200
        img = Image.open(BytesIO(r.data))
        assert img.size == (90, 90)

class LongPoll(Thread):
    def __init__(self, test, path):
        Thread.__init__(self)
        self.test = test
        self.path = path

    def run(self):
        self.result = self.test.get(self.path)

if __name__ == '__main__':
    unittest.main()