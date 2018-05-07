from flask.json import dumps as json_dumps
import requests

class dbImport:
    """database API routines for importing data into database"""
    def __init__(self, serverUrl='http://0.0.0.0:8000', prefix='v1', auth=None):
        if not auth: raise Exception("No user data provided")
        path = "%s/%s/users/login/password" % (serverUrl, prefix)
        self.url = "%s/%s" % (serverUrl, prefix)
        #r = requests.post(path, data = json_dumps(auth),
        #                  headers = {"Content-Type": "application/json"})
        r = requests.post(path, json = auth)
        assert r.status_code == 200
        self.auth = r.json()['token']
        self.authHeader = {"Authorization": "Bearer " + self.auth}

    def create_record(self, data):
        path = "%s/records" % (self.url)
        r = requests.post(path, json = data, headers=self.authHeader)
        assert r.status_code == 200
        return r.json()['id']

    def save_image(self, imageData):
        path = "%s/images" % (self.url)
        r = requests.post(path, data = {"image": imageData}, headers=self.authHeader)
        #print(r.text)
        assert r.status_code == 200
        return r.json()['id']

    def get_records(self):
        path = "%s/records" % (self.url)
        r = requests.get(path, headers=self.authHeader)
        assert r.status_code == 200
        return r
    def get_record(self, id):
        path = "%s/records/%s" % (self.url, id)
        r = requests.get(path, headers=self.authHeader)
        assert r.status_code == 200
        return r.json()

