from flask.json import dumps as json_dumps
from app import app
client = app.app.test_client()

class dbImport():
    """Dummy class to import data without authorization"""
    def setUp(self):
        r = self.plain_post('/v1/users/login/password', {"email": "hakan@debian.org", "password": "7tsLKBZo"})
        assert r.status_code == 200
        self.auth = r.json['token']

    def plain_post(self, path, body, auth=None, json=True):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        if json:
            return client.post(path, content_type='application/json', data=json_dumps(body), headers=headers)
        else:
            return client.post(path, data=body, headers=headers)

    def post(self, path, body, json=True):
        #assert self.plain_post(path, body, json=json).status_code == 401
        return self.plain_post(path, body, self.auth, json=json)

    def plain_get(self, path, auth=None):
        headers = {'Authorization': 'Bearer ' + auth} if auth else {}
        return client.get(path, headers=headers)

    def get(self, path):
        #assert self.plain_get(path).status_code == 401
        return self.plain_get(path, self.auth)

    def create_record(self, data):
        r = self.post('/v1/records', data)
        assert r.status_code == 200
        return r.json['id']
        #record_v1 = r.json
        #return record_v1

    def save_image(self, imageData):
        r = self.post('/v1/images', imageData, json=False)
        assert r.status_code == 200
        return r.json['id']
